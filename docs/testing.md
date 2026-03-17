<!-- Version: 1.0 | Last updated: 2026-03-17 -->

# Real-ESRGAN-pro: Testing

## Overview

Tests are organized by scope. The regression pack (`make test`) runs quickly without model weights. Full end-to-end tests (`make test-all`) require downloaded weights and take longer.

## Test Suite

| File | Type | What it covers | Requires weights? |
|------|------|---------------|-------------------|
| `tests/test_paths.py` | Unit | Weight dir resolution, env override, directory creation | No |
| `tests/test_cli.py` | Integration | `upscale --help`, `upscale --version`, `upscale-video --help/--version` | No |
| `tests/test_makefile.py` | Integration | Venv creation, stale detection, wrapper scripts, clean, PATH warning | No |
| `tests/test_precommit.py` | Unit | Pre-commit config uses Ruff, no legacy tools, scoping | No |
| `tests/test_setup.py` | Unit | Python classifiers, python_requires, licence | No |
| `tests/test_release.py` | One-off | Release.sh --dry-run, SKIP_TESTS support | No |

### Not in the Regression Pack

- `tests/test_release.py` — Verifies release.sh behaviour. Not included in `make test` because the release script is a destructive operation. Run manually when modifying release.sh.
- `tests/test_precommit.py` and `tests/test_setup.py` — Metadata verification tests. Included in `make test` to catch configuration drift.

## Running Tests

```bash
# Regression pack (fast, no weights needed)
make test

# All tests including model inference (slow, needs weights)
make test-all

# Specific test file
source .venv/bin/activate
python -m pytest tests/test_paths.py -v -o "addopts="

# Release verification (one-off)
python -m pytest tests/test_release.py -v -o "addopts="
```

## Test Strategy

We follow TDD per our [testing standards](../../.claude/docs/TESTING.md):

1. Write failing tests for the feature/fix
2. Implement minimal code to pass
3. Run issue tests
4. Regression pack at batch boundaries

### What Gets Tested

- **CLI entry points** — `--help` and `--version` exit 0 (verifies imports work without weights)
- **Path resolution** — Default path, env override, directory creation
- **Makefile targets** — Full install/clean/link cycle, stale venv detection
- **Configuration** — Pre-commit hooks, setup.py metadata

### What Does Not Get Tested in Regression

- **Model inference** — Requires ~500MB of weights. Covered by `make test-all`.
- **Release workflow** — Destructive (creates tags, pushes). Tested via `--dry-run`.
- **Homebrew formula** — Tested manually after `make release`.

## Adding Tests

New tests should:

1. Follow the `test_<unit>_<scenario>_<expected_result>` naming convention
2. Use Arrange-Act-Assert structure
3. Be added to `make test` unless they require model weights or are destructive
4. Include an ABOUTME comment explaining what the file covers
