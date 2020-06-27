import bpy
from bl_operators.presets import AddPresetBase
from bpy.props import StringProperty
from bpy.types import Operator, Menu

from .renaming_proFeatures import RENAMING_MT_variableMenu


def drawSimpleUi(self, context):
    layout = self.layout
    scene = context.scene

    split = layout.split(align=True, factor=0.3)
    split.label(text="Target")
    split.prop(scene, "renaming_object_types", text="")
    if str(scene.renaming_object_types) == 'OBJECT':
        layout.prop(scene, "renaming_object_types_specified", expand=True)
    # elif str(scene.renaming_object_types) == 'ADDOBJECTS':
    #    layout.prop(scene, "renaming_object_addtypes_specified", expand=True)

    # layout.use_property_split = False  # Activate single-column layout

    if str(scene.renaming_object_types) in ('MATERIAL', 'DATA'):
        layout.prop(scene, "renaming_only_selection", text="Only Of Selected Objects")
    elif str(scene.renaming_object_types) in ('OBJECT', 'ADDOBJECTS', 'BONE'):
        layout.prop(scene, "renaming_only_selection", text="Only Selected")

    layout.separator()

    ###############################################
    layout.label(text="Rename")

    row = layout.row(align=True)
    # row.scale_y = 1.5
    row.prop(scene, "renaming_newName", text="")
    row.operator("renaming.name_replace", icon="FORWARD")

    ###############################################
    row = layout.row(align=True)
    layout.label(text="Search and Replace")

    row = layout.row(align=True)
    if scene.renaming_useRegex == False:
        row = layout.row(align=True)
        row.prop(scene, "renaming_useRegex")
        row.prop(scene, "renaming_matchcase")
    else:
        layout.prop(scene, "renaming_useRegex")

    layout.prop(scene, "renaming_search")
    layout.prop(scene, "renaming_replace")

    if scene.renaming_object_types == 'BONE':
        if context.mode == 'POSE':
            row = layout.row(align=True)
            row.operator("renaming.search_select", icon="RESTRICT_SELECT_OFF")

    elif scene.renaming_object_types == 'OBJECT':
        row = layout.row(align=True)
        row.operator("renaming.search_select", icon="RESTRICT_SELECT_OFF")

    row = layout.row(align=True)
    row.operator("renaming.search_replace", icon="FILE_REFRESH")
    layout.separator()

    ###############################################
    layout.label(text="Other")

    ###############################################
    row = layout.row(align=True)
    row.prop(scene, "renaming_prefix", text="")
    row.operator("renaming.add_prefix", icon="REW")

    ###############################################
    row = layout.row(align=True)
    row.prop(scene, "renaming_suffix", text="")
    row.operator("renaming.add_suffix", icon="FF")

    ###############################################
    row = layout.row(align=True)
    # row.prop(scene, "renaming_digits_numerate", text="")
    row.operator("renaming.numerate", icon="LINENUMBERS_ON")

    ###############################################
    row = layout.row(align=True)
    row.prop(scene, "renaming_cut_size", text="")
    row.operator("renaming.cut_string", icon="X")

    if str(scene.renaming_object_types) in ('DATA', 'OBJECT', 'ADDOBJECTS'):
        row = layout.row(align=True)
        row.prop(scene, "renaming_sufpre_data_02", text="")
        row.operator("renaming.dataname_from_obj", icon="MOD_DATA_TRANSFER")


