# ABOUTME: Centralised weight-cache directory resolution for Real-ESRGAN models.
# ABOUTME: Returns ~/.cache/realesrgan/weights/ by default, overridable via $REALESRGAN_WEIGHTS_DIR.
import os


_DEFAULT_CACHE_DIR = os.path.join(os.path.expanduser('~'), '.cache', 'realesrgan', 'weights')


def get_weights_dir():
    """Return the directory where model weights are cached.

    Checks $REALESRGAN_WEIGHTS_DIR first, falls back to ~/.cache/realesrgan/weights/.
    Creates the directory if it does not exist.
    """
    weights_dir = os.environ.get('REALESRGAN_WEIGHTS_DIR', _DEFAULT_CACHE_DIR)
    os.makedirs(weights_dir, exist_ok=True)
    return weights_dir
