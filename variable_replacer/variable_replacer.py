import random
import re
import string
import time

import bpy

from .. import __package__ as base_package

# Single compiled pattern covering all supported variables.
# Multi-char tokens (@u1/@u2/@u3) are listed before the single-char fallback
# so the alternation matches them first.
_VARIABLE_RE = re.compile(r'@(?:u[123]|[fdirhlobantpmc])')


def generate_random_string(string_length=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(string_length))


class VariableReplacer:
    """This class is responsible for the custom variables"""
    addon_prefs = None
    entity = None
    number = 1
    digits = 3
    step = 1
    start_number = 0

    # Per-operation lookup caches built by prepare()
    _collection_cache = {}       # obj_name -> concatenated collection names
    _material_to_obj = {}        # material_name -> first owner object name
    _shape_key_to_obj = {}       # id(Key datablock) -> owner object name
    _mesh_arm_to_obj = {}        # id(obj.data) -> owner object name

    @classmethod
    def reset(cls):
        """reset all values to initial state"""
        prefs = bpy.context.preferences.addons[base_package].preferences
        start_number = prefs.numerate_start_number
        numerate_step = prefs.numerate_step
        numerate_digits = prefs.numerate_digits

        # print("reset = " + str(start_number))
        cls.step = numerate_step
        cls.digits = numerate_digits
        cls.start_number = start_number
        cls.number = 0

    @classmethod
    def prepare(cls, context):
        """Build per-operation lookup caches before the rename loop.

        Call this once per operator execution after reset().  The caches turn
        O(collections × objects) and O(objects) per-entity lookups into O(1).
        """
        # Collection reverse-lookup: obj_name -> concatenated collection names
        # (separated, since an object linked into multiple/nested collections
        # would otherwise produce a run-together name like "MainSub").
        separator = context.preferences.addons[base_package].preferences.renaming_separator
        collection_cache = {}
        for col in bpy.data.collections:
            for obj in col.objects:
                if obj.name in collection_cache:
                    collection_cache[obj.name] += separator + col.name
                else:
                    collection_cache[obj.name] = col.name
        cls._collection_cache = collection_cache

        # Material -> first owner object name
        material_to_obj = {}
        for obj in bpy.data.objects:
            for slot in obj.material_slots:
                if slot.material and slot.material.name not in material_to_obj:
                    material_to_obj[slot.material.name] = obj.name
        cls._material_to_obj = material_to_obj

        # Shape key (Key datablock) -> owner object name
        shape_key_to_obj = {}
        mesh_arm_to_obj = {}
        for obj in bpy.data.objects:
            if obj.data is None:
                continue
            data_id = id(obj.data)
            if data_id not in mesh_arm_to_obj:
                mesh_arm_to_obj[data_id] = obj.name
            if hasattr(obj.data, 'shape_keys') and obj.data.shape_keys is not None:
                sk_id = id(obj.data.shape_keys)
                if sk_id not in shape_key_to_obj:
                    shape_key_to_obj[sk_id] = obj.name
        cls._shape_key_to_obj = shape_key_to_obj
        cls._mesh_arm_to_obj = mesh_arm_to_obj

    @classmethod
    def replaceInputString(cls, context, inputText, entity):
        """Replace custom variables with the according string"""
        wm = context.scene
        cls.addon_prefs = context.preferences.addons[base_package].preferences

        if '@' not in inputText:
            return inputText

        # Find only the variables present in this template so we skip calling
        # getters that are not needed (lazy evaluation).
        vars_present = set(_VARIABLE_RE.findall(inputText))

        replacements = {}

        if '@n' in vars_present:
            replacements['@n'] = cls.getNumber()
        if '@f' in vars_present:
            replacements['@f'] = cls.getfileName(context)
        if '@d' in vars_present:
            replacements['@d'] = cls.getDateName()
        if '@i' in vars_present:
            replacements['@i'] = cls.getTimeName()
        if '@r' in vars_present:
            replacements['@r'] = cls.getRandomString()
        if '@h' in vars_present:
            replacements['@h'] = cls.get_high_variable()
        if '@l' in vars_present:
            replacements['@l'] = cls.get_low_variable()
        if '@b' in vars_present:
            replacements['@b'] = cls.get_cage_variable()
        if '@u1' in vars_present:
            replacements['@u1'] = cls.getuser1()
        if '@u2' in vars_present:
            replacements['@u2'] = cls.getuser2()
        if '@u3' in vars_present:
            replacements['@u3'] = cls.getuser3()
        if '@a' in vars_present:
            replacements['@a'] = cls.getActive(context)

        if wm.renaming_object_types == 'OBJECT':
            if '@o' in vars_present:
                replacements['@o'] = cls.getObject(entity)
            if '@t' in vars_present:
                replacements['@t'] = cls.getType(entity)
            if '@p' in vars_present:
                replacements['@p'] = cls.getParent(entity)
            if '@m' in vars_present:
                replacements['@m'] = cls.getData(entity)
            if '@c' in vars_present:
                replacements['@c'] = cls.getCollection(entity)

        if wm.renaming_object_types in (
            'UVMAPS', 'MATERIAL', 'BONE', 'MODIFIERS', 'SHAPEKEYS',
            'VERTEXGROUPS', 'PARTICLESYSTEM', 'COLORATTRIBUTES', 'ATTRIBUTES',
        ):
            owner_obj = bpy.data.objects.get(cls.getOwnerObjectName(entity))
            if owner_obj is not None:
                if '@o' in vars_present:
                    replacements['@o'] = owner_obj.name
                if '@t' in vars_present:
                    replacements['@t'] = cls.getType(owner_obj)
                if '@p' in vars_present:
                    replacements['@p'] = cls.getParent(owner_obj)
                if '@m' in vars_present:
                    replacements['@m'] = cls.getData(owner_obj)
                if '@c' in vars_present:
                    replacements['@c'] = cls.getCollection(owner_obj)

        if wm.renaming_object_types == 'NODE_GROUPS':
            if '@t' in vars_present:
                replacements['@t'] = cls.getType(entity)

        if wm.renaming_object_types == 'IMAGE':
            if '@r' in vars_present:
                replacements['@r'] = 'RESOLUTION'
            if '@i' in vars_present:
                replacements['@i'] = 'FILETYPE'

        return _VARIABLE_RE.sub(lambda m: replacements.get(m.group(), m.group()), inputText)

    @staticmethod
    def getRandomString():
        """Generate a Random String with the length of 6"""
        return generate_random_string(6)

    @classmethod
    def get_high_variable(cls):
        """Get High Poly identifier string"""
        return cls.addon_prefs.renaming_stringHigh

    @classmethod
    def get_low_variable(cls):
        """Get Low Poly identifier string"""
        return cls.addon_prefs.renaming_stringLow

    @classmethod
    def get_cage_variable(cls):
        """Get baking cage identifier string"""
        return cls.addon_prefs.renaming_stringCage

    @classmethod
    def getuser1(cls):
        return cls.addon_prefs.renaming_user1

    @classmethod
    def getuser2(cls):
        return cls.addon_prefs.renaming_user2

    @classmethod
    def getuser3(cls):
        return cls.addon_prefs.renaming_user3

    @classmethod
    def getPrefString(cls, suffixString):
        method = getattr(cls, suffixString, lambda: "Undefined variable")
        return method()

    @classmethod
    def getNumber(cls):
        new_nr = cls.number
        step = cls.step
        start_num = cls.start_number
        nr = str('{num:{fill}{width}}'.format(num=(new_nr * step) + start_num, fill='0', width=cls.digits))
        cls.number = new_nr + 1
        return nr

    @classmethod
    def getfileName(cls, context):
        if bpy.data.is_saved:
            filename = bpy.path.display_name(context.blend_data.filepath)
        else:
            filename = "UNSAVED"
            context.scene.renaming_error_messages.add_message(
                "@f variable: file is unsaved, replaced with 'UNSAVED'", isError=False
            )
        return filename

    @classmethod
    def getDateName(cls):
        date_format = cls.addon_prefs.date_format if cls.addon_prefs else "%d%b%Y"
        return time.strftime(date_format, time.localtime())

    @classmethod
    def getTimeName(cls):
        time_format = cls.addon_prefs.time_format if cls.addon_prefs else "%H%M"
        return time.strftime(time_format, time.localtime())

    @classmethod
    def getActive(cls, context):
        if context.object is None:
            return ""
        else:
            return context.object.name

    # OBJECTS
    @classmethod
    def getObject(cls, entity):
        obj_name = entity.name
        return obj_name

    @classmethod
    def getType(cls, entity):
        if entity is None:
            return "NO_TYPE"
        try:
            return str(entity.type)
        except AttributeError:
            return "NO_TYPE"

    @classmethod
    def getParent(cls, entity):
        if entity is None:
            return "NO_PARENT"
        try:
            if entity.parent is not None:
                return str(entity.parent.name)
            else:
                return entity.name
        except AttributeError:
            return "NO_PARENT"

    @classmethod
    def getData(cls, entity):
        if entity is None:
            return "NO_DATA"
        try:
            if entity.data is not None:
                return str(entity.data.name)
            else:
                return entity.name
        except AttributeError:
            return "NO_DATA"

    @classmethod
    def getCollection(cls, entity):
        """O(1) lookup using cache built by prepare()."""
        return cls._collection_cache.get(entity.name, "")

    @classmethod
    def getOwnerObjectName(cls, entity):
        """Find the owner object name using caches built by prepare()."""
        id_data = getattr(entity, 'id_data', None)
        if id_data is None:
            return ""

        # Modifier, vertex group, particle system, pose bone — id_data is the Object directly
        if id_data.bl_rna.identifier == 'Object':
            return id_data.name

        # Shape key — id_data is a Key datablock
        if id_data.bl_rna.identifier == 'Key':
            return cls._shape_key_to_obj.get(id(id_data), "")

        # Material — search by material name
        if id_data.bl_rna.identifier == 'Material':
            return cls._material_to_obj.get(id_data.name, "")

        # UV layer, bone — id_data is a Mesh or Armature datablock
        return cls._mesh_arm_to_obj.get(id(id_data), "")
