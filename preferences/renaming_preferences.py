import bpy
import textwrap
from bpy.props import (
    EnumProperty,
    StringProperty,
)

from ..ui.renaming_panels import VIEW3D_PT_tools_renaming_panel, VIEW3D_PT_tools_type_suffix
#from ..vallidation.renaming_vallidate import VIEW3D_PT_vallidation
from .renaming_keymap import remove_key

def label_multiline(context, text, parent):
    chars = int(context.region.width / 7)  # 7 pix on 1 character
    wrapper = textwrap.TextWrapper(width=chars)
    text_lines = wrapper.wrap(text=text)
    for text_line in text_lines:
        parent.label(text=text_line)


def add_key(km, idname, properties_name, button_assignment_type, button_assignment_ctrl, button_assignment_shift,
            button_assignment_alt, button_assignment_active):
    kmi = km.keymap_items.new(idname=idname, type=button_assignment_type, value='PRESS',
                              ctrl=button_assignment_ctrl, shift=button_assignment_shift, alt=button_assignment_alt)
    kmi.properties.name = properties_name
    kmi.active = button_assignment_active


def update_key(context, operation, operator_name, property_prefix):
    # This functions gets called when the hotkey assignment is updated in the preferences
    wm = context.window_manager
    km = wm.keyconfigs.addon.keymaps["Window"]

    prefs = context.preferences.addons[__package__.split('.')[0]].preferences

    # Remove previous key assignment
    remove_key(context, operation, operator_name)

    add_key(km, operation, operator_name, getattr(prefs, f'{property_prefix}_type'),
            getattr(prefs, f'{property_prefix}_ctrl'), getattr(prefs, f'{property_prefix}_shift'),
            getattr(prefs, f'{property_prefix}_alt'), getattr(prefs, f'{property_prefix}_active'))


def update_renaming_key(self, context):
    update_key(context, 'wm.call_panel', "VIEW3D_PT_tools_renaming_panel", "renaming_panel")


def update_suf_pre_key(self, context):
    update_key(context, 'wm.call_panel', "VIEW3D_PT_tools_type_suffix", "renaming_suf_pre")


def update_panel_category(self, context):
    '''Update panel tab for collider tools'''

    panels = [
        VIEW3D_PT_tools_renaming_panel,
        VIEW3D_PT_tools_type_suffix,
    ]

    for panel in panels:
        try:
            bpy.utils.unregister_class(panel)
        except:
            pass

        prefs = context.preferences.addons[__package__.split('.')[0]].preferences
        panel.bl_category = prefs.renaming_category
        bpy.utils.register_class(panel)
    return


# def update_vallidate_panel_category(self, context):
#     '''Update panel tab for collider tools'''
#
#     panels = [
#         VIEW3D_PT_vallidation,
#     ]
#
#     for panel in panels:
#         try:
#             bpy.utils.unregister_class(panel)
#         except:
#             pass
#
#         prefs = context.preferences.addons[__package__.split('.')[0]].preferences
#         panel.bl_category = prefs.vallidation_category
#         bpy.utils.register_class(panel)
#     return


# def toggle_validation_panel(self, context):
#     if self.renaming_show_validation:
#         bpy.utils.register_class(VIEW3D_PT_vallidation)
#     else:
#         bpy.utils.unregister_class(VIEW3D_PT_vallidation)
#     return


