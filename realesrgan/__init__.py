# ABOUTME: Package init for realesrgan — uses lazy loading for fast CLI startup.
# ABOUTME: Heavy submodules (archs, data, models, utils) loaded on first attribute access.
# flake8: noqa
from .version import *

_HEAVY_SUBMODULES = ('archs', 'data', 'models', 'utils')
_compat_loaded = False


def __getattr__(name):
    """Lazy-load heavy submodules on first attribute access."""
    global _compat_loaded
    import importlib

    if name == '_compat':
        _compat_loaded = True
        mod = importlib.import_module('._compat', __name__)
        globals()['_compat'] = mod
        return mod

    # Ensure compatibility patch is applied before any basicsr imports
    if not _compat_loaded:
        _compat_loaded = True
        importlib.import_module('._compat', __name__)

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
