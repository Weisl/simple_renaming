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
    "version": (1, 5, 3),
    "blender": (3, 0, 0),
    "location": "View3D > Tools ",
    "warning": "",
    "wiki_url": "https://weisl.github.io/renaming/",
    "tracker_url": "https://github.com/Weisl/simple_renaming_panel/issues",
    "support": "COMMUNITY",
    "category": "Scene"
}

# support reloading sub-modules
if "bpy" in locals():
    import importlib

    importlib.reload(renaming_operators)
    importlib.reload(renaming_popup)
    importlib.reload(renaming_utilities)
    importlib.reload(renaming_panels)
    # importlib.reload(renaming_vallidate)
    importlib.reload(renaming_sufPre_operators)
    importlib.reload(renaming_proFeatures)
    importlib.reload(renaming_keymap)
    importlib.reload(renaming_preferences)
    importlib.reload(addon_updater)
    importlib.reload(addon_updater_ops)

else:
    from . import renaming_operators
    from . import renaming_popup
    from . import renaming_utilities
    from . import renaming_panels
    # from . import renaming_vallidate
    from . import renaming_sufPre_operators
    from . import renaming_proFeatures
    from . import renaming_keymap
    from . import renaming_preferences
    from . import addon_updater
    from . import addon_updater_ops

# import standard modules
import bpy

from .renaming_panels import panel_func
from .renaming_proFeatures import tChange
from .renaming_utilities import RENAMING_MESSAGES, WarningError_MESSAGES, INFO_MESSAGES


def menu_add_suffix(self, context):
    self.layout.operator(VIEW3D_OT_add_suffix.bl_idname)  # or YourClass.bl_idname

def register():
    addon_updater_ops.register(bl_info)

    # call the register function of the sub modules
    renaming_operators.register()
    renaming_popup.register()
    renaming_proFeatures.register()
    renaming_sufPre_operators.register()
    renaming_utilities.register()
    # renaming_vallidate.register()



    # keymap and preferences should be last
    renaming_keymap.register()
    renaming_preferences.register()
    renaming_panels.register()

    from.renaming_preferences import update_panel_category
    update_panel_category(None, bpy.context)

    bpy.types.VIEW3D_PT_tools_type_suffix.prepend(panel_func)


def unregister():
    addon_updater_ops.unregister()

    # keymap and preferences should be last
    renaming_preferences.unregister()
    renaming_panels.unregister()
    renaming_keymap.unregister()

    # renaming_vallidate.unregister()
    renaming_utilities.unregister()
    renaming_sufPre_operators.unregister()
    renaming_proFeatures.unregister()
    renaming_popup.unregister()
    renaming_operators.unregister()

if __name__ == "__main__":
    register()
