# ABOUTME: Integration tests for Makefile build system — venv management, linking, and clean targets.
# ABOUTME: Verifies AC2.1–AC2.7: install, stale venv detection, symlinks, clean, PATH warning.
import os
import subprocess
import stat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV_DIR = os.path.join(REPO_ROOT, '.venv')
LINK_DIR = os.path.join(os.path.expanduser('~'), '.local', 'bin')
MAKE = ['make', '-C', REPO_ROOT]
ENV = {**os.environ, 'PATH': f'/usr/bin:/bin:/usr/sbin:/sbin:{os.path.expanduser("~/bin")}:{LINK_DIR}:/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:{os.environ.get("PATH", "")}'}


def test_makefile_install_clean_checkout_succeeds():
    """AC2.1: Given a clean checkout with no .venv/, make install completes successfully."""
    # Arrange: ensure clean state
    subprocess.run(MAKE + ['clean'], env=ENV, capture_output=True)
    assert not os.path.isdir(VENV_DIR)

    # Act
    result = subprocess.run(MAKE + ['install'], env=ENV, capture_output=True, text=True, timeout=600)

    # Assert
    assert result.returncode == 0, f'make install failed:\nstdout: {result.stdout}\nstderr: {result.stderr}'


def test_makefile_install_stale_venv_rebuilds():
    """AC2.2: Given a stale .venv with broken interpreter symlinks, make install detects and rebuilds it."""
    # Arrange: create a stale venv with broken symlinks
    subprocess.run(MAKE + ['clean'], env=ENV, capture_output=True)
    os.makedirs(os.path.join(VENV_DIR, 'bin'), exist_ok=True)
    stale_python = os.path.join(VENV_DIR, 'bin', 'python')
    os.symlink('/nonexistent/python3.12', stale_python)

    # Act
    result = subprocess.run(MAKE + ['install'], env=ENV, capture_output=True, text=True, timeout=600)

    # Assert
    assert result.returncode == 0, f'make install failed with stale venv:\nstdout: {result.stdout}\nstderr: {result.stderr}'
    assert 'Stale venv detected' in result.stdout or 'Stale venv detected' in result.stderr


def test_makefile_upscale_wrapper_exists_after_install():
    """AC2.3: After make install, upscale is an executable wrapper in ~/.local/bin/."""
    upscale_path = os.path.join(LINK_DIR, 'upscale')
    assert os.path.isfile(upscale_path), f'{upscale_path} does not exist'
    assert os.access(upscale_path, os.X_OK), f'{upscale_path} is not executable'


def test_makefile_upscale_video_wrapper_exists_after_install():
    """AC2.4: After make install, upscale-video is an executable wrapper in ~/.local/bin/."""
    upscale_video_path = os.path.join(LINK_DIR, 'upscale-video')
    assert os.path.isfile(upscale_video_path), f'{upscale_video_path} does not exist'
    assert os.access(upscale_video_path, os.X_OK), f'{upscale_video_path} is not executable'


def test_makefile_clean_removes_venv_and_wrappers():
    """AC2.5: The clean target removes the venv directory and both wrapper scripts."""
    # Act
    result = subprocess.run(MAKE + ['clean'], env=ENV, capture_output=True, text=True)

    # Assert
    assert result.returncode == 0, f'make clean failed:\nstdout: {result.stdout}\nstderr: {result.stderr}'
    assert not os.path.isdir(VENV_DIR), '.venv still exists after make clean'
    assert not os.path.isfile(os.path.join(LINK_DIR, 'upscale')), 'upscale wrapper still exists after make clean'
    assert not os.path.isfile(os.path.join(LINK_DIR, 'upscale-video')), 'upscale-video wrapper still exists after make clean'


def test_makefile_no_homebrew_bin_references():
    """AC2.6: Makefile and README contain no references to /opt/homebrew/bin."""
    for filename in ['Makefile', 'README.md']:
        filepath = os.path.join(REPO_ROOT, filename)
        if os.path.isfile(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
            # PYTHON_BIN referencing /opt/homebrew/opt/python@3.12 is fine — that's the interpreter, not LINK_DIR
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if '/opt/homebrew/bin' in line:
                    assert False, f'{filename}:{i+1} contains /opt/homebrew/bin: {line.strip()}'


def test_makefile_link_warns_if_not_in_path():
    """AC2.7: Given ~/.local/bin is absent from $PATH, make link prints a PATH warning."""
    # Arrange: PATH without ~/.local/bin
    stripped_path = ':'.join(
        p for p in ENV['PATH'].split(':')
        if os.path.normpath(p) != os.path.normpath(LINK_DIR)
    )
    env_no_link = {**ENV, 'PATH': stripped_path}

    # Ensure install is done first
    subprocess.run(MAKE + ['install'], env=ENV, capture_output=True, timeout=600)

    # Act
    result = subprocess.run(MAKE + ['link'], env=env_no_link, capture_output=True, text=True)

    # Assert
    combined = result.stdout + result.stderr
    assert 'WARNING' in combined and 'PATH' in combined, f'No PATH warning in output:\n{combined}'