def drawAdvancedUI(self, context, advancedMode):
    layout = self.layout
    scene = context.scene

    split = layout.split(align=True, factor=0.3)
    split.label(text="Target")
    split.prop(scene, "renaming_object_types", text="")

    if str(scene.renaming_object_types) == 'OBJECT':
        layout.prop(scene, "renaming_object_types_specified", expand=True)
    # elif str(scene.renaming_object_types) == 'ADDOBJECTS':
    #    layout.prop(scene, "renaming_object_addtypes_specified", expand=True)

    # layout.use_property_split = True  # Activate single-column layout

    if str(scene.renaming_object_types) in ('MATERIAL', 'DATA'):
        layout.prop(scene, "renaming_only_selection", text="Only Of Selected Objects")
    elif str(scene.renaming_object_types) in ('OBJECT', 'ADDOBJECTS', 'BONE'):
        layout.prop(scene, "renaming_only_selection", text="Only Selected")

    layout.separator()

    layout.label(text="Rename")
    if True:
        ###### NEW NAME #######
        layout.prop(scene, "renaming_usenumerate")
        row = layout.row(align=True)
        split = layout.split(factor=0.6, align=True)
        split.prop(scene, "renaming_newName", text='')
        split = split.split(factor=0.75, align=True)
        split.prop(scene, "renaming_numerate", text='')
        button = split.operator("object.renaming_set_variable", text="@").inputBox = "newName"

        row = layout.row()
        row.scale_y = 1.5
        row.operator("renaming.name_replace", icon="FORWARD")
        layout.separator()

        ###### SEARCH REPLACE #######

        layout.separator()

        layout.label(text="Search and Replace")
        if advancedMode == True:
            if scene.renaming_useRegex == False:
                row = layout.row(align=True)
                row.prop(scene, "renaming_useRegex")
                row.prop(scene, "renaming_matchcase")
            else:
                layout.prop(scene, "renaming_useRegex")

            row = layout.row(align=True)
            split = row.split(factor=0.9, align=True)
            split.prop(scene, "renaming_search", text='Search')
            button = split.operator("object.renaming_set_variable", text="@").inputBox = "search"
            row = layout.row(align=True)
            split = row.split(factor=0.9, align=True)
            split.prop(scene, "renaming_replace", text='Replace')
            button = split.operator("object.renaming_set_variable", text="@").inputBox = "replace"

        if scene.renaming_object_types == 'BONE':
            if context.mode == 'POSE':
                row = layout.row(align=True)
                row.operator("renaming.search_select", icon="RESTRICT_SELECT_OFF")

        elif scene.renaming_object_types == 'OBJECT':
            row = layout.row(align=True)
            row.operator("renaming.search_select", icon="RESTRICT_SELECT_OFF")

        row = layout.row(align=True)
        row.scale_y = 1.5
        row.operator("renaming.search_replace", icon="FILE_REFRESH")
        layout.separator()

        ###############################################
        # layout.label(text="Other")
        # layout.separator()

        layout.label(text="Prefix")
        #### REFIX SUFFIX
        row = layout.row(align=True)
        split = row.split(factor=0.9, align=True)
        split.prop(scene, "renaming_prefix", text='')
        button = split.operator("object.renaming_set_variable", text="@").inputBox = "prefix"
        layout.operator("renaming.add_prefix", icon="REW")

        layout.label(text="Suffix ")

        row = layout.row(align=True)
        split = row.split(factor=0.9, align=True)
        split.prop(scene, "renaming_suffix", text='')
        button = split.operator("object.renaming_set_variable", text="@").inputBox = "suffix"
        layout.operator("renaming.add_suffix", icon="FF")

        layout.separator()
        layout.label(text="Other")
        ###############################################
        row = layout.row(align=True)
        # row.prop(scene, "renaming_digits_numerate", text="")
        row.operator("renaming.numerate", icon="LINENUMBERS_ON")

        ###############################################
        row = layout.row(align=True)
        row.prop(scene, "renaming_cut_size", text="")
        row.operator("renaming.cut_string", icon="X")

    if str(scene.renaming_object_types) in ('DATA', 'OBJECT', 'ADDOBJECTS'):
        layout.separator()
        layout.label(text="Data Name")

        row = layout.row(align=True)
        split = row.split(factor=0.9, align=True)
        split.prop(scene, "renaming_sufpre_data_02", text='')
        button = split.operator("object.renaming_set_variable", text="@").inputBox = "dataFromObj"
        layout.operator("renaming.dataname_from_obj", icon="MOD_DATA_TRANSFER")


def panel_func(self, context):
    layout = self.layout

    row = layout.row(align=True)
    row.menu(OBJECT_MT_sufpre_presets.__name__, text=OBJECT_MT_sufpre_presets.bl_label)
    row.operator(AddPresetRenamingPresets.bl_idname, text="", icon='ADD')
    row.operator(AddPresetRenamingPresets.bl_idname, text="", icon='REMOVE').remove_active = True


