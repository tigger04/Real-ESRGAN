# ABOUTME: Package init for realesrgan — uses lazy loading for fast CLI startup.
# ABOUTME: Heavy submodules (archs, data, models, utils) loaded on first attribute access.
# flake8: noqa
from .version import *

_HEAVY_SUBMODULES = ('archs', 'data', 'models', 'utils')
_compat_loaded = False


def __getattr__(name):
    """Lazy-load heavy submodules on first attribute access."""
    global _compat_loaded
    if name == '_compat':
        from . import _compat
        _compat_loaded = True
        return _compat

    # Ensure compatibility patch is applied before any basicsr imports
    if not _compat_loaded:
        from . import _compat  # noqa: F401
        _compat_loaded = True

    import importlib
    for submod_name in _HEAVY_SUBMODULES:
        try:
            submod = importlib.import_module(f'.{submod_name}', __name__)
        except ImportError:
            continue
        if hasattr(submod, name):
            val = getattr(submod, name)
            globals()[name] = val
            return val

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
