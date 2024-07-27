from .validation_operator import VIEW3D_OT_Validate

classes = (
    VIEW3D_OT_Validate,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
