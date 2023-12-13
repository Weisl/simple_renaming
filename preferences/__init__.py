from . import renaming_keymap
from . import renaming_preferences

classes = (
    renaming_preferences.VIEW3D_OT_renaming_preferences,
    renaming_keymap.RENAMING_OT_add_hotkey_renaming,
    renaming_keymap.REMOVE_OT_hotkey,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    renaming_keymap.add_keymap()


def unregister():

    renaming_keymap.remove_keymap()

    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
