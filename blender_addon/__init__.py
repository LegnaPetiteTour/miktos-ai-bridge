
bl_info = {
    "name": "Miktos Bridge",
    "author": "Miktos Universe", 
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Miktos",
    "description": "Bridge between Blender and Miktos AI Platform",
    "category": "3D View",
}

import bpy
from . import miktos_panel
from . import miktos_operators

def register():
    miktos_panel.register()
    miktos_operators.register()

def unregister():
    miktos_panel.unregister()
    miktos_operators.unregister()

if __name__ == "__main__":
    register()
