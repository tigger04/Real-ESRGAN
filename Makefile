# ABOUTME: Makefile for Real-ESRGAN-pro — manages venv, deps, CLI install, and releases.
# ABOUTME: Wraps the upstream Real-ESRGAN install in a reproducible local workflow.

SHELL := /bin/bash
.DEFAULT_GOAL := help

PYTHON_BIN := /opt/homebrew/opt/python@3.12/bin/python3.12
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
ACTIVATE := source $(VENV)/bin/activate
LINK_DIR := $(HOME)/.local/bin
RELEASE_VERSION ?=
SKIP_TESTS ?=

.PHONY: help install clean update sync test link unlink release ensure-venv

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

ensure-venv:
	@if [ -d "$(VENV)" ] && ! "$(VENV)/bin/python" --version >/dev/null 2>&1; then \
		echo "Stale venv detected — rebuilding..."; \
		rm -rf "$(VENV)"; \
	fi
	@if [ ! -d "$(VENV)" ]; then \
		$(PYTHON_BIN) -m venv "$(VENV)"; \
	fi

install: ensure-venv ## Create venv, install deps, register CLI entry points, and link commands
	$(ACTIVATE) && $(PIP) install --upgrade pip
	$(ACTIVATE) && $(PIP) install -r requirements.txt
	$(ACTIVATE) && $(PIP) install -e .
	@$(MAKE) link
	@echo ""
	@echo "Done. Commands available: upscale, upscale-video"

update: ## Fetch and merge upstream changes
	git fetch upstream
	git merge upstream/master
	@echo "Upstream merged. Run 'make install' if dependencies changed."

clean: unlink ## Remove the virtual environment and wrapper scripts
	@if [ -d "$(VENV)" ]; then \
		if command -v trash >/dev/null 2>&1; then \
			trash "$(VENV)"; \
		else \
			rm -rf "$(VENV)"; \
		fi; \
	fi
	@echo "Cleaned. Run 'make install' to rebuild."

test: ensure-venv ## Run tests
	$(ACTIVATE) && $(PYTHON) -m pytest tests/test_paths.py tests/test_cli.py tests/test_makefile.py tests/test_precommit.py tests/test_setup.py tests/test_compat_import_order.py -v -o "addopts="

test-all: ensure-venv ## Run all tests (requires model weights)
	$(ACTIVATE) && $(PYTHON) -m pytest tests/ -v

link: ensure-venv ## Create wrapper scripts in ~/.local/bin for upscale and upscale-video
	@if [ ! -f "$(VENV)/bin/upscale" ]; then \
		echo "Error: run 'make install' first"; exit 1; \
	fi
	@mkdir -p "$(LINK_DIR)"
	@echo '#!/bin/bash' > "$(LINK_DIR)/upscale"
	@echo 'exec "$(CURDIR)/$(VENV)/bin/upscale" "$$@"' >> "$(LINK_DIR)/upscale"
	@chmod +x "$(LINK_DIR)/upscale"
	@echo '#!/bin/bash' > "$(LINK_DIR)/upscale-video"
	@echo 'exec "$(CURDIR)/$(VENV)/bin/upscale-video" "$$@"' >> "$(LINK_DIR)/upscale-video"
	@chmod +x "$(LINK_DIR)/upscale-video"
	@echo "Linked: $(LINK_DIR)/upscale, $(LINK_DIR)/upscale-video"
	@case ":$$PATH:" in \
		*":$(LINK_DIR):"*) ;; \
		*) echo "WARNING: $(LINK_DIR) is not in your PATH. Add it to your shell profile." ;; \
	esac

unlink: ## Remove wrapper scripts from ~/.local/bin
	@if [ -f "$(LINK_DIR)/upscale" ]; then rm -f "$(LINK_DIR)/upscale"; fi
	@if [ -f "$(LINK_DIR)/upscale-video" ]; then rm -f "$(LINK_DIR)/upscale-video"; fi
	@echo "Unlinked."

sync: ## Stage all, commit, pull (merge), push
	@if git diff --quiet && git diff --cached --quiet && [ -z "$$(git ls-files --others --exclude-standard)" ]; then \
		echo "Nothing to commit."; \
	else \
		git add --all && \
		git commit -m "sync: $$(date +%Y-%m-%d)" && \
		echo "Committed."; \
	fi
	@if [ -f .gitmodules ]; then \
		git submodule update --init --recursive; \
	fi
	git pull --rebase=false
	git push

release: ## Tag a release and update Homebrew formula (usage: make release [VERSION=x.y.z])
	@SKIP_TESTS=$(SKIP_TESTS) ./scripts/release.sh $(RELEASE_VERSION)
