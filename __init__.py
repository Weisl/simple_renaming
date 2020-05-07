'''
Copyright (C) 2019 Matthias Patscheider
patscheider.matthias@gmail.com

Created by Matthias Patscheider

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
    "name": "Simple Renaming Panel",
    "description": "This Addon offers the basic functionality of renaming a set of objects",
    "author": "Matthias Patscheider",
    "version": (1, 5, 0),
    "blender": (2, 83, 0),
    "location": "View3D > Tools ",
    "warning": "",
    "wiki_url": "https://github.com/Weisl/simple_renaming_panel",
    "tracker_url": "https://github.com/Weisl/simple_renaming_panel/issues",
    "support": "COMMUNITY",
    "category": "Scene"
}

#activate hotkeys to begin with
#disable Validation panel
#disable suffix\prefix panel
#use collection name
# auto update
#blender code formating
#presets for vallidations

# support reloading sub-modules
if "bpy" in locals():
    import importlib

    importlib.reload(renaming_operators)
    importlib.reload(renaming_popup)
    importlib.reload(renaming_utilities)
    importlib.reload(renaming_panels)
    #importlib.reload(renaming_vallidate)
    importlib.reload(renaming_sufPre_operators)
    importlib.reload(renaming_proFeatures)
    importlib.reload(renaming_preferences)
    importlib.reload(addon_updater)
    importlib.reload(addon_updater_ops)

else:
    from . import renaming_operators
    from . import renaming_popup
    from . import renaming_utilities
    from . import renaming_panels
    #from . import renaming_vallidate
    from . import renaming_sufPre_operators
    from . import renaming_proFeatures
    from . import renaming_preferences
    from . import addon_updater
    from . import addon_updater_ops

# import standard modules
import bpy
from bpy.props import (
    BoolProperty,
    IntProperty,
    EnumProperty,
    StringProperty,
)

from .renaming_panels import panel_func
from .renaming_preferences import remove_hotkey
from .renaming_proFeatures import tChange
from .renaming_utilities import RENAMING_MESSAGES, WarningError_MESSAGES, INFO_MESSAGES

# Add default key configuration for batch renaming


# all classes that are supposed to be registered in the blender core.
classes = (
    renaming_panels.VIEW3D_PT_tools_renaming_panel,
    renaming_panels.VIEW3D_PT_tools_type_suffix,
    renaming_panels.VIEW3D_OT_SimpleOperator,
    renaming_panels.VIEW3D_OT_RenamingPopupOperator,
    renaming_panels.OBJECT_MT_sufpre_presets,
    renaming_panels.AddPresetRenamingPresets,
    renaming_popup.VIEW3D_PT_renaming_popup,
    renaming_popup.VIEW3D_PT_info_popup,
    renaming_popup.VIEW3D_PT_error_popup,
    renaming_operators.VIEW3D_OT_add_suffix,
    renaming_operators.VIEW3D_OT_add_prefix,
    renaming_operators.VIEW3D_OT_search_and_replace,
    renaming_operators.VIEW3D_OT_renaming_numerate,
    renaming_operators.VIEW3D_OT_trim_string,
    renaming_operators.VIEW3D_OT_use_objectname_for_data,
    renaming_operators.VIEW3D_OT_replace_name,
    renaming_operators.VIEW3D_OT_search_and_select,
    renaming_sufPre_operators.VIEW3D_OT_add_type_suf_pre,
    renaming_proFeatures.RENAMING_MT_variableMenu,
    renaming_proFeatures.VIEW3D_OT_inputVariables,
    #renaming_vallidate.VIEW3D_OT_Validate,
    #renaming_vallidate.VIEW3D_PT_vallidation,
    renaming_preferences.RENAMING_OT_add_hotkey_renaming,
    renaming_preferences.VIEW3D_OT_renaming_preferences,
# Preferences need to be after Operators for the hotkeys to work
)


def menu_add_suffix(self, context):
    self.layout.operator(VIEW3D_OT_add_suffix.bl_idname)  # or YourClass.bl_idname


enumObjectTypes = [('EMPTY', "", "Rename empty objects", 'OUTLINER_OB_EMPTY', 1),
                   ('MESH', "", "Rename mesh objects", 'OUTLINER_OB_MESH', 2),
                   ('CAMERA', "", "Rename Camera objects", 'OUTLINER_OB_CAMERA', 4),
                   ('LIGHT', "", "Rename light objects", 'OUTLINER_OB_LIGHT', 8),
                   ('ARMATURE', "", "Rename armature objects", 'OUTLINER_OB_ARMATURE', 16),
                   ('LATTICE', "", "Rename lattice objects", 'OUTLINER_OB_LATTICE', 32),
                   ('CURVE', "", "Rename curve objects", 'OUTLINER_OB_CURVE', 64),
                   ('SURFACE', "", "Rename surface objects", 'OUTLINER_OB_SURFACE', 128),
                   ('TEXT', "", "Rename text objects", 'OUTLINER_OB_FONT', 256),
                   ('GPENCIL', "", "Rename greace pencil objects", 'OUTLINER_OB_GREASEPENCIL', 512),
                   ('METABALL', "", "Rename metaball objects", 'OUTLINER_OB_META', 1024),
                   ('SPEAKER', "", "Rename empty speakers", 'OUTLINER_OB_SPEAKER', 2048),
                   ('LIGHT_PROBE', "", "Rename mesh lightpropes", 'OUTLINER_OB_LIGHTPROBE', 4096),
                   ('VOLUME', "", "Rename mesh volumes", 'OUTLINER_OB_VOLUME', 8192)
                   ]

enumObjectTypesAdd = [('SPEAKER', "", "Rename empty speakers", 'OUTLINER_OB_SPEAKER', 1),
                      ('LIGHT_PROBE', "", "Rename mesh lightpropes", 'OUTLINER_OB_LIGHTPROBE', 2)]

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
                   ]

prefixSuffixItems = [('PRE', "Prefix", "prefix"),
                     ('SUF', "Suffix", "suffix")
                     ]

renamingEntitiesItems = [('OBJECT', "Object", "Scene Objects"),
                         # ('ADDOBJECTS', "Objects (additional)","Scene Objects"),
                         ('MATERIAL', "Material", "Materials"),
                         ('IMAGE', "Image Textures", "Image Textures"),
                         ('DATA', "Data", "Object Data"),
                         ('BONE', "Bone", "Bones"),
                         ('COLLECTION', "Collection", "Rename collections"),
                         ('ACTIONS', "Actions", "Rename Actions"),
                         ('SHAPEKEYS', "Shape Keys", "Rename shape keys")
                         # ('VERTEXGROUPS',"Vertex Groups", "Rename vertex groups")
                         # ('UVMaps')
                         # ('FACEMAPS')
                         # ('PARTICLESYSTEM')
                         ]

keys = []


def register():



    IDStore = bpy.types.Scene

    IDStore.renaming_sufpre_type = EnumProperty(
        name="Suffix or Prefix by Type",
        items=prefixSuffixItems,
        description="Add Prefix or Suffix to type",
        default='SUF'
    )

    IDStore.renaming_object_types = EnumProperty(
        name="Renaming Objects",
        items=renamingEntitiesItems,
        description="Which kind of object to rename",
    )

    IDStore.renaming_object_types_specified = EnumProperty(name="Object Types",
                                                           items=enumObjectTypes,
                                                           description="Which kind of object to rename",
                                                           options={'ENUM_FLAG'},
                                                           default={'CURVE', 'LATTICE', 'SURFACE', 'METABALL', 'MESH',
                                                                    'ARMATURE', 'LIGHT', 'CAMERA', 'EMPTY', 'GPENCIL',
                                                                    'TEXT', 'SPEAKER', 'LIGHT_PROBE', 'VOLUME'}
                                                           )

    IDStore.renaming_newName = StringProperty(name="New Name", default='')
    IDStore.renaming_search = StringProperty(name='Search', default='')
    IDStore.renaming_replace = StringProperty(name='Replace', default='')
    IDStore.renaming_suffix = StringProperty(name="Suffix", default='')
    IDStore.renaming_prefix = StringProperty(name="Prefix", default='')
    IDStore.renaming_numerate = StringProperty(name="Numerate", default='###')

    IDStore.renaming_only_selection = BoolProperty(name="Selected Objects", description="Rename Selected Objects",
                                                   default=True)
    IDStore.renamingPanel_advancedMode = BoolProperty(name="Advanced Renaming",
                                                      description="Enable additional feautres for renaming",
                                                      default=False)
    IDStore.renaming_matchcase = BoolProperty(name="Match Case", description="", default=True)
    IDStore.renaming_useRegex = BoolProperty(name="Use Regex", description="", default=False)
    IDStore.renaming_usenumerate = BoolProperty(name="Numerate",
                                                description="Enable and Disable the numeration of objects. This can be especially useful in combination with the custom numberation variable @n",
                                                default=True,
                                                )
    IDStore.renaming_base_numerate = IntProperty(name="Step Size", default=1)
    IDStore.renaming_start_number = IntProperty(name="Step Size", default=1)
    IDStore.renaming_digits_numerate = IntProperty(name="Number Length", default=3)
    IDStore.renaming_cut_size = IntProperty(name="Trim Size", default=3)
    IDStore.renaming_messages = RENAMING_MESSAGES()
    IDStore.renaming_error_messages = WarningError_MESSAGES()
    IDStore.renaming_info_messages = INFO_MESSAGES()

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

    addon_updater_ops.register(bl_info)

    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.VIEW3D_PT_tools_type_suffix.prepend(panel_func)



def unregister():
    IDStore = bpy.types.Scene
    del IDStore.renaming_search
    del IDStore.renaming_newName
    del IDStore.renaming_object_types
    del IDStore.renaming_sufpre_type
    del IDStore.renaming_replace
    del IDStore.renaming_suffix
    del IDStore.renaming_prefix
    del IDStore.renaming_only_selection
    del IDStore.renaming_base_numerate
    del IDStore.renaming_digits_numerate
    del IDStore.renaming_cut_size
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

    addon_updater_ops.unregister()

    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    # from .addon_preferenecs import remove_hotkey



    remove_hotkey()


if __name__ == "__main__":
    register()
