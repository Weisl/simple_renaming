import bpy
from bl_operators.presets import AddPresetBase
from bpy.props import StringProperty
from bpy.types import Operator, Menu

from ..ui.renaming_variables import RENAMING_MT_variableMenu

# Selected objects are renamed directly
types_selected = ('OBJECT', 'ADDOBJECTS', 'BONE')

# Components of the selected objects are renamed
types_of_selected = (
    'MATERIAL', 'DATA', 'VERTEXGROUPS', 'PARTICLESYSTEM', 'SHAPEKEYS', 'MODIFIERS', 'UVMAPS',
    'COLORATTRIBUTES', 'ATTRIBUTES', 'ACTIONS')


def draw_renaming_panel(layout, context):
    scene = context.scene

    row = layout.row(align=True)
    row.label(text="Target")
    row = layout.row(align=True)
    row.prop(scene, "renaming_object_types", text="")

    # SELECTED
    if str(scene.renaming_object_types) == 'OBJECT':
        layout.prop(scene, "renaming_object_types_specified", expand=True)
    if str(scene.renaming_object_types) in types_of_selected:
        layout.prop(scene, "renaming_only_selection", text="Only Of Selected Objects")
    elif str(scene.renaming_object_types) in types_selected:
        layout.prop(scene, "renaming_only_selection", text="Only Selected")
    elif str(scene.renaming_object_types) == 'COLLECTION':
        if bpy.context.space_data.type == 'OUTLINER':
            row = layout.row(align=True)
            row.prop(scene, "renaming_only_selection", text="Only Selected")
        else:
            col = layout.column(align=True)
            row = col.row(align=True)
            row.enabled = False
            row.prop(scene, "renaming_only_selection", text="Only Selected")
            row = col.row(align=True)
            row.enabled = False
            row.label(text="Open from Outliner", icon="ERROR")

    box = layout
    # Sorting
    if str(scene.renaming_object_types) not in ['COLLECTION', 'IMAGE']:
        col = box.column(align=True)
        col.prop(scene, "renaming_sorting")
        if scene.renaming_sorting:
            if str(scene.renaming_object_types) == 'BONE':
                col.prop(scene, "renaming_sort_bone_enum", expand=True)
            else:
                col.prop(scene, "renaming_sort_enum", expand=True)
            col.prop(scene, "renaming_sort_reverse")

    layout.separator(type='LINE')
    layout.label(text="Rename")

    # NEW NAME
    col = layout.column(align=True)
    col.prop(scene, "renaming_use_enumerate")

    row = col.row(align=True)
    split = row.split(factor=0.6, align=True)
    split.prop(scene, "renaming_new_name", text='')
    split = split.split(factor=0.75, align=True)
    split.prop(scene, "renaming_numerate", text='')
    split.operator("object.renaming_set_variable", text="@").inputBox = "new_name"

    row = col.row()
    row.operator("renaming.name_replace", icon="FORWARD")

    # SEARCH REPLACE
    layout.separator()
    layout.label(text="Search and Replace")

    split = layout.split(factor=0.5, align=True)
    col_a = split.column(align=True)
    col_b = split.column(align=True)

    row = col_a.row(align=True)
    row.prop(scene, "renaming_useRegex")

    row = col_b.row(align=True)
    row.enabled = not scene.renaming_useRegex
    row.prop(scene, "renaming_matchcase")

    col = layout.column(align=True)
    split = col.split(factor=0.9, align=True)
    split.prop(scene, "renaming_search", text='Search')
    split.operator("object.renaming_set_variable", text="@").inputBox = "search"

    split = col.split(factor=0.9, align=True)
    split.prop(scene, "renaming_replace", text='Replace')
    split.operator("object.renaming_set_variable", text="@").inputBox = "replace"

    if scene.renaming_object_types == 'BONE':
        if context.mode == 'POSE' or context.mode == 'EDIT_ARMATURE':
            row = layout.row(align=True)
            row.operator("renaming.search_select", icon="RESTRICT_SELECT_OFF")

    elif scene.renaming_object_types == 'OBJECT':
        row = layout.row(align=True)
        row.operator("renaming.search_select", icon="RESTRICT_SELECT_OFF")

    row = layout.row(align=True)
    row.operator("renaming.search_replace", icon="FILE_REFRESH")

    ###############################################
    layout.separator()
    layout.label(text="Add Prefix and Suffix")

    # REFIX SUFFIX
    col = layout.column(align=True)
    split = col.split(factor=0.9, align=True)
    split.prop(scene, "renaming_prefix", text='')
    split.operator("object.renaming_set_variable", text="@").inputBox = "prefix"
    col.operator("renaming.add_prefix", icon="REW")

    col = layout.column(align=True)
    split = col.split(factor=0.9, align=True)
    split.prop(scene, "renaming_suffix", text='')
    split.operator("object.renaming_set_variable", text="@").inputBox = "suffix"
    col.operator("renaming.add_suffix", icon="FF")

    ###############################################
    layout.separator()
    layout.label(text="Other")

    row = layout.row(align=True)
    row.operator("renaming.numerate", icon="LINENUMBERS_ON")

    row = layout.row(align=True)
    row.operator("renaming.cut_string", icon="X")
    row.prop(scene, "renaming_cut_size", text="")

    if str(scene.renaming_object_types) in ('DATA', 'OBJECT', 'ADDOBJECTS'):
        layout.label(text="Data Name")

        col = layout.column(align=True)
        split = col.split(factor=0.9, align=True)
        split.prop(scene, "renaming_suffix_prefix_data_02", text='')
        split.operator("object.renaming_set_variable", text="@").inputBox = "dataFromObj"
        col.operator("renaming.data_name_from_obj", icon="MOD_DATA_TRANSFER")


