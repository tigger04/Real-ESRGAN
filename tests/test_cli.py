# ABOUTME: Tests for CLI entry points — verifies --help and --version work for both commands.
# ABOUTME: Uses subprocess to test the actual entry points as a user would invoke them.
import subprocess
import sys


def test_upscale_help_returns_zero():
    """upscale --help exits 0 and prints usage info."""
    # Act
    result = subprocess.run(
        [sys.executable, '-m', 'realesrgan.cli_image', '--help'],
        capture_output=True, text=True)

    # Assert
    assert result.returncode == 0
    assert 'usage' in result.stdout.lower() or 'Usage' in result.stdout


def test_upscale_version_returns_zero():
    """upscale --version exits 0 and prints a version string."""
    # Act
    result = subprocess.run(
        [sys.executable, '-m', 'realesrgan.cli_image', '--version'],
        capture_output=True, text=True)

    # Assert
    assert result.returncode == 0
    assert 'upscale' in result.stdout.lower()


def test_upscale_video_help_returns_zero():
    """upscale-video --help exits 0 and prints usage info."""
    # Act
    result = subprocess.run(
        [sys.executable, '-m', 'realesrgan.cli_video', '--help'],
        capture_output=True, text=True)

    # Assert
    assert result.returncode == 0
    assert 'usage' in result.stdout.lower() or 'Usage' in result.stdout


def test_upscale_video_version_returns_zero():
    """upscale-video --version exits 0 and prints a version string."""
    # Act
    result = subprocess.run(
        [sys.executable, '-m', 'realesrgan.cli_video', '--version'],
        capture_output=True, text=True)

    # Assert
    assert result.returncode == 0
    assert 'upscale-video' in result.stdout.lower()
