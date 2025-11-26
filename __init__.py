import bpy
import sys
import importlib
from pathlib import Path

bl_info = {
    "name": "PrevizMode",
    "author": "histeria",
    "version": (0, 6, 0),
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar > PREVIZ MODE",
    "description": "Interface para mudar rapidamente entre modo de render e previz",
    "category": "Previz",
}


# Importar o módulo diretamente
from .src.panels import pvz_panel

modules = [
    pvz_panel,
]


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