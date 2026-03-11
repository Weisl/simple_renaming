import re

import bpy

from .renaming_operators import switch_to_edit_mode
from ..operators.renaming_utilities import get_renaming_list, call_renaming_popup, call_error_popup
from ..variable_replacer.variable_replacer import VariableReplacer


class VIEW3D_OT_search_and_replace(bpy.types.Operator):
    bl_idname = "renaming.search_replace"
    bl_label = "Search and Replace"
    bl_description = "replaces parts in the object names"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        wm = context.scene

        # get list of objects to be renamed
        renaming_list, switch_edit_mode, errMsg = get_renaming_list(context)

        if errMsg is not None:
            error_msg = wm.renaming_error_messages
            error_msg.add_message(errMsg)
            call_error_popup(context)
            return {'CANCELLED'}

        searchName = wm.renaming_search

        msg = wm.renaming_messages  # variable to save messages

        VariableReplacer.reset()

        if len(renaming_list) > 0:
            for entity in renaming_list:  # iterate over all objects that are to be renamed
                if entity is not None:
                    if searchName != '':
                        oldName = entity.name
                        searchReplaced = VariableReplacer.replaceInputString(context, wm.renaming_search, entity)
                        replaceReplaced = VariableReplacer.replaceInputString(context, wm.renaming_replace, entity)
                        if not wm.renaming_useRegex:
                            if wm.renaming_matchcase:
                                new_name = str(entity.name).replace(searchReplaced, replaceReplaced)
                                entity.name = new_name
                                msg.add_message(oldName, entity.name)
                            else:
                                replaceSearch = re.compile(re.escape(searchReplaced), re.IGNORECASE)
                                new_name = replaceSearch.sub(lambda m: replaceReplaced, entity.name)
                                entity.name = new_name
                                msg.add_message(oldName, entity.name)
                        else:  # Use regex
                            # build and compile pattern once, catching errors
                            try:
                                # note: we want to allow user-specified regex, so don't escape
                                flags = 0
                                if not wm.renaming_matchcase:
                                    flags |= re.IGNORECASE
                                pattern = re.compile(searchReplaced, flags)
                            except re.error as err:
                                # invalid regex, warn user and abort operation
                                errMsg = f"Invalid regular expression: {err}"
                                wm.renaming_error_messages.add_message(errMsg)
                                call_error_popup(context)
                                return {'CANCELLED'}

                            try:
                                new_name = pattern.sub(replaceReplaced, str(entity.name))
                            except re.error as err:
                                # should not normally happen after compilation, but guard anyway
                                errMsg = f"Regex substitution error: {err}"
                                wm.renaming_error_messages.add_message(errMsg)
                                call_error_popup(context)
                                return {'CANCELLED'}

                            entity.name = new_name
                            msg.add_message(oldName, entity.name)

        call_renaming_popup(context)
        if switch_edit_mode:
            switch_to_edit_mode(context)
        return {'FINISHED'}
