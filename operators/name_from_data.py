import bpy

from .renaming_operators import switch_to_edit_mode
from .renaming_utilities import get_renaming_list, call_error_popup, call_renaming_popup


class VIEW3D_OT_use_objectname_for_data(bpy.types.Operator):
    bl_idname = "renaming.data_name_from_obj"
    bl_label = "Data Name from Object"
    bl_description = "Renames the object data according to the object name and adds the in the data textfield " \
                     "specified suffix. "
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        wm = context.scene
        suffix_data = wm.renaming_suffix_prefix_data_02
        msg = context.scene.renaming_messages
        renaming_list, switch_edit_mode, errMsg = get_renaming_list(context)

        if errMsg is not None:
            error_msg = wm.renaming_error_messages
            error_msg.add_message(errMsg)
            call_error_popup(context)
            return {'CANCELLED'}

        for obj in renaming_list:

            if obj.data:
                oldName = obj.data.name
                new_name = obj.name + suffix_data
                obj.data.name = new_name
                msg.add_message(oldName, obj.data.name)

        call_renaming_popup(context)
        if switch_edit_mode:
            switch_to_edit_mode(context)

        return {'FINISHED'}
