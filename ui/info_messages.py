class MESSAGE:
    """messages parent class"""
    message = []

    @classmethod
    def add_message(cls):
        return

    @classmethod
    def get_messages(cls):
        return cls.message

    @classmethod
    def print_all(cls):
        print("Print All " + str(list(cls.message)))
        return

    @classmethod
    def clear(cls):
        cls.message = []

    @classmethod
    def draw(cls, context):
        return


class INFO_MESSAGES(MESSAGE):
    """Custom info messages"""

    @classmethod
    def add_message(cls, assetName, message='', obType=False, obIcon=False):
        message_dict = {'assetName': assetName, 'message': message, 'obType': obType, 'obIcon': obIcon}
        cls.message.append(message_dict)
        return


class WarningError_MESSAGES(MESSAGE):
    """Custom error warning messages"""

    @classmethod
    def add_message(cls, message='', isError=False):
        message_dict = {'message': message, 'isError': isError}
        cls.message.append(message_dict)
        return


class RENAMING_MESSAGES(MESSAGE):
    """Custom renaming messages"""
    message = []

    @classmethod
    def add_message(cls, oldName, new_name=None, obType=False, obIcon=False, warning=False):
        message_dict = {'oldName': oldName, 'new_name': new_name, 'obType': obType, 'obIcon': obIcon, 'warning': warning}
        cls.message.append(message_dict)
        return
