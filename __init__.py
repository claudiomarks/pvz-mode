import bpy
import sys
import importlib
from pathlib import Path

bl_info = {
    "name": "PrevizMode",
    "author": "histeria",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > PREVIZ MODE",
    "description": "Interface para mudar rapidamente entre modo de render e previz",
    "category": "Previz",
}

# Importar módulos
module_names = [
    "panels.pvz_panel",
]

modules = []
for module_name in module_names:
    if module_name in sys.modules:
        modules.append(importlib.reload(sys.modules[module_name]))
    else:
        parent = ".".join(__name__.split(".")[:-1])
        if parent:
            modules.append(importlib.import_module(f".{module_name}", parent))
        else:
            modules.append(importlib.import_module(module_name))


def register():
    for module in modules:
        if hasattr(module, "register"):
            module.register()


def unregister():
    for module in reversed(modules):
        if hasattr(module, "unregister"):
            module.unregister()


if __name__ == "__main__":
    register()