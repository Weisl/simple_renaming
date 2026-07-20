import time

import bpy

from .numbering import format_number
from .renaming_operators import switch_to_edit_mode
from .. import __package__ as base_package
from ..operators.renaming_utilities import get_renaming_list, call_renaming_popup, call_error_popup, apply_rename, report_rename_warnings, log_timing


class VIEW3D_OT_renaming_numerate(bpy.types.Operator):
    bl_idname = "renaming.numerate"
    bl_label = "Numerate"
    bl_description = "adds a growing number to the object names with the amount of digits specified in Number Length"
    bl_options = {'REGISTER', 'UNDO'}

    start_number: bpy.props.IntProperty(name="Start", default=1)
    step: bpy.props.IntProperty(name="Step", default=1)
    digits: bpy.props.IntProperty(name="Digits", default=3, min=0)
    use_letters: bpy.props.BoolProperty(name="Use Letters", default=False)
    letters_upper: bpy.props.BoolProperty(name="Uppercase Letters", default=True)

    def invoke(self, context, event):
        prefs = context.preferences.addons[base_package].preferences
        self.start_number = prefs.numerate_start_number
        self.step = prefs.numerate_step
        self.digits = prefs.numerate_digits
        self.use_letters = prefs.numerate_use_letters
        self.letters_upper = prefs.numerate_letters_upper
        return self.execute(context)

    def execute(self, context):
        prefs = context.preferences.addons[base_package].preferences
        separator = prefs.renaming_separator

        wm = context.scene

        start_number = self.start_number
        step = self.step
        digits = self.digits
        use_letters = self.use_letters
        letters_upper = self.letters_upper

        msg = wm.renaming_messages
        msg.clear()
        conflicts = 0
        protected = 0

        renaming_list, switch_edit_mode, errMsg = get_renaming_list(context)

        if errMsg is not None:
            error_msg = wm.renaming_error_messages
            error_msg.clear()
            error_msg.add_message(errMsg)
            call_error_popup(context)
            return {'CANCELLED'}

        per_object_types = {'SHAPEKEYS', 'VERTEXGROUPS', 'UVMAPS', 'COLORATTRIBUTES', 'ATTRIBUTES', 'BONE'}
        obj_type = wm.renaming_object_types

        t_start = time.perf_counter()
        if len(renaming_list) > 0:
            i = 0
            current_owner = None
            for entity in renaming_list:
                if entity is not None:
                    if obj_type in per_object_types:
                        owner = entity.id_data
                        if owner != current_owner:
                            current_owner = owner
                            i = 0
                    new_name = entity.name + separator + format_number(
                        (i * step) + start_number, digits, use_letters, letters_upper)
                    _, warning, is_protected = apply_rename(wm, entity, new_name, msg)
                    if is_protected:
                        protected += 1
                    elif warning:
                        conflicts += 1
                    i = i + 1

        log_timing(context, "numerate", t_start, len(renaming_list))
        report_rename_warnings(self, conflicts, protected)
        call_renaming_popup(context)
        if switch_edit_mode:
            switch_to_edit_mode(context)
        return {'FINISHED'}
