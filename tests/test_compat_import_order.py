# ABOUTME: Tests for _compat import ordering — verifies the torchvision compatibility
# ABOUTME: patch loads before basicsr in both CLI entry points (issue #7).
import os
import re
import subprocess
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.regression(test_id="RT-001")
def test_cli_image_imports_without_module_not_found_error():
    """AC7.1: cli_image.main() loads imports without ModuleNotFoundError."""
    # Arrange — invoke upscale with a non-existent input to get past argparse
    # Act
    result = subprocess.run(
        [sys.executable, '-m', 'realesrgan.cli_image', '-i', '/nonexistent.png'],
        capture_output=True, text=True, timeout=60,
    )
    # Assert — may fail for other reasons, but must not have ModuleNotFoundError
    assert 'ModuleNotFoundError' not in result.stderr, (
        f'ModuleNotFoundError in cli_image imports:\n{result.stderr}'
    )


@pytest.mark.regression(test_id="RT-002")
def test_cli_video_imports_without_module_not_found_error():
    """AC7.2: cli_video.main() loads imports without ModuleNotFoundError."""
    # Arrange — invoke upscale-video with a non-existent input to get past argparse
    # Act
    result = subprocess.run(
        [sys.executable, '-m', 'realesrgan.cli_video', '-i', '/nonexistent.mp4'],
        capture_output=True, text=True, timeout=60,
    )
    # Assert
    assert 'ModuleNotFoundError' not in result.stderr, (
        f'ModuleNotFoundError in cli_video imports:\n{result.stderr}'
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
