import time

import bpy

from .renaming_operators import switch_to_edit_mode
from ..operators.renaming_utilities import get_renaming_list, trim_string, call_renaming_popup, call_error_popup, apply_rename, report_rename_warnings, log_timing


class VIEW3D_OT_trim_string(bpy.types.Operator):
    bl_idname = "renaming.trim_string"
    bl_label = "Trim String"
    bl_description = "Deletes the in the trim size specified amount of characters at the start or the end of object names"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        wm = context.scene
        renaming_list, switch_edit_mode, errMsg = get_renaming_list(context)

        if errMsg is not None:
            error_msg = wm.renaming_error_messages
            error_msg.clear()
            error_msg.add_message(errMsg)
            call_error_popup(context)
            return {'CANCELLED'}

        t_start = time.perf_counter()
        msg = wm.renaming_messages
        msg.clear()
        conflicts = 0
        protected = 0

        if len(renaming_list) > 0:
            for entity in renaming_list:
                if entity is not None:
                    new_name = trim_string(entity.name, wm.renaming_trim_indices)
                    _, warning, is_protected = apply_rename(wm, entity, new_name, msg)
                    if is_protected:
                        protected += 1
                    elif warning:
                        conflicts += 1

        log_timing(context, "trim_string", t_start, len(renaming_list))
        report_rename_warnings(self, conflicts, protected)
        call_renaming_popup(context)

        if switch_edit_mode:
            switch_to_edit_mode(context)

        return {'FINISHED'}
