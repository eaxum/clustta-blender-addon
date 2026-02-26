"""Clustta Blender Addon — version control and collaboration for artists."""

import importlib
import sys

from . import api_client, helpers, operators, panels, props

# Module reload support for Blender development
_modules = [api_client, helpers, props, operators, panels]

def _reload_modules():
    for mod in _modules:
        importlib.reload(mod)


def register():
    """Register all Clustta classes and properties with Blender."""
    if f"{__name__}.panels" in sys.modules:
        _reload_modules()

    props.register()
    operators.register()
    panels.register()


def unregister():
    """Unregister all Clustta classes and properties from Blender."""
    panels.unregister()
    operators.unregister()
    props.unregister()


if __name__ == "__main__":
    register()
