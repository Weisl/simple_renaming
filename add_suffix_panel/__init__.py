from . import renaming_sufPre_operators

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    StringProperty,
    IntProperty,
)


def tChange(self, context):
    '''

    :param context: current blender context
    :return: no return value
    '''

    wm = bpy.context.scene

    # The print function works fine
    nameingPreset = context.scene.renaming_presetNaming
    nameVar = ""

    ##### System and Global Values ################
    if nameingPreset == 'FILE':
        nameVar = "@f"
    if nameingPreset == "DATE":
        nameVar = "@d"
    if nameingPreset == "TIME":
        nameVar = "@i"
    if nameingPreset == "RANDOM":
        nameVar = "@r"

    ##### UserStrings ################
    if nameingPreset == "HIGH":
        nameVar = "@h"
    if nameingPreset == "LOW":
        nameVar = "@l"
    if nameingPreset == "CAGE":
        nameVar = "@b"
    if nameingPreset == "USER1":
        nameVar = "@u1"
    if nameingPreset == "USER2":
        nameVar = "@u2"
    if nameingPreset == "USER3":
        nameVar = "@u3"
    if nameingPreset == "NUMERATE":
        nameVar = "@n"

    if wm.renaming_object_types == 'OBJECT':
        if nameingPreset == 'OBJECT':
            nameVar = "@o"
        if nameingPreset == "TYPE":
            nameVar = "@t"
        if nameingPreset == "PARENT":
            nameVar = "@p"
        if nameingPreset == "ACTIVE":
            nameVar = "@a"
        if nameingPreset == "COLLECTION":
            nameVar = "@c"
        if nameingPreset == "DATA":
            nameVar = "@m"

    context.scene.renaming_newName += str(nameVar)
    return

classes = (
   renaming_sufPre_operators.VIEW3D_OT_add_type_suf_pre,
)

enumPresetItems = [('FILE', "File", "", '', 1),
                   ('OBJECT', "Object", "", '', 2),
                   ('HIGH', "High", "", '', 4),
                   ('LOW', "Low", "", '', 8),
                   ('CAGE', "Cage", "", '', 16),
                   ('DATE', "Date", "", '', 32),
                   ('TIME', "Time", "", '', 128),
                   ('TYPE', "Type", "", '', 1024),
                   ('PARENT', "Parent", "", '', 2048),
                   ('ACTIVE', "Active", "", '', 4096),
                   ('USER1', "User1", "", '', 8192),
                   ('USER2', "User2", "", '', 256),
                   ('USER3', "User3", "", '', 512),
                   ('NUMBER', "Number", "", '', 1024),
                   ('DATA', "Data", "", '', 2048),
                   ]

enumObjectTypesExt = [('EMPTY', "", "Rename empty objects", 'OUTLINER_OB_EMPTY', 1),
                      ('MESH', "", "Rename mesh objects", 'OUTLINER_OB_MESH', 2),
                      ('CAMERA', "", "Rename Camera objects", 'OUTLINER_OB_CAMERA', 4),
                      ('LIGHT', "", "Rename light objects", 'OUTLINER_OB_LIGHT', 8),
                      ('ARMATURE', "", "Rename armature objects", 'OUTLINER_OB_ARMATURE', 16),
                      ('LATTICE', "", "Rename lattice objects", 'OUTLINER_OB_LATTICE', 32),
                      ('CURVE', "", "Rename curve objects", 'OUTLINER_OB_CURVE', 64),
                      ('SURFACE', "", "Rename surface objects", 'OUTLINER_OB_SURFACE', 128),
                      ('TEXT', "", "Rename text objects", 'OUTLINER_OB_FONT', 256),
                      ('GPENCIL', "", "Rename greace pencil objects", 'OUTLINER_OB_GREASEPENCIL', 512),
                      ('METABALL', "", "Rename metaball objects", 'OUTLINER_OB_META', 2048),
                      ('COLLECTION', "", "Rename collections", 'GROUP', 4096),
                      ('BONE', "", "", 'BONE_DATA', 8192), ]


