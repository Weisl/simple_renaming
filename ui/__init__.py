from .renaming_proFeatures import RENAMING_MT_variableMenu, VIEW3D_OT_inputVariables
from .renaming_panels import VIEW3D_PT_tools_renaming_panel,VIEW3D_PT_tools_type_suffix,VIEW3D_OT_SetVariable,VIEW3D_OT_RenamingPopupOperator, OBJECT_MT_sufpre_presets, AddPresetRenamingPresets
from .renaming_popup import VIEW3D_PT_renaming_popup, VIEW3D_PT_info_popup, VIEW3D_PT_error_popup
from .ui_helpers import PREFERENCES_OT_open_addon

from .renaming_panels import panel_func

from .info_messages import RENAMING_MESSAGES,WarningError_MESSAGES,INFO_MESSAGES
import bpy

classes = (
    RENAMING_MT_variableMenu,
    VIEW3D_OT_inputVariables,
    VIEW3D_PT_error_popup,
    VIEW3D_PT_info_popup,
    VIEW3D_PT_renaming_popup,
    OBJECT_MT_sufpre_presets,
    AddPresetRenamingPresets,
    VIEW3D_PT_tools_renaming_panel,
    VIEW3D_PT_tools_type_suffix,
    VIEW3D_OT_SetVariable,
    VIEW3D_OT_RenamingPopupOperator,
    PREFERENCES_OT_open_addon,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

    bpy.types.VIEW3D_PT_tools_type_suffix.prepend(panel_func)

    IDStore = bpy.types.Scene

    IDStore.renaming_messages = RENAMING_MESSAGES()
    IDStore.renaming_error_messages = WarningError_MESSAGES()
    IDStore.renaming_info_messages = INFO_MESSAGES()

def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)

    IDStore = bpy.types.Scene
    del IDStore.renaming_messages
    del IDStore.renaming_error_messages
    del IDStore.renaming_info_messages
