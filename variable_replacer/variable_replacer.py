import random
import re
import string
import time

import bpy


def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


class VariableReplacer():
    '''This class is responsible for the custom variables'''
    addon_prefs = None
    entity = None
    number = 1
    digits = 3
    step = 1
    startnumber = 0

    @classmethod
    def reset(cls):
        '''reset all values to initial state'''
        prefs = bpy.context.preferences.addons[__package__.split('.')[0]].preferences
        startNum = prefs.numerate_start_number
        numerate_step = prefs.numerate_step
        numerate_digits = prefs.numerate_digits

        # print("reset = " + str(startNum))
        cls.step = numerate_step
        cls.digits = numerate_digits
        cls.startNum = startNum
        cls.number = 0

    @classmethod
    def replaceInputString(cls, context, inputText, entity):

        '''Replace custom variables with the according string'''
        wm = context.scene
        cls.addon_prefs = context.preferences.addons[__package__.split('.')[0]].preferences

        ##### System and Global Values ################
        inputText = re.sub(r'@f', cls.getfileName(context), inputText)  # file name
        inputText = re.sub(r'@d', cls.getDateName(context), inputText)  # date
        inputText = re.sub(r'@i', cls.getTimeName(context), inputText)  # time
        inputText = re.sub(r'@r', cls.getRandomString(context), inputText)

        ##### UserStrings ################
        inputText = re.sub(r'@h', cls.gethigh(), inputText)  # high
        inputText = re.sub(r'@l', cls.getlow(), inputText)  # low
        inputText = re.sub(r'@b', cls.getcage(), inputText)  # cage
        inputText = re.sub(r'@u1', cls.getuser1(), inputText)
        inputText = re.sub(r'@u2', cls.getuser2(), inputText)
        inputText = re.sub(r'@u3', cls.getuser3(), inputText)

        ##### GetScene ################
        inputText = re.sub(r'@a', cls.getActive(context), inputText)  # active object
        inputText = re.sub(r'@n', cls.getNumber(context), inputText)

        if wm.renaming_object_types == 'OBJECT':
            ##### Objects #################
            inputText = re.sub(r'@o', cls.getObject(context, entity), inputText)  # object
            inputText = re.sub(r'@t', cls.getType(context, entity), inputText)  # type
            inputText = re.sub(r'@p', cls.getParent(context, entity), inputText)  # parent
            inputText = re.sub(r'@m', cls.getData(context, entity), inputText)  # data
            inputText = re.sub(r'@c', cls.getCollection(context, entity), inputText)  # collection

        ###### IMAGES ###########
        if wm.renaming_object_types == 'IMAGE':
            inputText = re.sub(r'@r', 'RESOLUTION', inputText)
            inputText = re.sub(r'@i', 'FILETYPE', inputText)

        return inputText

    @classmethod
    def gethigh(cls):
        '''Get High Poly identifier string'''
        return cls.addon_prefs.renaming_stringHigh

    @classmethod
    def getlow(cls):
        '''Get Low Poly identifier string'''
        return cls.addon_prefs.renaming_stringLow

    @classmethod
    def getcage(cls):
        '''Get baking cage identifier string'''
        return cls.addon_prefs.renaming_stringCage

    # @classmethod
    def getRandomString(cls):
        '''Generate a Random String with the length of 6'''
        return randomString(6)

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
    def getNumber(cls, context):
        wm = context.scene
        # digits = len(wm.renaming_numerate)
        newNr = cls.number
        step = cls.step
        startNum = cls.startNum
        nr = str('{num:{fill}{width}}'.format(num=(newNr * step) + startNum, fill='0', width=cls.digits))
        cls.number = newNr + 1
        return nr

    @classmethod
    def getfileName(cls, context):
        scn = context.scene

        if bpy.data.is_saved:
            filename = bpy.path.display_name(context.blend_data.filepath)
        else:
            filename = "UNSAVED"
            # scn.renaming_messages.addMessage(oldName, entity.name)
            # TODO: Error message! is unsaved
        return filename

    @classmethod
    def getDateName(cls, context):
        # Todo: Specify Date Layout in preferences
        # TODO: Fix Timezone
        t = time.localtime()
        t = time.mktime(t)
        return time.strftime("%d%b%Y", time.gmtime(t))

    @classmethod
    def getTimeName(cls, context):
        # TODO: Specify Time Layout in preferences
        t = time.localtime()
        t = time.mktime(t)
        return time.strftime("%H:%M", time.gmtime(t))

    @classmethod
    def getActive(cls, context):
        if context.object is None:
            return ""
        else:
            return context.object.name

    ################## OBJECTS ####################################
    @classmethod
    def getObject(cls, context, entity):
        objName = entity.name
        return objName

    @classmethod
    def getType(cls, context, entity):
        # TODO: Error Case
        # TODO: Per Object
        return str(entity.type)

    @classmethod
    def getParent(cls, context, entity):
        # TODO: Error Case
        if entity.parent is not None:
            return str(entity.parent.name)
        else:
            return entity.name

    @classmethod
    def getData(cls, context, entity):
        # TODO: Error Case
        if entity.data is not None:
            return str(entity.data.name)
        else:
            return entity.name

    @classmethod
    def getCollection(cls, context, entity):
        # prefs = context.preferences.addons[__package__.split('.')[0]].preferences
        # separator = prefs.renaming_separator

        collectionNames = ""
        for collection in bpy.data.collections:
            collection_objects = collection.objects
            if entity.name in collection.objects and entity in collection_objects[:]:
                collectionNames += collection.name

        return collectionNames
