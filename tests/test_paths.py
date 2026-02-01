# ABOUTME: Tests for realesrgan.paths — weight directory resolution and env override.
# ABOUTME: Verifies default cache dir, $REALESRGAN_WEIGHTS_DIR override, and directory creation.
import importlib.util
import os
import tempfile


def _import_paths():
    """Import realesrgan.paths directly to avoid triggering realesrgan/__init__.py import chain."""
    spec = importlib.util.spec_from_file_location(
        'realesrgan.paths',
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'realesrgan', 'paths.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


paths = _import_paths()
get_weights_dir = paths.get_weights_dir


def test_get_weights_dir_default_path():
    """get_weights_dir returns ~/.cache/realesrgan/weights/ when no env override."""
    # Arrange: ensure the env var is unset
    env_backup = os.environ.pop('REALESRGAN_WEIGHTS_DIR', None)
    try:
        # Act
        result = get_weights_dir()

        # Assert
        expected = os.path.join(os.path.expanduser('~'), '.cache', 'realesrgan', 'weights')
        assert result == expected
        assert os.path.isdir(result)
    finally:
        if env_backup is not None:
            os.environ['REALESRGAN_WEIGHTS_DIR'] = env_backup


def test_get_weights_dir_env_override():
    """get_weights_dir honours $REALESRGAN_WEIGHTS_DIR."""
    with tempfile.TemporaryDirectory() as tmpdir:
        custom_dir = os.path.join(tmpdir, 'custom_weights')
        # Arrange
        env_backup = os.environ.get('REALESRGAN_WEIGHTS_DIR')
        os.environ['REALESRGAN_WEIGHTS_DIR'] = custom_dir
        try:
            # Act
            result = get_weights_dir()

            # Assert
            assert result == custom_dir
            assert os.path.isdir(custom_dir)
        finally:
            if env_backup is not None:
                os.environ['REALESRGAN_WEIGHTS_DIR'] = env_backup
            else:
                os.environ.pop('REALESRGAN_WEIGHTS_DIR', None)


def test_get_weights_dir_creates_directory():
    """get_weights_dir creates the directory if it does not exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        new_dir = os.path.join(tmpdir, 'nested', 'path', 'weights')
        env_backup = os.environ.get('REALESRGAN_WEIGHTS_DIR')
        os.environ['REALESRGAN_WEIGHTS_DIR'] = new_dir
        try:
            # Act
            assert not os.path.exists(new_dir)
            result = get_weights_dir()

            # Assert
            assert result == new_dir
            assert os.path.isdir(new_dir)
        finally:
            if env_backup is not None:
                os.environ['REALESRGAN_WEIGHTS_DIR'] = env_backup
            else:
                os.environ.pop('REALESRGAN_WEIGHTS_DIR', None)
