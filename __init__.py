'''
Copyright (C) 2019 Matthias Patscheider
patscheider.matthias@gmail.com

Created by Matthias Patscheider

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
    "name": "Simple Renaming Panel",
    "description": "This Addon offers the basic functionality of renaming a set of objects",
    "author": "Matthias Patscheider",
    "version": (2, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Tools ",
    "warning": "",
    "wiki_url": "https://weisl.github.io/renaming/",
    "doc_url": "https://weisl.github.io/renaming/",
    "tracker_url": "https://github.com/Weisl/simple_renaming_panel/issues",
    "support": "COMMUNITY",
    "category": "Scene"
}

# support reloading sub-modules
if "bpy" in locals():
    import importlib

    importlib.reload(add_suffix_panel)
    importlib.reload(operators)
    importlib.reload(preferences)
    importlib.reload(ui)
    #.reload(vallidation)
    importlib.reload(variable_replacer)

else:
    from . import add_suffix_panel
    from . import operators
    from . import preferences
    from . import ui
    #from . import vallidation
    from . import variable_replacer

# import standard modules
import bpy

def menu_add_suffix(self, context):
    self.layout.operator(VIEW3D_OT_add_suffix.bl_idname)  # or YourClass.bl_idname

    from ..preferences.renaming_preferences import update_panel_category
    update_panel_category(None, bpy.context)
def register():

    add_suffix_panel.register()
    operators.register()
    ui.register()
    #vallidation.register()

    # keymap and preferences should be last
    preferences.register()


def unregister():

    # keymap and preferences should be last
    preferences.unregister()

    #vallidation.unregister()
    ui.unregister()
    operators.unregister()
    add_suffix_panel.unregister()



if __name__ == "__main__":
    register()
