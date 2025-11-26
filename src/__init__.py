import bpy
import json
import os
import sys  # Para listar os módulos carregados
from bpy.types import Panel, Operator, UIList
from bpy.props import StringProperty, BoolProperty, EnumProperty

bl_info = {
    "name": "PrevizMode",
    "author": "histeria",
    "version": (0, 1, 0),
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar > PREVIZ MODE",
    "description": "interface para mudar rapidamente entre modo de render e previz",
    "category": "Previz",
}