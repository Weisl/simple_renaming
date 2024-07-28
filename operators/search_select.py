import re

import bpy

from .renaming_operators import switch_to_edit_mode
from ..operators.renaming_utilities import get_renaming_list, call_error_popup
from ..variable_replacer.variable_replacer import VariableReplacer


class VIEW3D_OT_naming(bpy.types.Operator):
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        VariableReplacer.reset()
        return


class VIEW3D_OT_search_and_select(VIEW3D_OT_naming):
    bl_idname = "renaming.search_select"
    bl_label = "Search and Select"
    bl_description = "Select Object By Name"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        return super().invoke(context, event)

    def execute(self, context):
        super().execute(context)
        wm = context.scene

        # get list of objects to be selected
        selectionList = []

        renaming_list, switch_edit_mode, errMsg = get_renaming_list(context)

        if errMsg is not None:
            error_msg = wm.renaming_error_messages
            error_msg.add_message(errMsg)
            call_error_popup(context)
            return {'CANCELLED'}

        searchName = wm.renaming_search
        msg = wm.renaming_messages  # variable to save messages

        if len(renaming_list) > 0:
            for entity in renaming_list:  # iterate over all objects that are to be renamed
                if entity is not None and searchName != '':
                    entityName = entity.name
                    searchReplaced = VariableReplacer.replaceInputString(context, searchName, entity)

                    if wm.renaming_matchcase:
                        if entityName.find(searchReplaced) >= 0:
                            selectionList.append(entity)
                            msg.add_message("selected", entityName)
                    else:
                        if re.search(searchReplaced, entityName, re.IGNORECASE):
                            selectionList.append(entity)

        if str(wm.renaming_object_types) == 'OBJECT':
            # set to object mode
            if bpy.context.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')

            bpy.ops.object.select_all(action='DESELECT')

            for obj in selectionList:
                obj.select_set(True)

        elif str(wm.renaming_object_types) == 'BONE':
            # print("SELECTION LIST: " + str(selectionList))
            if bpy.context.mode == 'POSE':
                bpy.ops.pose.select_all(action='DESELECT')
                for bone in selectionList:
                    bone.select = True

            elif bpy.context.mode == 'EDIT_ARMATURE':
                bpy.ops.armature.select_all(action='DESELECT')
                for bone in selectionList:
                    # print("EDIT Bone: " + str(bone))
                    bone.select = True
                    bone.select_head = True
                    bone.select_tail = True

        # call_renaming_popup(context)
        if switch_edit_mode:
            switch_to_edit_mode(context)
        return {'FINISHED'}
