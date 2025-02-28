import bpy

from .renaming_operators import switch_to_edit_mode
from ..operators.renaming_utilities import get_renaming_list, trim_string, call_renaming_popup, call_error_popup
    
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
            error_msg.add_message(errMsg)
            call_error_popup(context)
            return {'CANCELLED'}

        msg = wm.renaming_messages

        if len(renaming_list) > 0:
            for entity in renaming_list:
                if entity is not None:
                    old_name = entity.name
                    new_name = trim_string(entity.name, wm.renaming_trim_indices)
                    entity.name = new_name
                    msg.add_message(old_name, entity.name)

        wm.renaming_trim_indices = (0, 0)
        
        call_renaming_popup(context)

        if switch_edit_mode:
            switch_to_edit_mode(context)
            
        return {'FINISHED'}