class VIEW3D_PT_tools_renaming_panel(bpy.types.Panel):
    """Creates a renaming Panel"""
    bl_label = "Simple Renaming Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Rename"

    def draw(self, context):

        prefs = context.preferences.addons[__package__].preferences
        advancedMode = prefs.renamingPanel_advancedMode

        layout = self.layout
        layout.prop(prefs, "renamingPanel_advancedMode")

        if advancedMode == True:
            drawAdvancedUI(self, context, advancedMode)
        else:
            drawSimpleUi(self, context)


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
        layout.prop(scene, "renaming_sufpre_type", expand=True)
        # layout.prop(scene, "renaming_sufpre_types_specified")

        if scene.renaming_sufpre_type == "PRE":
            layout.label(text="Add Type Prefix")
        else:
            layout.label(text="Add Type Suffix")

        split = layout.split()

        col = split.column()
        row = col.row()
        row.prop(scene, "renaming_sufpre_empty", text="")
        op = row.operator("renaming.add_sufpre_by_type", text="Empties").option = 'empty'

        row = col.row()
        row.prop(scene, "renaming_sufpre_geometry", text="")
        op = row.operator('renaming.add_sufpre_by_type', text="Meshes").option = 'mesh'

        row = col.row()
        row.prop(scene, "renaming_sufpre_material", text="")
        op = row.operator('renaming.add_sufpre_by_type', text="Materials").option = 'material'

        row = col.row()
        row.prop(scene, "renaming_sufpre_curve", text="")
        op = row.operator('renaming.add_sufpre_by_type', text="Curves").option = 'curve'

        row = col.row()
        row.prop(scene, "renaming_sufpre_armature", text="")
        op = row.operator('renaming.add_sufpre_by_type', text="Armatures").option = 'armature'

        row = col.row()
        row.prop(scene, "renaming_sufpre_lattice", text="")
        row.operator('renaming.add_sufpre_by_type', text="Lattices").option = 'lattice'

        row = col.row()
        row.prop(scene, "renaming_sufpre_data", text="")
        row.operator('renaming.add_sufpre_by_type', text="Data").option = 'data'

        row = col.row()
        row.prop(scene, "renaming_sufpre_surfaces", text="")
        row.operator('renaming.add_sufpre_by_type', text="Surfaces").option = 'surface'

        row = col.row()
        row.prop(scene, "renaming_sufpre_cameras", text="")
        row.operator('renaming.add_sufpre_by_type', text="Cameras").option = 'camera'

        row = col.row()
        row.prop(scene, "renaming_sufpre_lights", text="")
        row.operator('renaming.add_sufpre_by_type', text="Lights").option = 'light'

        row = col.row()
        row.prop(scene, "renaming_sufpre_collection", text="")
        row.operator('renaming.add_sufpre_by_type', text="Collections").option = 'collection'

        row = col.row()
        row.prop(scene, "renaming_sufpre_text", text="")
        row.operator('renaming.add_sufpre_by_type', text="Texts").option = 'text'

        row = col.row()
        row.prop(scene, "renaming_sufpre_gpencil", text="")
        row.operator('renaming.add_sufpre_by_type', text="Grease Pencil").option = 'gpencil'

        row = col.row()
        row.prop(scene, "renaming_sufpre_metaball", text="")
        row.operator('renaming.add_sufpre_by_type', text="Metaballs").option = 'metaball'

        row = col.row()
        row.prop(scene, "renaming_sufpre_bone", text="")
        row.operator('renaming.add_sufpre_by_type', text="Bones").option = 'bone'

        row = col.row()
        row.prop(scene, "renaming_sufpre_speakers", text="")
        row.operator('renaming.add_sufpre_by_type', text="Speakers").option = 'speakers'

        row = col.row()
        row.prop(scene, "renaming_sufpre_lightprops", text="")
        row.operator('renaming.add_sufpre_by_type', text="Light Probes").option = 'lightprops'

        row = col.row()
        row.operator('renaming.add_sufpre_by_type', text="All").option = 'all'


class VIEW3D_OT_SimpleOperator(bpy.types.Operator):
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
    bl_label = "Simple Renaming Panel"

    my_float: bpy.props.FloatProperty(name="Some Floating Point")
    my_bool: bpy.props.BoolProperty(name="Toggle Option")
    my_string: bpy.props.StringProperty(name="String Value")

    def execute(self, context):
        print("Dialog Runs")
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class LITTLE_RENAMING_HELPERS(bpy.types.Operator):
    """Creates a renaming Panel"""
    bl_label = "Renaming Helpers"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Rename"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        return {'FINISHED'}


class OBJECT_MT_sufpre_presets(Menu):
    bl_label = "Type Presets"
    preset_subdir = "scene/display"
    preset_operator = "script.execute_preset"
    draw = Menu.draw_preset


class AddPresetRenamingPresets(AddPresetBase, Operator):
    '''Add a Object Display Preset'''
    bl_idname = "renaming.sufpreadd_presets"
    bl_label = "Add Renaming Preset"
    preset_menu = "OBJECT_MT_sufpre_presets"

    # variable used for all preset values
    preset_defines = [
        "scene = bpy.context.scene"
    ]

    # properties to store in the preset
    preset_values = [
        "scene.renaming_sufpre_empty",
        "scene.renaming_sufpre_geometry",
        "scene.renaming_sufpre_material",
        "scene.renaming_sufpre_curve",
        "scene.renaming_sufpre_armature",
        "scene.renaming_sufpre_lattice",
        "scene.renaming_sufpre_data",
        "scene.renaming_sufpre_surfaces",
        "scene.renaming_sufpre_cameras",
        "scene.renaming_sufpre_lights",
        "scene.renaming_sufpre_collection",
        "scene.renaming_sufpre_text",
        "scene.renaming_sufpre_gpencil",
        "scene.renaming_sufpre_metaball",
        "scene.renaming_sufpre_bone",
        "scene.renaming_sufpre_speakers",
        "scene.renaming_sufpre_lightprops",
    ]

    # where to store the preset
    preset_subdir = "scene/display"
