# ABOUTME: Tests for _compat import ordering — verifies the torchvision compatibility
# ABOUTME: patch loads before basicsr in both CLI entry points (issues #7, #8).
import os
import re
import subprocess
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV_BIN = os.path.join(REPO_ROOT, '.venv', 'bin')


@pytest.mark.regression(test_id="RT-001")
def test_cli_image_entry_point_imports_successfully():
    """AC8.1: upscale entry point imports all dependencies and reaches argument processing."""
    # Arrange — invoke via the actual entry-point script, not python -m
    upscale = os.path.join(VENV_BIN, 'upscale')
    assert os.path.isfile(upscale), f'Entry point not found: {upscale} — run make install'
    # Act
    result = subprocess.run(
        [upscale, '-i', '/nonexistent.png'],
        capture_output=True, text=True, timeout=60,
    )
    # Assert — may fail for other reasons, but imports must succeed
    assert 'ModuleNotFoundError' not in result.stderr, (
        f'Import failure in upscale entry point:\n{result.stderr}'
    )
    assert 'RecursionError' not in result.stderr, (
        f'Recursion in upscale entry point:\n{result.stderr}'
    )


@pytest.mark.regression(test_id="RT-002")
def test_cli_video_entry_point_imports_successfully():
    """AC8.1: upscale-video entry point imports all dependencies and reaches argument processing."""
    # Arrange
    upscale_video = os.path.join(VENV_BIN, 'upscale-video')
    assert os.path.isfile(upscale_video), f'Entry point not found: {upscale_video} — run make install'
    # Act
    result = subprocess.run(
        [upscale_video, '-i', '/nonexistent.mp4'],
        capture_output=True, text=True, timeout=60,
    )
    # Assert
    assert 'ModuleNotFoundError' not in result.stderr, (
        f'Import failure in upscale-video entry point:\n{result.stderr}'
    )
    assert 'RecursionError' not in result.stderr, (
        f'Recursion in upscale-video entry point:\n{result.stderr}'
    )


@pytest.mark.regression(test_id="RT-005")
def test_package_import_of_compat_resolves_cleanly():
    """AC8.2: from realesrgan import _compat completes without recursion."""
    # Arrange/Act — fresh interpreter, import through the package interface
    result = subprocess.run(
        [sys.executable, '-c', 'from realesrgan import _compat'],
        capture_output=True, text=True, timeout=30,
        cwd=REPO_ROOT,
    )
    # Assert
    assert result.returncode == 0, (
        f'Package import of _compat failed (exit {result.returncode}):\n{result.stderr}'
    )


@pytest.mark.regression(test_id="RT-003")
def test_cli_image_compat_import_precedes_basicsr():
    """AC7.3: In cli_image.py, _compat is imported before any basicsr import."""
    # Arrange
    cli_image_path = os.path.join(REPO_ROOT, 'realesrgan', 'cli_image.py')
    with open(cli_image_path) as f:
        lines = f.readlines()

    # Act — find first _compat import and first basicsr import
    compat_line = None
    basicsr_line = None
    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        if compat_line is None and re.search(r'import\s+_compat|from\s+realesrgan\s+import\s+_compat', stripped):
            compat_line = i
        if basicsr_line is None and re.search(r'from\s+basicsr', stripped):
            basicsr_line = i

    # Assert
    assert compat_line is not None, '_compat import not found in cli_image.py'
    assert basicsr_line is not None, 'basicsr import not found in cli_image.py'
    assert compat_line < basicsr_line, (
        f'_compat imported on line {compat_line} but basicsr imported earlier on line {basicsr_line}'
    )


@pytest.mark.regression(test_id="RT-004")
def test_cli_video_compat_import_precedes_basicsr():
    """AC7.4: In cli_video.py, _compat is imported before any basicsr import."""
    # Arrange
    cli_video_path = os.path.join(REPO_ROOT, 'realesrgan', 'cli_video.py')
    with open(cli_video_path) as f:
        lines = f.readlines()

    # Act — find first _compat import and first basicsr import
    compat_line = None
    basicsr_line = None
    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        if compat_line is None and re.search(r'import\s+_compat|from\s+realesrgan\s+import\s+_compat', stripped):
            compat_line = i
        if basicsr_line is None and re.search(r'from\s+basicsr', stripped):
            basicsr_line = i

    # Assert
    assert compat_line is not None, '_compat import not found in cli_video.py'
    assert basicsr_line is not None, 'basicsr import not found in cli_video.py'
    assert compat_line < basicsr_line, (
        f'_compat imported on line {compat_line} but basicsr imported earlier on line {basicsr_line}'
    )
