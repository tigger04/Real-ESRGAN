# ABOUTME: Makefile for Real-ESRGAN-pro — manages venv, deps, CLI install, and releases.
# ABOUTME: Wraps the upstream Real-ESRGAN install in a reproducible local workflow.

SHELL := /bin/bash
.DEFAULT_GOAL := help

PYTHON_BIN := /opt/homebrew/opt/python@3.12/bin/python3.12
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
ACTIVATE := source $(VENV)/bin/activate
LINK_DIR := /opt/homebrew/bin
VERSION := $(shell cat VERSION)

.PHONY: help install clean update sync test link unlink release

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

$(VENV):
	$(PYTHON_BIN) -m venv $(VENV)

install: $(VENV) ## Create venv, install deps, and register CLI entry points
	$(ACTIVATE) && $(PIP) install --upgrade pip
	$(ACTIVATE) && $(PIP) install -r requirements.txt
	$(ACTIVATE) && $(PIP) install -e .
	@echo ""
	@echo "Done. Activate with: source $(VENV)/bin/activate"
	@echo "Commands available inside venv: upscale, upscale-video"

update: ## Fetch and merge upstream changes
	git fetch upstream
	git merge upstream/master
	@echo "Upstream merged. Run 'make install' if dependencies changed."

clean: ## Remove the virtual environment and wrapper scripts
	if [ -d "$(VENV)" ]; then trash $(VENV) 2>/dev/null || rm -rf $(VENV); fi
	@echo "Cleaned. Run 'make install' to rebuild."

test: $(VENV) ## Run tests
	$(ACTIVATE) && $(PYTHON) -m pytest tests/test_paths.py tests/test_cli.py -v -o "addopts="

test-all: $(VENV) ## Run all tests (requires model weights)
	$(ACTIVATE) && $(PYTHON) -m pytest tests/ -v

link: $(VENV) ## Create system-wide symlinks for upscale and upscale-video
	@if [ ! -f "$(VENV)/bin/upscale" ]; then \
		echo "Error: run 'make install' first"; exit 1; \
	fi
	@echo '#!/bin/bash' > $(LINK_DIR)/upscale
	@echo 'exec "$(CURDIR)/$(VENV)/bin/upscale" "$$@"' >> $(LINK_DIR)/upscale
	@chmod +x $(LINK_DIR)/upscale
	@echo '#!/bin/bash' > $(LINK_DIR)/upscale-video
	@echo 'exec "$(CURDIR)/$(VENV)/bin/upscale-video" "$$@"' >> $(LINK_DIR)/upscale-video
	@chmod +x $(LINK_DIR)/upscale-video
	@echo "Linked: $(LINK_DIR)/upscale, $(LINK_DIR)/upscale-video"

unlink: ## Remove system-wide symlinks
	@rm -f $(LINK_DIR)/upscale $(LINK_DIR)/upscale-video
	@echo "Unlinked."

sync: ## Stage all, commit, pull (merge), push
	@if git diff --quiet && git diff --cached --quiet && [ -z "$$(git ls-files --others --exclude-standard)" ]; then \
		echo "Nothing to commit."; \
	else \
		git add --all && \
		git commit -m "sync: $$(date +%Y-%m-%d)" && \
		echo "Committed."; \
	fi
	git submodule update --init --recursive 2>/dev/null || true
	git pull --rebase=false
	git push

release: ## Tag a release and update Homebrew formula (usage: make release [VERSION=x.y.z])
	@./scripts/release.sh $(VERSION)
