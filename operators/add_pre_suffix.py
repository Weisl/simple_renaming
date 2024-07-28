import bpy

from .renaming_operators import switch_to_edit_mode
from ..operators.renaming_utilities import get_renaming_list, call_renaming_popup, call_error_popup
from ..variable_replacer.variable_replacer import VariableReplacer


class VIEW3D_OT_add_suffix(bpy.types.Operator):
    bl_idname = "renaming.add_suffix"
    bl_label = "Add suffix"
    bl_description = "Adds a suffix to object names"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        wm = context.scene

        renaming_list, switch_edit_mode, errMsg = get_renaming_list(context)

        if errMsg is not None:
            error_msg = wm.renaming_error_messages
            error_msg.add_message(errMsg)
            call_error_popup(context)
            return {'CANCELLED'}

        msg = wm.renaming_messages

        VariableReplacer.reset()
        if len(renaming_list) > 0:
            for entity in renaming_list:
                if entity is not None:
                    suffix = VariableReplacer.replaceInputString(context, wm.renaming_suffix, entity)
                    if not entity.name.endswith(suffix):
                        oldName = entity.name
                        new_name = entity.name + suffix
                        entity.name = new_name
                        msg.add_message(oldName, entity.name)
        else:
            msg.add_message(None, None, "Insert Valid String")
        if switch_edit_mode:
            switch_to_edit_mode(context)
        call_renaming_popup(context)
        return {'FINISHED'}


class VIEW3D_OT_add_prefix(bpy.types.Operator):
    bl_idname = "renaming.add_prefix"
    bl_label = "Add Prefix"
    bl_description = "Adds a prefix to object names"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        wm = context.scene

        msg = wm.renaming_messages

        renaming_list, switch_edit_mode, errMsg = get_renaming_list(context)

        if errMsg is not None:
            error_msg = wm.renaming_error_messages
            error_msg.add_message(errMsg)
            call_error_popup(context)
            return {'CANCELLED'}

        VariableReplacer.reset()

        if len(renaming_list) > 0:
            for entity in renaming_list:
                if entity is not None:
                    pre = VariableReplacer.replaceInputString(context, wm.renaming_prefix, entity)
                    if not entity.name.startswith(pre):
                        oldName = entity.name
                        new_name = pre + entity.name
                        entity.name = new_name
                        msg.add_message(oldName, entity.name)

        call_renaming_popup(context)
        if switch_edit_mode:
            switch_to_edit_mode(context)

        return {'FINISHED'}
