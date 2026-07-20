import re

import bpy

from .renaming_operators import switch_to_edit_mode
from .. import __package__ as base_package
from ..operators.renaming_utilities import get_renaming_list, call_renaming_popup, call_error_popup, apply_rename, report_rename_warnings

_DIGIT_RUN_RE = re.compile(r'\d+')
_LETTER_RUN_RE = re.compile(r'[A-Za-z]+')


def _last_match(pattern, name):
    matches = list(pattern.finditer(name))
    return matches[-1] if matches else None


def pad_number(name, width):
    """Pad/strip the last number in the name to `width` digits (width=0 → no leading zeros)."""
    match = _last_match(_DIGIT_RUN_RE, name)
    if not match:
        return name
    formatted = '{:0{width}d}'.format(int(match.group()), width=width)
    return name[:match.start()] + formatted + name[match.end():]


def number_to_letters(name, upper, separator):
    """Convert the last number in the name to spreadsheet-style letters (1-based, base-26).

    Inserts `separator` before the letters when they'd otherwise be glued
    directly onto a preceding letter (e.g. "Cube9" -> "Cube_i" rather than
    "Cubei") — without a delimiter there, the letters become indistinguishable
    from the base name and letters_to_number() can't reverse the conversion.
    """
    match = _last_match(_DIGIT_RUN_RE, name)
    if not match:
        return name
    n = int(match.group())
    if n <= 0:
        return name
    letters = ''
    while n > 0:
        n, rem = divmod(n - 1, 26)
        letters = chr(65 + rem) + letters
    if not upper:
        letters = letters.lower()
    prefix = name[:match.start()]
    if prefix and prefix[-1].isalpha():
        prefix += separator
    return prefix + letters + name[match.end():]


def letters_to_number(name):
    """Convert the last letter run in the name back to its spreadsheet-style number."""
    match = _last_match(_LETTER_RUN_RE, name)
    if not match:
        return name
    n = 0
    for ch in match.group().upper():
        n = n * 26 + (ord(ch) - 64)
    return name[:match.start()] + str(n) + name[match.end():]


# ---------------------------------------------------------------------------
# Operator base
# ---------------------------------------------------------------------------

class _NumberOperatorBase(bpy.types.Operator):
    bl_options = {'REGISTER', 'UNDO'}

    def _transform(self, name, context):
        raise NotImplementedError

    def execute(self, context):
        scene = context.scene
        renaming_list, switch_edit_mode, errMsg = get_renaming_list(context)

        if errMsg is not None:
            scene.renaming_error_messages.clear()
            scene.renaming_error_messages.add_message(errMsg)
            call_error_popup(context)
            return {'CANCELLED'}

        msg = scene.renaming_messages
        msg.clear()
        conflicts = 0
        protected = 0
        for entity in renaming_list:
            if entity is not None:
                new_name = self._transform(entity.name, context)
                _, warning, is_protected = apply_rename(scene, entity, new_name, msg)
                if is_protected:
                    protected += 1
                elif warning:
                    conflicts += 1

        report_rename_warnings(self, conflicts, protected)
        call_renaming_popup(context)
        if switch_edit_mode:
            switch_to_edit_mode(context)
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# Operators
# ---------------------------------------------------------------------------

class VIEW3D_OT_number_pad(_NumberOperatorBase):
    bl_idname = "renaming.number_pad"
    bl_label = "Set Number Width"
    bl_description = "Pad or strip leading zeros on the last number in the name to match Number Width  (009 → 9 at width 1, 9 → 009 at width 3)"

    def _transform(self, name, context):
        return pad_number(name, context.scene.renaming_number_width)


class VIEW3D_OT_number_to_letters_lower(_NumberOperatorBase):
    bl_idname = "renaming.number_to_letters_lower"
    bl_label = "Number → letters"
    bl_description = "Convert the last number in the name to spreadsheet-style letters  (1 → a, 2 → b, … 26 → z, 27 → aa …)"

    def _transform(self, name, context):
        prefs = context.preferences.addons[base_package].preferences
        return number_to_letters(name, upper=False, separator=prefs.renaming_separator)


class VIEW3D_OT_number_to_letters_upper(_NumberOperatorBase):
    bl_idname = "renaming.number_to_letters_upper"
    bl_label = "Number → LETTERS"
    bl_description = "Convert the last number in the name to spreadsheet-style letters  (1 → A, 2 → B, … 26 → Z, 27 → AA …)"

    def _transform(self, name, context):
        prefs = context.preferences.addons[base_package].preferences
        return number_to_letters(name, upper=True, separator=prefs.renaming_separator)


class VIEW3D_OT_letters_to_number(_NumberOperatorBase):
    bl_idname = "renaming.letters_to_number"
    bl_label = "Letters → Number"
    bl_description = "Convert the last letter run in the name back to its spreadsheet-style number  (A → 1, B → 2, … Z → 26, AA → 27 …)"

    def _transform(self, name, context):
        return letters_to_number(name)