def panel_func(self, context):
    layout = self.layout

    row = layout.row(align=True)
    row.menu('OBJECT_MT_suffix_prefix_presets', text=OBJECT_MT_suffix_prefix_presets.bl_label)
    row.operator(AddPresetRenamingPresets.bl_idname, text="", icon='ADD')
    row.operator(AddPresetRenamingPresets.bl_idname, text="", icon='REMOVE').remove_active = True


class VIEW3D_PT_tools_renaming_panel(bpy.types.Panel):
    """Creates a renaming Panel"""
    bl_label = "Simple Renaming"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Rename"

    def draw_header(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.operator("wm.url_open", text="", icon='HELP').url = "https://weisl.github.io/renaming/"
        addon_name = get_addon_name()

        op = row.operator("preferences.rename_addon_search", text="", icon='PREFERENCES')
        op.addon_name = addon_name
        op.prefs_tabs = 'UI'

    def draw(self, context):
        layout = self.layout
        draw_renaming_panel(layout, context)


# needed for adding direct link to settings
def get_addon_name():
    return "Simple Renaming"


# addon Panel
class VIEW3D_PT_tools_type_suffix(bpy.types.Panel):
    """Creates a renaming Panel"""
    bl_label = "Prefix/Suffix by Type"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Rename"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        scene = context.scene
        layout = self.layout

        layout.prop(scene, "type_pre_sub_only_selection", text="Only Selected Objects")
        layout.prop(scene, "renaming_suffix_prefix_type", expand=True)
        # layout.prop(scene, "renaming_suffix_prefix_types_specified")

        if scene.renaming_suffix_prefix_type == "PRE":
            layout.label(text="Add Type Prefix")
        else:
            layout.label(text="Add Type Suffix")

        split = layout.split()

        col = split.column()
        row = col.row()
        row.prop(scene, "renaming_suffix_prefix_empty", text="")
        row.operator("renaming.add_suffix_prefix_by_type", text="Empties").option = 'empty'

        row = col.row()
        row.prop(scene, "renaming_suffix_prefix_geometry", text="")
        row.operator('renaming.add_suffix_prefix_by_type', text="Meshes").option = 'mesh'

        row = col.row()
        row.prop(scene, "renaming_suffix_prefix_material", text="")
        row.operator('renaming.add_suffix_prefix_by_type', text="Materials").option = 'material'

        row = col.row()
        row.prop(scene, "renaming_suffix_prefix_curve", text="")
        row.operator('renaming.add_suffix_prefix_by_type', text="Curves").option = 'curve'

        row = col.row()
        row.prop(scene, "renaming_suffix_prefix_armature", text="")
        row.operator('renaming.add_suffix_prefix_by_type', text="Armatures").option = 'armature'

        row = col.row()
        row.prop(scene, "renaming_suffix_prefix_lattice", text="")
        row.operator('renaming.add_suffix_prefix_by_type', text="Lattices").option = 'lattice'

        row = col.row()
        row.prop(scene, "renaming_suffix_prefix_data", text="")
        row.operator('renaming.add_suffix_prefix_by_type', text="Data").option = 'data'

        row = col.row()
        row.prop(scene, "renaming_suffix_prefix_surfaces", text="")
        row.operator('renaming.add_suffix_prefix_by_type', text="Surfaces").option = 'surface'

        row = col.row()
        row.prop(scene, "renaming_suffix_prefix_cameras", text="")
        row.operator('renaming.add_suffix_prefix_by_type', text="Cameras").option = 'camera'

        row = col.row()
        row.prop(scene, "renaming_suffix_prefix_lights", text="")
        row.operator('renaming.add_suffix_prefix_by_type', text="Lights").option = 'light'

        row = col.row()
        row.prop(scene, "renaming_suffix_prefix_collection", text="")
        row.operator('renaming.add_suffix_prefix_by_type', text="Collections").option = 'collection'

        row = col.row()
        row.prop(scene, "renaming_suffix_prefix_text", text="")
        row.operator('renaming.add_suffix_prefix_by_type', text="Texts").option = 'text'

        row = col.row()
        row.prop(scene, "renaming_suffix_prefix_gpencil", text="")
        row.operator('renaming.add_suffix_prefix_by_type', text="Grease Pencil").option = 'gpencil'

        row = col.row()
        row.prop(scene, "renaming_suffix_prefix_metaball", text="")
        row.operator('renaming.add_suffix_prefix_by_type', text="Metaballs").option = 'metaball'

        row = col.row()
        row.prop(scene, "renaming_suffix_prefix_bone", text="")
        row.operator('renaming.add_suffix_prefix_by_type', text="Bones").option = 'bone'

        row = col.row()
        row.prop(scene, "renaming_suffix_prefix_speakers", text="")
        row.operator('renaming.add_suffix_prefix_by_type', text="Speakers").option = 'speakers'

        row = col.row()
        row.prop(scene, "renaming_suffix_prefix_lightprops", text="")
        row.operator('renaming.add_suffix_prefix_by_type', text="Light Probes").option = 'lightprops'

        row = col.row()
        row.operator('renaming.add_suffix_prefix_by_type', text="Rename All").option = 'all'


class VIEW3D_OT_SetVariable(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.renaming_set_variable"
    bl_label = "Simple Object Operator"

    inputBox: StringProperty()

    def execute(self, context):
        context.scene.renaming_inputContext = self.inputBox
        bpy.ops.wm.call_menu(name=RENAMING_MT_variableMenu.bl_idname)
        return {'FINISHED'}


class VIEW3D_OT_RenamingPopupOperator(bpy.types.Operator):
    bl_idname = "renaming.f_popup_operator"
    bl_label = "Simple Renaming"

    my_float: bpy.props.FloatProperty(name="Some Floating Point")
    my_bool: bpy.props.BoolProperty(name="Toggle Option")
    my_string: bpy.props.StringProperty(name="String Value")

    def execute(self, context):
        print("Dialog Runs")
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class OBJECT_MT_suffix_prefix_presets(Menu):
    bl_label = "Type Presets"
    preset_subdir = "scene/display"
    preset_operator = "script.execute_preset"
    draw = Menu.draw_preset


class AddPresetRenamingPresets(AddPresetBase, Operator):
    """Add an Object Display Preset"""
    bl_idname = "renaming.sufpreadd_presets"
    bl_label = "Add Renaming Preset"
    preset_menu = "OBJECT_MT_suffix_prefix_presets"

    # variable used for all preset values
    preset_defines = [
        "scene = bpy.context.scene"
    ]

    # properties to store in the preset
    preset_values = [
        "scene.renaming_suffix_prefix_empty",
        "scene.renaming_suffix_prefix_geometry",
        "scene.renaming_suffix_prefix_material",
        "scene.renaming_suffix_prefix_curve",
        "scene.renaming_suffix_prefix_armature",
        "scene.renaming_suffix_prefix_lattice",
        "scene.renaming_suffix_prefix_data",
        "scene.renaming_suffix_prefix_surfaces",
        "scene.renaming_suffix_prefix_cameras",
        "scene.renaming_suffix_prefix_lights",
        "scene.renaming_suffix_prefix_collection",
        "scene.renaming_suffix_prefix_text",
        "scene.renaming_suffix_prefix_gpencil",
        "scene.renaming_suffix_prefix_metaball",
        "scene.renaming_suffix_prefix_bone",
        "scene.renaming_suffix_prefix_speakers",
        "scene.renaming_suffix_prefix_lightprops",
    ]

    # where to store the preset
    preset_subdir = "scene/display"
