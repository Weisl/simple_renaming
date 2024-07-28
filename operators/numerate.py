import bpy

from .renaming_operators import switch_to_edit_mode
from .. import __package__ as base_package
from ..operators.renaming_utilities import get_renaming_list, call_renaming_popup, call_error_popup


class VIEW3D_OT_renaming_numerate(bpy.types.Operator):
    bl_idname = "renaming.numerate"
    bl_label = "Numerate"
    bl_description = "adds a growing number to the object names with the amount of digits specified in Number Length"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        prefs = context.preferences.addons[base_package].preferences
        separator = prefs.renaming_separator

        wm = context.scene

        start_number = prefs.numerate_start_number

        step = prefs.numerate_step
        digits = prefs.numerate_digits

        msg = wm.renaming_messages

        renaming_list, switch_edit_mode, errMsg = get_renaming_list(context)

        if errMsg is not None:
            error_msg = wm.renaming_error_messages
            error_msg.add_message(errMsg)
            call_error_popup(context)
            return {'CANCELLED'}

        if len(renaming_list) > 0:
            i = 0
            for entity in renaming_list:
                if entity is not None:
                    oldName = entity.name
                    new_name = entity.name + separator + (
                        '{num:{fill}{width}}'.format(num=(i * step) + start_number, fill='0', width=digits))
                    entity.name = new_name
                    msg.add_message(oldName, entity.name)
                    i = i + 1

        call_renaming_popup(context)
        if switch_edit_mode:
            switch_to_edit_mode(context)
        return {'FINISHED'}
