import random
import re
import string
import time

import bpy

from .. import __package__ as base_package


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
    def replaceInputString(cls, context, inputText, entity):

        """Replace custom variables with the according string"""
        wm = context.scene
        cls.addon_prefs = context.preferences.addons[base_package].preferences

        # System and Global Values #
        _f = cls.getfileName(context)
        inputText = re.sub(r'@f', lambda m: _f, inputText)  # file name
        _d = cls.getDateName()
        inputText = re.sub(r'@d', lambda m: _d, inputText)  # date
        _i = cls.getTimeName()
        inputText = re.sub(r'@i', lambda m: _i, inputText)  # time
        _r = cls.getRandomString()
        inputText = re.sub(r'@r', lambda m: _r, inputText)

        # UserStrings #
        _h = cls.get_high_variable()
        inputText = re.sub(r'@h', lambda m: _h, inputText)  # high
        _l = cls.get_low_variable()
        inputText = re.sub(r'@l', lambda m: _l, inputText)  # low
        _b = cls.get_cage_variable()
        inputText = re.sub(r'@b', lambda m: _b, inputText)  # cage
        _u1 = cls.getuser1()
        inputText = re.sub(r'@u1', lambda m: _u1, inputText)
        _u2 = cls.getuser2()
        inputText = re.sub(r'@u2', lambda m: _u2, inputText)
        _u3 = cls.getuser3()
        inputText = re.sub(r'@u3', lambda m: _u3, inputText)

        # GetScene #
        _a = cls.getActive(context)
        inputText = re.sub(r'@a', lambda m: _a, inputText)  # active object
        _n = cls.getNumber()
        inputText = re.sub(r'@n', lambda m: _n, inputText)

        if wm.renaming_object_types == 'OBJECT':
            # Objects
            _o = cls.getObject(entity)
            inputText = re.sub(r'@o', lambda m: _o, inputText)  # object
            _t = cls.getType(entity)
            inputText = re.sub(r'@t', lambda m: _t, inputText)  # type
            _p = cls.getParent(entity)
            inputText = re.sub(r'@p', lambda m: _p, inputText)  # parent
            _m = cls.getData(entity)
            inputText = re.sub(r'@m', lambda m: _m, inputText)  # data
            _c = cls.getCollection(entity)
            inputText = re.sub(r'@c', lambda m: _c, inputText)  # collection

        # IMAGES #
        if wm.renaming_object_types == 'IMAGE':
            inputText = re.sub(r'@r', lambda m: 'RESOLUTION', inputText)
            inputText = re.sub(r'@i', lambda m: 'FILETYPE', inputText)

        return inputText

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
        scn = context.scene

        if bpy.data.is_saved:
            filename = bpy.path.display_name(context.blend_data.filepath)
        else:
            filename = "UNSAVED"
            # scn.renaming_messages.add_message(oldName, entity.name)
        return filename

    @classmethod
    def getDateName(cls):
        t = time.localtime()
        t = time.mktime(t)
        return time.strftime("%d%b%Y", time.gmtime(t))

    @classmethod
    def getTimeName(cls):
        t = time.localtime()
        t = time.mktime(t)
        return time.strftime("%H:%M", time.gmtime(t))

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
        return str(entity.type)

    @classmethod
    def getParent(cls, entity):
        if entity.parent is not None:
            return str(entity.parent.name)
        else:
            return entity.name

    @classmethod
    def getData(cls, entity):
        if entity.data is not None:
            return str(entity.data.name)
        else:
            return entity.name

    @classmethod
    def getCollection(cls, entity):

        collectionew_names = ""
        for collection in bpy.data.collections:
            collection_objects = collection.objects
            if entity.name in collection.objects and entity in collection_objects[:]:
                collectionew_names += collection.name

        return collectionew_names
