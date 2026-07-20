import re
import time

import bpy

from .renaming_operators import switch_to_edit_mode
from ..operators.renaming_utilities import get_renaming_list, call_renaming_popup, call_error_popup, apply_rename, report_rename_warnings, log_timing
from ..variable_replacer.variable_replacer import VariableReplacer
from .case_transform import to_upper, to_lower, upper_first, lower_first


# ---------------------------------------------------------------------------
# Regex replace with \u \l \U \L case modifier support
# Modifiers apply to the immediately following group reference ($N or \N).
#   \u$1  — uppercase first char of group 1
#   \l$1  — lowercase first char of group 1
#   \U$1  — uppercase all of group 1
#   \L$1  — lowercase all of group 1
# Both $1 and \1 are accepted as group references.
# ---------------------------------------------------------------------------

def _read_group_ref(repl, i, match):
    """Read a $N or \\N group reference at position i.
    Returns (group_value, chars_consumed)."""
    if i >= len(repl):
        return '', 0
    c = repl[i]
    if c in ('$', '\\') and i + 1 < len(repl) and repl[i + 1].isdigit():
        group_num = int(repl[i + 1])
        try:
            return match.group(group_num) or '', 2
        except IndexError:
            return '', 0
    return '', 0


def _expand_replacement(repl, match):
    """Expand a replacement string, handling case modifiers and group refs."""
    result = []
    i = 0
    n = len(repl)

    while i < n:
        c = repl[i]

        if c == '\\' and i + 1 < n:
            next_c = repl[i + 1]

            if next_c in ('u', 'l', 'U', 'L'):
                modifier = next_c
                i += 2
                group_val, advance = _read_group_ref(repl, i, match)
                i += advance
                if modifier == 'u':
                    group_val = upper_first(group_val)
                elif modifier == 'l':
                    group_val = lower_first(group_val)
                elif modifier == 'U':
                    group_val = to_upper(group_val)
                elif modifier == 'L':
                    group_val = to_lower(group_val)
                result.append(group_val)

            elif next_c.isdigit():
                group_num = int(next_c)
                try:
                    result.append(match.group(group_num) or '')
                except IndexError:
                    result.append('\\' + next_c)
                i += 2

            else:
                result.append(c)
                i += 1

        elif c == '$' and i + 1 < n and repl[i + 1].isdigit():
            group_num = int(repl[i + 1])
            try:
                result.append(match.group(group_num) or '')
            except IndexError:
                result.append(c)
            i += 2

        else:
            result.append(c)
            i += 1

    return ''.join(result)


def regex_case_sub(pattern, repl, string):
    """re.sub that additionally supports \\u \\l \\U \\L case modifiers."""
    if not re.search(r'\\[uUlL]', repl):
        return re.sub(pattern, repl, string)

    def replacer(match):
        return _expand_replacement(repl, match)

    return re.sub(pattern, replacer, string)


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
            error_msg.clear()
            error_msg.add_message(errMsg)
            call_error_popup(context)
            return {'CANCELLED'}

        t_start = time.perf_counter()
        searchName = wm.renaming_search

        msg = wm.renaming_messages  # variable to save messages
        msg.clear()
        conflicts = 0
        protected = 0

        VariableReplacer.reset()
        VariableReplacer.prepare(context)

        # When the search string contains no @ variables it is the same for
        # every entity, so the case-insensitive pattern can be compiled once.
        search_has_variables = '@' in searchName
        static_pattern = None
        if not wm.renaming_useRegex and not wm.renaming_matchcase and not search_has_variables and searchName != '':
            static_pattern = re.compile(re.escape(searchName), re.IGNORECASE)

        if len(renaming_list) > 0:
            for entity in renaming_list:  # iterate over all objects that are to be renamed
                if entity is not None:
                    if searchName != '':
                        searchReplaced = VariableReplacer.replaceInputString(context, wm.renaming_search, entity)
                        replaceReplaced = VariableReplacer.replaceInputString(context, wm.renaming_replace, entity)
                        if not wm.renaming_useRegex:
                            if wm.renaming_matchcase:
                                new_name = str(entity.name).replace(searchReplaced, replaceReplaced)
                            else:
                                pattern = static_pattern or re.compile(re.escape(searchReplaced), re.IGNORECASE)
                                new_name = pattern.sub(replaceReplaced, entity.name)
                        else:  # Use regex
                            new_name = regex_case_sub(searchReplaced, replaceReplaced, str(entity.name))
                        _, warning, is_protected = apply_rename(wm, entity, new_name, msg)
                        if is_protected:
                            protected += 1
                        elif warning:
                            conflicts += 1

        log_timing(context, "search_replace", t_start, len(renaming_list))
        report_rename_warnings(self, conflicts, protected)
        call_renaming_popup(context)
        if switch_edit_mode:
            switch_to_edit_mode(context)
        return {'FINISHED'}
