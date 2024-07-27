import bpy

from .renaming_operators import switchToEditMode
from ..operators.renaming_utilities import getRenamingList, callRenamingPopup, callErrorPopup


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
        renamingList, switchEditMode, errMsg = getRenamingList(context)

        if errMsg is not None:
            errorMsg = wm.renaming_error_messages
            errorMsg.addMessage(errMsg)
            callErrorPopup(context)
            return {'CANCELLED'}

        for obj in renamingList:

            if obj.data:
                oldName = obj.data.name
                new_name = obj.name + suffix_data
                obj.data.name = new_name
                msg.addMessage(oldName, obj.data.name)

        callRenamingPopup(context)
        if switchEditMode:
            switchToEditMode(context)

        return {'FINISHED'}
