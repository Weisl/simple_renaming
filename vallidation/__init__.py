from .renaming_vallidate import VIEW3D_PT_vallidation, VIEW3D_OT_Validate

classes = (
    VIEW3D_OT_Validate,
    VIEW3D_PT_vallidation,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