# addon Preferences
class VIEW3D_OT_renaming_preferences(bpy.types.AddonPreferences):
    """Contains the blender addon preferences"""
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__.split('.')[0]
    bl_options = {'REGISTER'}

    prefs_tabs: EnumProperty(items=(('UI', "General", "General Settings"),
                                    ('KEYMAPS', "Keymaps", "Keymaps"),
                                    # ('VALIDATE', "Validate", "Validate"),
                                    ('SUPPORT', "Support", "Support")),
                             default='UI')

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

    renamingPanel_useObjectOrder: bpy.props.BoolProperty(
        name="Use Selection Order",
        description="Use the order of selection when renaming objects",
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

    # renaming_show_validation: bpy.props.BoolProperty(
    #     name="Use Name Validation",
    #     description="Enable or Disable Validation Panel",
    #     default=False,
    #     update=toggle_validation_panel)

    # vallidation_category: StringProperty(name="Category",
    #                                      description="Defines in which category of the tools panel the simple renaimg vallidation panel is listed",
    #                                      default='Rename',
    #                                      update=update_vallidate_panel_category)  # update = update_panel_position,
    #

    regex_Mesh: bpy.props.StringProperty(
        name="Naming Regex",
        description="",
        default='r"^[A-Za-z_]"',
    )

    materialRegex: bpy.props.StringProperty(
        name="Material Regex",
        description="",
        default='r"^[A-Za-z_](_mat)?$""',
    )


    props_general = [
        "renaming_category",
        "renamingPanel_showPopup",
        "renamingPanel_useObjectOrder",
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

    vallidation_variables = [
        "regex_Mesh",
        "materialRegex",
    ]

    renaming_panel_type: bpy.props.StringProperty(
        name="Renaming Popup",
        default="F2",
        update=update_renaming_key
    )

    renaming_panel_ctrl: bpy.props.BoolProperty(
        name="Ctrl",
        default=True,
        update=update_renaming_key
    )

    renaming_panel_shift: bpy.props.BoolProperty(
        name="Shift",
        default=True,
        update=update_renaming_key
    )
    renaming_panel_alt: bpy.props.BoolProperty(
        name="Alt",
        default=False,
        update=update_renaming_key
    )

    renaming_panel_active: bpy.props.BoolProperty(
        name="Active",
        default=True,
        update=update_renaming_key
    )

    renaming_suf_pre_type: bpy.props.StringProperty(
        name="Renaming Popup",
        default="F2",
        update=update_suf_pre_key
    )

    renaming_suf_pre_ctrl: bpy.props.BoolProperty(
        name="Ctrl",
        default=True,
        update=update_suf_pre_key
    )

    renaming_suf_pre_shift: bpy.props.BoolProperty(
        name="Shift",
        default=False,
        update=update_suf_pre_key
    )
    renaming_suf_pre_alt: bpy.props.BoolProperty(
        name="Alt",
        default=True,
        update=update_suf_pre_key
    )

    renaming_suf_pre_active: bpy.props.BoolProperty(
        name="Active",
        default=True,
        update=update_suf_pre_key
    )

    def keymap_ui(self, layout, title, property_prefix, id_name, properties_name):
        box = layout.box()
        split = box.split(align=True, factor=0.5)
        col = split.column()

        # Is hotkey active checkbox
        row = col.row(align=True)
        row.prop(self, f'{property_prefix}_active', text="")
        row.label(text=title)

        # Button to assign the key assignments
        col = split.column()
        row = col.row(align=True)
        key_type = getattr(self, f'{property_prefix}_type')
        text = (
            bpy.types.Event.bl_rna.properties['type'].enum_items[key_type].name
            if key_type != 'NONE'
            else 'Press a key'
        )

        op = row.operator("rename.key_selection_button", text=text)
        op.property_prefix = property_prefix
        # row.prop(self, f'{property_prefix}_type', text="")
        op = row.operator("rename.remove_hotkey", text="", icon="X")
        op.idname = id_name
        op.properties_name = properties_name
        op.property_prefix = property_prefix

        row = col.row(align=True)
        row.prop(self, f'{property_prefix}_ctrl')
        row.prop(self, f'{property_prefix}_shift')
        row.prop(self, f'{property_prefix}_alt')

    def draw(self, context):
        '''
        simple preference UI to define custom inputs and user preferences
        '''
        layout = self.layout
        wm = context.window_manager

        row = layout.row(align=True)
        row.prop(self, "prefs_tabs", expand=True)

        # Genral settings regarding renaming
        if self.prefs_tabs == 'UI':
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

        # Settings regarding the keymap
        if self.prefs_tabs == 'KEYMAPS':
          
            self.keymap_ui(layout, 'Renaming Panel', 'renaming_panel',
                           'wm.call_panel', "VIEW3D_PT_tools_renaming_panel")
            self.keymap_ui(layout, 'Renaming Sub/Prefix', 'renaming_suf_pre',
                           'wm.call_panel', "VIEW3D_PT_tools_type_suffix")

        # Settings regarding the vallidation.
        if self.prefs_tabs == 'VALIDATE':
            row = layout.row()
            row.prop(self, "renaming_show_validation", expand=True)
            row = layout.row()
            row.prop(self, "vallidation_category", expand=True)

            box = layout.box()
            for propName in self.vallidation_variables:
                row = box.row()
                row.prop(self, propName)

        elif self.prefs_tabs == 'VALIDATE':
            box = layout.box()

            row = box.row()
            row.label(text="Vallidation Regex")
            row = box.row()
            row.prop(self, "regex_Mesh", expand=True)
            row = box.row()
            row.prop(self, "materialRegex", expand=True)


        elif self.prefs_tabs == 'SUPPORT':
            text = "Support me developing great tools!"
            label_multiline(
                context=context,
                text=text,
                parent=layout
            )
            box = layout.box()
            text = "Check out my other Blender Addons providing more efficient workflows for game asset creation."
            label_multiline(
                context=context,
                text=text,
                parent=box
            )
            box = layout.box()
            row = box.row()
            row.operator("wm.url_open", text="Collider Tools").url = "https://blendermarket.com/products/collider-tools"
            row = box.row()
            row.operator("wm.url_open", text="Cam-Manager").url = "https://blendermarket.com/products/cam-manager"

            box = layout.box()
            text = "Please support me by donating for this addon."
            label_multiline(
                context=context,
                text=text,
                parent=box
            )
            row = box.row()
            row.operator("wm.url_open", text="Gumroad").url = "https://weisl.gumroad.com/l/simple_renaming_panel"
            row = box.row()
            row.operator("wm.url_open", text="PayPal Donation").url = "https://www.paypal.com/donate?hosted_button_id=JV7KRF77TY78A"
            row = box.row()
            row.operator("wm.url_open", text="Blender Market").url = "https://blendermarket.com/products/simple-renaming-panel"




