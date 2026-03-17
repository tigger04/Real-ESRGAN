# ABOUTME: Tests for pre-commit configuration — verifies Ruff replaces legacy tools.
# ABOUTME: Verifies AC4.1–AC4.5: Ruff hooks, scoping, config, linting, retained hooks.
import os
import subprocess

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV_BIN = os.path.join(REPO_ROOT, '.venv', 'bin')
PRECOMMIT_CONFIG = os.path.join(REPO_ROOT, '.pre-commit-config.yaml')
PYPROJECT_TOML = os.path.join(REPO_ROOT, 'pyproject.toml')


def test_precommit_no_legacy_tools():
    """AC4.1: No legacy Python tools (flake8, yapf, isort, seed-isort) in pre-commit config."""
    with open(PRECOMMIT_CONFIG) as f:
        content = f.read()
    for tool in ['flake8', 'yapf', 'isort', 'seed-isort']:
        assert tool not in content, f'Legacy tool "{tool}" still in .pre-commit-config.yaml'


def test_precommit_has_ruff():
    """AC4.1: Ruff is configured in pre-commit config."""
    with open(PRECOMMIT_CONFIG) as f:
        content = f.read()
    assert 'ruff' in content, 'Ruff not found in .pre-commit-config.yaml'


def test_precommit_ruff_scoped_to_project_files():
    """AC4.2: Ruff hooks are scoped to project files only."""
    with open(PRECOMMIT_CONFIG) as f:
        content = f.read()
    assert 'files' in content, 'No files scope found for Ruff hooks'
    # Should reference our modules and tests
    assert 'tests/' in content, 'Ruff scope does not include tests/'


def test_pyproject_toml_has_ruff_config():
    """AC4.3: Ruff configuration defined in pyproject.toml."""
    assert os.path.isfile(PYPROJECT_TOML), 'pyproject.toml does not exist'
    with open(PYPROJECT_TOML) as f:
        content = f.read()
    assert '[tool.ruff]' in content, 'No [tool.ruff] section in pyproject.toml'


def test_ruff_passes_on_project_files():
    """AC4.4: Our project files pass Ruff linting."""
    env = {
        **os.environ,
        'PATH': f'{VENV_BIN}:/usr/bin:/bin:/usr/sbin:/sbin:{os.path.expanduser("~/bin")}:'
                f'{os.path.expanduser("~/.local/bin")}:/opt/homebrew/bin:'
                f'/opt/homebrew/sbin:/usr/local/bin:{os.environ.get("PATH", "")}',
    }
    project_files = [
        'realesrgan/cli_image.py',
        'realesrgan/cli_video.py',
        'realesrgan/paths.py',
        'realesrgan/_compat.py',
    ]
    existing = [f for f in project_files if os.path.isfile(os.path.join(REPO_ROOT, f))]
    # Also check tests/
    existing.append('tests/')
    result = subprocess.run(
        ['ruff', 'check'] + existing,
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f'Ruff lint failures:\n{result.stdout}\n{result.stderr}'


def test_precommit_retains_non_python_hooks():
    """AC4.5: Non-Python hooks (codespell, trailing-whitespace, check-yaml) retained."""
    with open(PRECOMMIT_CONFIG) as f:
        content = f.read()
    for hook in ['codespell', 'trailing-whitespace', 'check-yaml']:
        assert hook in content, f'Hook "{hook}" missing from .pre-commit-config.yaml'