def register():
    IDStore = bpy.types.Scene

    ############## Type Suffix Prefix ########################################
    IDStore.type_pre_sub_only_selection = BoolProperty(
        name="Selected Objects",
        description="Rename Selected Objects",
        default=True,
    )

    IDStore.renaming_sufpre_types_specified = EnumProperty(name="Object Types",
                                                           items=enumObjectTypesExt,
                                                           description="Which kind of object to rename",
                                                           options={'ENUM_FLAG'},
                                                           default={'CURVE', 'LATTICE', 'SURFACE', 'METABALL', 'MESH',
                                                                    'ARMATURE', 'LIGHT', 'CAMERA', 'EMPTY', 'GPENCIL',
                                                                    'TEXT', 'BONE', 'COLLECTION'}
                                                           )

    IDStore.renaming_sufpre_material = StringProperty(name='Material', default='')
    IDStore.renaming_sufpre_geometry = StringProperty(name='Geometry', default='')
    IDStore.renaming_sufpre_empty = StringProperty(name="Empty", default='')
    IDStore.renaming_sufpre_group = StringProperty(name="Group", default='')
    IDStore.renaming_sufpre_curve = StringProperty(name="Curve", default='')
    IDStore.renaming_sufpre_armature = StringProperty(name="Armature", default='')
    IDStore.renaming_sufpre_lattice = StringProperty(name="Lattice", default='')
    IDStore.renaming_sufpre_data = StringProperty(name="Data", default='')
    IDStore.renaming_sufpre_data_02 = StringProperty(name="Data = Objectname + ", default='')
    IDStore.renaming_sufpre_surfaces = StringProperty(name="Surfaces", default='')
    IDStore.renaming_sufpre_cameras = StringProperty(name="Cameras", default='')
    IDStore.renaming_sufpre_lights = StringProperty(name="Lights", default='')
    IDStore.renaming_sufpre_collection = StringProperty(name="Collections", default='')
    IDStore.renaming_sufpre_text = StringProperty(name="Text", default='')
    IDStore.renaming_sufpre_gpencil = StringProperty(name="Grease Pencil", default='')
    IDStore.renaming_sufpre_metaball = StringProperty(name="Metaballs", default='')
    IDStore.renaming_sufpre_bone = StringProperty(name="Bones", default='')
    IDStore.renaming_sufpre_speakers = StringProperty(name="Speakers", default='')
    IDStore.renaming_sufpre_lightprops = StringProperty(name="LightProps", default='')

    IDStore.renaming_inputContext = StringProperty(name="LightProps", default='')

    # Pro Features
    IDStore.renaming_presetNaming = EnumProperty(name="Object Types",
                                                 items=enumPresetItems,
                                                 description="Which kind of object to rename",
                                                 update=tChange
                                                 )

    IDStore.renaming_presetNaming1 = EnumProperty(name="Object Types",
                                                  items=enumPresetItems,
                                                  description="Which kind of object to rename",
                                                  update=tChange
                                                  )

    IDStore.renaming_presetNaming2 = EnumProperty(name="Object Types",
                                                  items=enumPresetItems,
                                                  description="Which kind of object to rename",
                                                  update=tChange
                                                  )

    IDStore.renaming_presetNaming3 = EnumProperty(name="Object Types",
                                                  items=enumPresetItems,
                                                  description="Which kind of object to rename",
                                                  update=tChange
                                                  )

    IDStore.renaming_presetNaming4 = EnumProperty(name="Object Types",
                                                  items=enumPresetItems,
                                                  description="Which kind of object to rename",
                                                  update=tChange
                                                  )

    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)

    IDStore = bpy.types.Scene

    del IDStore.renaming_sufpre_material
    del IDStore.renaming_sufpre_geometry
    del IDStore.renaming_sufpre_empty
    del IDStore.renaming_sufpre_group
    del IDStore.renaming_sufpre_curve
    del IDStore.renaming_sufpre_armature
    del IDStore.renaming_sufpre_lattice
    del IDStore.renaming_sufpre_data
    del IDStore.renaming_sufpre_data_02
    del IDStore.renaming_start_number

    del IDStore.renaming_sufpre_lights
    del IDStore.renaming_sufpre_cameras
    del IDStore.renaming_sufpre_surfaces
    del IDStore.renaming_sufpre_bone
    del IDStore.renaming_sufpre_collection
    del IDStore.renaming_object_types_specified
    del IDStore.renaming_sufpre_speakers
    del IDStore.renaming_sufpre_lightprops
