# ABOUTME: Compatibility shim for basicsr + newer torchvision (0.18+).
# ABOUTME: Restores torchvision.transforms.functional_tensor removed in newer releases.
import importlib
import sys
import types


def patch_torchvision_functional_tensor():
    """Register a stub torchvision.transforms.functional_tensor module.

    basicsr 1.4.2 imports rgb_to_grayscale from torchvision.transforms.functional_tensor,
    which was removed in torchvision 0.18+. The function still exists in
    torchvision.transforms.functional, so we create a shim module that re-exports it.
    """
    module_name = 'torchvision.transforms.functional_tensor'
    if module_name in sys.modules:
        return

    try:
        importlib.import_module(module_name)
        return  # already loadable, nothing to do
    except ModuleNotFoundError:
        pass

    try:
        from torchvision.transforms.functional import rgb_to_grayscale
    except ImportError:
        return  # no torchvision at all — nothing we can do

    shim = types.ModuleType(module_name)
    shim.rgb_to_grayscale = rgb_to_grayscale
    sys.modules[module_name] = shim


patch_torchvision_functional_tensor()
