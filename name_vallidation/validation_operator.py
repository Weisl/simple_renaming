import re

import bpy

from .. import __package__ as base_package
from ..operators.renaming_utilities import getRenamingList, callInfoPopup


class VIEW3D_OT_Validate(bpy.types.Operator):
    bl_idname = "renaming.validate"
    bl_label = "Validate Names"
    bl_description = "replaces parts in the object names"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        wm = context.scene
        prefs = context.preferences.addons[f'{base_package}'].preferences
        regex = prefs.regex_Mesh

        renaming_list, switch_edit_mode, err_msg = getRenamingList(context)

        if len(renaming_list) > 0:
            for entity in renaming_list:
                if entity is not None:
                    if regex != '':
                        match = bool(re.compile(regex).match(entity.name))

                        if match:
                            wm.renaming_info_messages.addMessage("Valid", entity.name)
                        else:
                            wm.renaming_info_messages.addMessage("Not", entity.name)

        callInfoPopup(context)
        return {'FINISHED'}



