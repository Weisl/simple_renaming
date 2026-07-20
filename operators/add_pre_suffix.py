import time

import bpy

from .renaming_operators import switch_to_edit_mode
from ..operators.renaming_utilities import get_renaming_list, call_renaming_popup, call_error_popup, apply_rename, report_rename_warnings, log_timing
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

        t_start = time.perf_counter()
        msg = wm.renaming_messages
        conflicts = 0
        protected = 0

        VariableReplacer.reset()
        VariableReplacer.prepare(context)
        if len(renaming_list) > 0:
            for entity in renaming_list:
                if entity is not None:
                    suffix = VariableReplacer.replaceInputString(context, wm.renaming_suffix, entity)
                    if not entity.name.endswith(suffix):
                        new_name = entity.name + suffix
                        _, warning, is_protected = apply_rename(wm, entity, new_name, msg)
                        if is_protected:
                            protected += 1
                        elif warning:
                            conflicts += 1
        else:
            msg.add_message(None, None, warning="Insert Valid String")
        if switch_edit_mode:
            switch_to_edit_mode(context)
        log_timing(context, "add_suffix", t_start, len(renaming_list))
        report_rename_warnings(self, conflicts, protected)
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
        conflicts = 0
        protected = 0

        renaming_list, switch_edit_mode, errMsg = get_renaming_list(context)

        if errMsg is not None:
            error_msg = wm.renaming_error_messages
            error_msg.add_message(errMsg)
            call_error_popup(context)
            return {'CANCELLED'}

        t_start = time.perf_counter()
        VariableReplacer.reset()
        VariableReplacer.prepare(context)

        if len(renaming_list) > 0:
            for entity in renaming_list:
                if entity is not None:
                    pre = VariableReplacer.replaceInputString(context, wm.renaming_prefix, entity)
                    if not entity.name.startswith(pre):
                        new_name = pre + entity.name
                        _, warning, is_protected = apply_rename(wm, entity, new_name, msg)
                        if is_protected:
                            protected += 1
                        elif warning:
                            conflicts += 1
        else:
            msg.add_message(None, None, warning="Insert Valid String")

        log_timing(context, "add_prefix", t_start, len(renaming_list))
        report_rename_warnings(self, conflicts, protected)
        call_renaming_popup(context)
        if switch_edit_mode:
            switch_to_edit_mode(context)

        return {'FINISHED'}
