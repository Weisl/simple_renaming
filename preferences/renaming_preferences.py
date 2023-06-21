import bpy
from bpy.props import (
    EnumProperty,
    StringProperty,
)

from ..ui.renaming_panels import VIEW3D_PT_tools_renaming_panel, VIEW3D_PT_tools_type_suffix
from ..vallidation.renaming_vallidate import VIEW3D_PT_vallidation
from .renaming_keymap import draw_keymap_items


def update_panel_category(self, context):
    is_panel = hasattr(bpy.types, 'VIEW3D_PT_tools_renaming_panel')
    if is_panel:
        try:
            bpy.utils.unregister_class(VIEW3D_PT_tools_renaming_panel)
        except:
            pass

    is_panel = hasattr(bpy.types, 'VIEW3D_PT_tools_type_suffix')
    VIEW3D_PT_tools_renaming_panel.bl_category = context.preferences.addons[__package__].preferences.renaming_category
    bpy.utils.register_class(VIEW3D_PT_tools_renaming_panel)

    if is_panel:
        try:
            bpy.utils.unregister_class(VIEW3D_PT_tools_type_suffix)
        except:
            pass
    VIEW3D_PT_tools_type_suffix.bl_category = context.preferences.addons[__package__].preferences.renaming_category
    bpy.utils.register_class(VIEW3D_PT_tools_type_suffix)
    return


def update_panel_category_vallidation(self, context):
    is_panel = hasattr(bpy.types, 'VIEW3D_PT_vallidation')

    if is_panel:
        try:
            bpy.utils.unregister_class(VIEW3D_PT_vallidation)
        except:
            pass

    VIEW3D_PT_vallidation.bl_category = context.preferences.addons[__package__].preferences.vallidation_category
    bpy.utils.register_class(VIEW3D_PT_vallidation)
    return


def toggle_validation_panel(self, context):
    if self.renaming_show_validation:
        bpy.utils.register_class(VIEW3D_PT_vallidation)
    else:
        bpy.utils.unregister_class(VIEW3D_PT_vallidation)
    return


# addon Preferences
class VIEW3D_OT_renaming_preferences(bpy.types.AddonPreferences):
    """Contains the blender addon preferences"""
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__  ### __package__ works on multifile and __name__ not

    prefs_tabs: EnumProperty(items=(('ui', "General", "General Settings"),
                                    ('keymaps', "Keymaps", "Keymaps"),
                                    # ('validate', "Validate", "Validate (experimental)")
                                    ),
                             default='ui')

    renaming_category: StringProperty(name="Category",
                                      description="Defines in which category of the tools panel the simple renaimg panel is listed",
                                      default='Rename', update=update_panel_category)

    renaming_separator: StringProperty(
        name="Separator",
        description="Defines the separator between different operations",
        default='_',
    )

    renamingPanel_showPopup: bpy.props.BoolProperty(
        name="Show Popup",
        description="Enable or Disable Popup",
        default=True,
    )
    numerate_start_number: bpy.props.IntProperty(
        name="Numerate Start",
        description="Defines the first number for iterating objects. E.g., 1 means that the first object will be named [objectname]001",
        default=1,
    )

    numerate_digits: bpy.props.IntProperty(
        name="Digits",
        description="Defines digits used for numerating. Number 1 with digits 3 would result in 001",
        default=3,
    )
    numerate_step: bpy.props.IntProperty(
        name="Numerate Step",
        description="Defines the steps between numbers. E.g., 1 results in 1, 2, 3, a step siye ot two results in 1,3,5",
        default=1,
    )

    renaming_stringHigh: StringProperty(
        name="High",
        description="",
        default="high",
        # update = update_panel_position,
    )
    renaming_stringLow: StringProperty(
        name="Low",
        description="",
        default='low',
        # update = update_panel_position,
    )
    renaming_stringCage: StringProperty(
        name="Cage",
        description="",
        default='cage',
        # update = update_panel_position,
    )
    renaming_user1: StringProperty(
        name="User 1",
        description="",
        default='',
        # update = update_panel_position,
    )
    renaming_user2: StringProperty(
        name="User 2",
        description="",
        default='',
        # update = update_panel_position,
    )
    renaming_user3: StringProperty(
        name="User 3",
        description="",
        default='',
        # update = update_panel_position,
    )

    renaming_show_validation: bpy.props.BoolProperty(
        name="Use Validation Panel",
        description="Enable or Disable Validation Panel",
        default=False,
        update=toggle_validation_panel)

    vallidation_category: StringProperty(name="Category",
                                         description="Defines in which category of the tools panel the simple renaimg vallidation panel is listed",
                                         default='Rename',
                                         update=update_panel_category_vallidation)  # update = update_panel_position,

    regex_Mesh: bpy.props.StringProperty(
        name="Naming Regex",
        description="",
        default='r"^[A-Za-z]{2}_[A-Za-z]{6}_[A-Za-z0-9]+(_[A-Za-z0-9]+)?$"',
    )

    assetRegex: bpy.props.StringProperty(
        name="Asset Regex",
        description="",
        default='r"^[A-Za-z]+(_[A-Za-z0-9]+)?$"',
    )
    materialRegex: bpy.props.StringProperty(
        name="Material Regex",
        description="",
        default='r"^[A-Za-z](_mat|_main_mat)?$"',
    )
    genericMaterialRegex: bpy.props.StringProperty(
        name="Generic Material Regex",
        description="",
        default='r"^Gen[A-Za-z]+_mat"',
    )

    socketPrefix: bpy.props.StringProperty(
        name="Socket Prefix",
        description="",
        default="SOCKET_",
    )

    props_general = [
        "renaming_category",
        "renamingPanel_showPopup",
    ]
    props_naming = [
        "renaming_separator",
        "numerate_digits",
    ]
    props_numerate = [
        "numerate_start_number",
        "numerate_step",
    ]

    props_user_variables = [
        "renaming_stringLow",
        "renaming_stringHigh",
        "renaming_stringCage",
        "renaming_user1",
        "renaming_user2",
        "renaming_user3"
    ]

    def draw(self, context):
        '''
        simple preference UI to define custom inputs and user preferences
        '''
        layout = self.layout
        wm = context.window_manager

        row = layout.row(align=True)
        row.prop(self, "prefs_tabs", expand=True)

        if self.prefs_tabs == 'ui':
            for propName in self.props_general:
                row = layout.row()
                row.prop(self, propName)

            box = layout.box()
            row = box.row()
            row.label(text='Naming')
            for propName in self.props_naming:
                row = box.row()
                row.prop(self, propName)

            box = layout.box()
            row = box.row()
            row.label(text='Numerate')
            for propName in self.props_numerate:
                row = box.row()
                row.prop(self, propName)

            box = layout.box()
            row = box.row()
            row.label(text='User Variables')
            for propName in self.props_user_variables:
                row = box.row()
                row.prop(self, propName)

        if self.prefs_tabs == 'keymaps':
            draw_keymap_items(wm, layout)

        if self.prefs_tabs == 'validate':
            box = layout.box()
            row = box.row()
            row.prop(self, "renaming_show_validation", expand=True)
            row = box.row()
            row.prop(self, "vallidation_category", expand=True)
            row = box.row()
            row.prop(self, "regex_Mesh", expand=True)
            row = box.row()
            row.prop(self, "assetRegex", expand=True)
            row = box.row()
            row.prop(self, "materialRegex", expand=True)
            row = box.row()
            row.prop(self, "genericMaterialRegex", expand=True)


