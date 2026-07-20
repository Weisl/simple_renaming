import re

import bpy

from .renaming_operators import switch_to_edit_mode
from ..operators.renaming_utilities import get_renaming_list, call_renaming_popup, call_error_popup, apply_rename, report_rename_warnings


# ---------------------------------------------------------------------------
# Word splitting — handles snake_case, kebab-case, PascalCase, camelCase
# ---------------------------------------------------------------------------

def split_words(name):
    """Split a name into words regardless of input convention."""
    # camelCase / PascalCase boundaries: lowercase→Uppercase
    name = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', name)
    # Runs of capitals before a capitalised word: XMLParser → XML Parser
    name = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', name)
    # Replace separators with spaces
    name = re.sub(r'[-_\s]+', ' ', name)
    return [w for w in name.split(' ') if w]


# ---------------------------------------------------------------------------
# Conversion helpers (also imported by search_replace for \u \l \U \L)
# ---------------------------------------------------------------------------

def to_upper(text):
    return text.upper()


def to_lower(text):
    return text.lower()


def upper_first(text):
    """Uppercase only the first character, leave the rest unchanged."""
    return text[:1].upper() + text[1:] if text else text


def lower_first(text):
    """Lowercase only the first character, leave the rest unchanged."""
    return text[:1].lower() + text[1:] if text else text


def to_pascal_case(name):
    """hello_world → HelloWorld"""
    return ''.join(w.capitalize() for w in split_words(name))


def to_camel_case(name):
    """hello_world → helloWorld"""
    words = split_words(name)
    if not words:
        return name
    return words[0].lower() + ''.join(w.capitalize() for w in words[1:])


def to_snake_case(name):
    """HelloWorld → hello_world"""
    return '_'.join(w.lower() for w in split_words(name))


def to_kebab_case(name):
    """HelloWorld → hello-world"""
    return '-'.join(w.lower() for w in split_words(name))


# ---------------------------------------------------------------------------
# Operator base
# ---------------------------------------------------------------------------

class _CaseOperatorBase(bpy.types.Operator):
    bl_options = {'REGISTER', 'UNDO'}

    def _transform(self, name):
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
                new_name = self._transform(entity.name)
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

class VIEW3D_OT_case_upper(_CaseOperatorBase):
    bl_idname = "renaming.case_upper"
    bl_label = "UPPERCASE"
    bl_description = "Convert name to UPPERCASE  (hello_world → HELLO_WORLD)"

    def _transform(self, name):
        return to_upper(name)


class VIEW3D_OT_case_lower(_CaseOperatorBase):
    bl_idname = "renaming.case_lower"
    bl_label = "lowercase"
    bl_description = "Convert name to lowercase  (Hello_World → hello_world)"

    def _transform(self, name):
        return to_lower(name)


class VIEW3D_OT_case_pascal(_CaseOperatorBase):
    bl_idname = "renaming.case_pascal"
    bl_label = "PascalCase"
    bl_description = "Convert name to PascalCase  (hello_world → HelloWorld)"

    def _transform(self, name):
        return to_pascal_case(name)


class VIEW3D_OT_case_camel(_CaseOperatorBase):
    bl_idname = "renaming.case_camel"
    bl_label = "camelCase"
    bl_description = "Convert name to camelCase  (hello_world → helloWorld)"

    def _transform(self, name):
        return to_camel_case(name)


class VIEW3D_OT_case_snake(_CaseOperatorBase):
    bl_idname = "renaming.case_snake"
    bl_label = "snake_case"
    bl_description = "Convert name to snake_case  (HelloWorld → hello_world)"

    def _transform(self, name):
        return to_snake_case(name)


class VIEW3D_OT_case_kebab(_CaseOperatorBase):
    bl_idname = "renaming.case_kebab"
    bl_label = "kebab-case"
    bl_description = "Convert name to kebab-case  (HelloWorld → hello-world)"

    def _transform(self, name):
        return to_kebab_case(name)
