class MESSAGE():
    '''messages parent class'''
    message = []

    @classmethod
    def addMessage(cls):
        return

    @classmethod
    def getMessages(cls):
        return cls.message

    @classmethod
    def printAll(cls):
        print("Print All " + str(list(cls.message)))
        return

    @classmethod
    def clear(cls):
        cls.message = []

    @classmethod
    def draw(cls, context):
        return


class INFO_MESSAGES(MESSAGE):
    '''Custom info messages'''

    @classmethod
    def addMessage(cls, assetName, message='', obType=False, obIcon=False):
        dict = {'assetName': assetName, 'message': message, 'obType': obType, 'obIcon': obIcon}
        cls.message.append(dict)
        return


class WarningError_MESSAGES(MESSAGE):
    '''Custom error warning messages'''

    @classmethod
    def addMessage(cls, message='', isError=False):
        dict = {'message': message, 'isError': isError}
        cls.message.append(dict)
        return


class RENAMING_MESSAGES(MESSAGE):
    '''Custom renaming messages'''
    message = []

    @classmethod
    def addMessage(cls, oldName, newName=None, obType=False, obIcon=False, warning=False):
        dict = {'oldName': oldName, 'newName': newName, 'obType': obType, 'obIcon': obIcon, 'warning': warning}
        cls.message.append(dict)
        return


