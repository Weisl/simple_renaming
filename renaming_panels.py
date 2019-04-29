import bpy
from . import get_hotkey_entry_item
#############################################
############ PANELS ########################
#############################################

# addon Panel
class VIEW3D_PT_tools_renaming_panel(bpy.types.Panel):
    """Creates a renaming Panel"""
    bl_label = "Simple Renaming Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Simple Renaming Panel"

    def draw(self, context):

        layout = self.layout
        scene = context.scene
        prefs = bpy.context.preferences.addons[__package__].preferences
        #
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.addon
        km = kc.keymaps['3D View Generic']

        kmi1 = get_hotkey_entry_item(km, 'wm.call_panel', 'VIEW3D_PT_tools_renaming_panel')
        kmi2 = get_hotkey_entry_item(km, 'wm.call_panel', 'VIEW3D_PT_tools_type_suffix')

        keys = ""
        if kmi1.shift:
            keys += " Shift "
        if kmi1.alt:
            keys += " Alt "
        if kmi1.ctrl:
            keys += " Ctrl "
        keys += " " + kmi1.type

        keys2 = ""
        if kmi2.ctrl:
            keys2 += " Ctrl "
        if kmi2.shift:
            keys2 += " Shift "
        if kmi2.alt:
            keys2 += " Alt "
        keys2 += " " + kmi2.type


        layout.label(text = keys)
        layout.label(text = keys2)

        layout.prop(scene, "renaming_object_types")
        if str(scene.renaming_object_types) == 'OBJECT':
            layout.prop(scene, "renaming_object_types_specified", expand=True)
        #elif str(scene.renaming_object_types) == 'ADDOBJECTS':
        #    layout.prop(scene, "renaming_object_addtypes_specified", expand=True)

        layout.use_property_split = True  # Activate single-column layout

        if str(scene.renaming_object_types) in ('MATERIAL', 'DATA'):
            layout.prop(scene, "renaming_only_selection", text="Only Of Selected Objects")
        elif str(scene.renaming_object_types) in ('OBJECT', 'ADDOBJECTS', 'BONE'):
            layout.prop(scene, "renaming_only_selection", text="Only Selected")

        layout.separator()

        layout.prop(scene, "renaming_newName")
        layout.operator("renaming.name_replace")
        layout.prop(scene, "renaming_search")
        layout.prop(scene, "renaming_replace")
        layout.prop(scene, "renaming_useRegex")

        if scene.renaming_useRegex == False:
            layout.prop(scene, "renaming_matchcase")

        layout.operator("renaming.search_replace")

        layout.prop(scene, "renaming_prefix")
        layout.operator("renaming.add_prefix")

        layout.prop(scene, "renaming_suffix")
        layout.operator("renaming.add_suffix")

        layout.prop(scene, "renaming_digits_numerate")
        layout.operator("renaming.numerate")
        layout.prop(scene, "renaming_cut_size")
        layout.operator("renaming.cut_string")

        if str(scene.renaming_object_types) in ('DATA', 'OBJECT','ADDOBJECTS'):
            layout.prop(scene, "renaming_sufpre_data_02")
            layout.operator("renaming.dataname_from_obj")

# addon Panel
class VIEW3D_PT_tools_type_suffix(bpy.types.Panel):
    """Creates a renaming Panel"""
    bl_label = "Prefix/Suffix by Type"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Simple Renaming Panel"


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
        row.prop(scene, "renaming_sufpre_empty", text = "")
        op = row.operator("renaming.add_sufpre_by_type", text = "Empties").option = 'empty'

        row = col.row()
        row.prop(scene, "renaming_sufpre_geometry", text = "")
        op = row.operator('renaming.add_sufpre_by_type', text = "Meshes").option = 'mesh'

        row = col.row()
        row.prop(scene, "renaming_sufpre_material", text = "")
        op = row.operator('renaming.add_sufpre_by_type', text = "Materials").option = 'material'

        row = col.row()
        row.prop(scene, "renaming_sufpre_curve", text = "")
        op = row.operator('renaming.add_sufpre_by_type', text = "Curves").option = 'curve'

        row = col.row()
        row.prop(scene, "renaming_sufpre_armature", text = "")
        op = row.operator('renaming.add_sufpre_by_type', text = "Armatures").option = 'armature'

        row= col.row()
        row.prop(scene, "renaming_sufpre_lattice", text = "")
        row.operator('renaming.add_sufpre_by_type', text = "Lattices").option = 'lattice'

        row= col.row()
        row.prop(scene, "renaming_sufpre_data", text = "")
        row.operator('renaming.add_sufpre_by_type', text = "Data").option = 'data'

        row = col.row()
        row.prop(scene, "renaming_sufpre_surfaces", text = "")
        row.operator('renaming.add_sufpre_by_type', text = "Surfaces").option = 'surface'

        row = col.row()
        row.prop(scene, "renaming_sufpre_cameras", text = "")
        row.operator('renaming.add_sufpre_by_type', text = "Cameras").option = 'camera'

        row = col.row()
        row.prop(scene, "renaming_sufpre_lights", text = "")
        row.operator('renaming.add_sufpre_by_type', text = "Lights").option = 'light'

        row = col.row()
        row.prop(scene, "renaming_sufpre_collection", text = "")
        row.operator('renaming.add_sufpre_by_type', text = "Collections").option = 'collection'

        row = col.row()
        row.prop(scene, "renaming_sufpre_text", text = "")
        row.operator('renaming.add_sufpre_by_type', text = "Texts").option = 'text'

        row = col.row()
        row.prop(scene, "renaming_sufpre_gpencil", text = "")
        row.operator('renaming.add_sufpre_by_type', text = "Grease Pencil").option = 'gpencil'

        row = col.row()
        row.prop(scene, "renaming_sufpre_metaball", text = "")
        row.operator('renaming.add_sufpre_by_type', text = "Metaballs").option = 'metaball'

        row = col.row()
        row.prop(scene, "renaming_sufpre_bone", text = "")
        row.operator('renaming.add_sufpre_by_type', text = "Bones").option = 'bone'

        row = col.row()
        row.prop(scene, "renaming_sufpre_speakers", text = "")
        row.operator('renaming.add_sufpre_by_type', text = "Speakers").option = 'speakers'

        row = col.row()
        row.prop(scene, "renaming_sufpre_lightprops", text = "")
        row.operator('renaming.add_sufpre_by_type', text = "Light Probes").option = 'lightprops'

