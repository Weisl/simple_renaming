from . import renaming_keymap
from . import renaming_preferences
from . import keymap
classes = (
    renaming_keymap.RENAMING_OT_add_hotkey_renaming,
    renaming_preferences.VIEW3D_OT_renaming_preferences,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    keymap.add_keymap()


def unregister():
    keymap.remove_keymap()

    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
