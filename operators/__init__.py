import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    StringProperty,
    IntProperty,
    IntVectorProperty,
)

from . import add_pre_suffix
from . import case_transform
from . import name_from_data
from . import name_replace
from . import number_transform
from . import numerate
from . import search_replace
from . import search_select
from . import select_in_renaming_order
from . import trim_string

enumObjectTypes = [('EMPTY', "", "Rename empty objects", 'OUTLINER_OB_EMPTY', 1),
                   ('MESH', "", "Rename mesh objects", 'OUTLINER_OB_MESH', 2),
                   ('CAMERA', "", "Rename Camera objects", 'OUTLINER_OB_CAMERA', 4),
                   ('LIGHT', "", "Rename light objects", 'OUTLINER_OB_LIGHT', 8),
                   ('ARMATURE', "", "Rename armature objects", 'OUTLINER_OB_ARMATURE', 16),
                   ('LATTICE', "", "Rename lattice objects", 'OUTLINER_OB_LATTICE', 32),
                   ('CURVE', "", "Rename curve objects", 'OUTLINER_OB_CURVE', 64),
                   ('SURFACE', "", "Rename surface objects", 'OUTLINER_OB_SURFACE', 128),
                   ('FONT', "", "Rename font objects", 'OUTLINER_OB_FONT', 256),
                   ('GPENCIL', "", "Rename grease pencil objects", 'OUTLINER_OB_GREASEPENCIL', 512),
                   ('META', "", "Rename metaball objects", 'OUTLINER_OB_META', 1024),
                   ('SPEAKER', "", "Rename empty speakers", 'OUTLINER_OB_SPEAKER', 2048),
                   ('LIGHT_PROBE', "", "Rename mesh lightpropes", 'OUTLINER_OB_LIGHTPROBE', 4096),
                   ('VOLUME', "", "Rename mesh volumes", 'OUTLINER_OB_VOLUME', 8192),
                   ('POINTCLOUD', "", "Rename point cloud objects", 'OUTLINER_OB_POINTCLOUD', 16384),
                   ('CURVES', "", "Rename hair curve objects", 'OUTLINER_OB_CURVES', 32768)]

enumObjectTypesAdd = [('SPEAKER', "", "Rename empty speakers", 'OUTLINER_OB_SPEAKER', 1),
                      ('LIGHT_PROBE', "", "Rename mesh lightpropes", 'OUTLINER_OB_LIGHTPROBE', 2)]

prefixSuffixItems = [('PRE', "Prefix", "prefix"),
                     ('SUF', "Suffix", "suffix")
                     ]

renamingEntitiesItems = [('OBJECT', "Object", "Scene Objects"),
                         ('MATERIAL', "Material", "Materials"),
                         ('COLLECTION', "Collection", "Rename collections"),
                         None,
                         ('DATA', "Data", "Object Data"),
                         None,
                         ('BONE', "Bone", "Bones"),
                         ('IMAGE', "Image Textures", "Image Textures"),
                         None,
                         ('MODIFIERS', "Modifiers", "Rename Modifiers"),
                         ('SHAPEKEYS', "Shape Keys", "Rename shape keys"),
                         None,
                         ('ATTRIBUTES', "Attributes", "Rename attributes"),
                         ('COLORATTRIBUTES', "Color Attributes", "Rename color attributes"),
                         ('UVMAPS', "UV Maps", "Rename vertex groups"),
                         ('VERTEXGROUPS', "Vertex Groups", "Rename vertex groups"),
                         None,
                         ('ACTIONS', "Actions", "Rename Actions"),
                         None,
                         ('PARTICLESYSTEM', "Particle Systems", "Rename particle systems"),
                         ('PARTICLESETTINGS', "Particle Settings", "Rename particle settings"),
                         None,
                         ('NODE_GROUPS', "Node Groups", "Rename node groups"),
                         ]

classes = (
    search_select.VIEW3D_OT_search_and_select,
    search_replace.VIEW3D_OT_search_and_replace,
    name_replace.VIEW3D_OT_replace_name,
    trim_string.VIEW3D_OT_trim_string,
    add_pre_suffix.VIEW3D_OT_add_suffix,
    add_pre_suffix.VIEW3D_OT_add_prefix,
    numerate.VIEW3D_OT_renaming_numerate,
    name_from_data.VIEW3D_OT_use_objectname_for_data,
    case_transform.VIEW3D_OT_case_upper,
    case_transform.VIEW3D_OT_case_lower,
    case_transform.VIEW3D_OT_case_pascal,
    case_transform.VIEW3D_OT_case_camel,
    case_transform.VIEW3D_OT_case_snake,
    case_transform.VIEW3D_OT_case_kebab,
    number_transform.VIEW3D_OT_number_pad,
    number_transform.VIEW3D_OT_number_to_letters_lower,
    number_transform.VIEW3D_OT_number_to_letters_upper,
    number_transform.VIEW3D_OT_letters_to_number,
    number_transform.VIEW3D_OT_letters_to_upper,
    number_transform.VIEW3D_OT_letters_to_lower,
    select_in_renaming_order.VIEW3D_OT_select_in_renaming_order,
)

enum_sort_items = [('X', "X Axis", "Sort the object based on the X axis."),
                   ('Y', "Y Axis", "Sort the object based on the Y axis."),
                   ('Z', "Z Axis", "Sort the object based on the Z axis."),
                   ('SELECTION', "Selection", "Sort the objects based on the order they were clicked in with \"Select in Renaming Order\""), ]

enum_sort_bone_items = [('X', "X Axis", "Sort the object based on the X axis."),
                        ('Y', "Y Axis", "Sort the object based on the Y axis."),
                        ('Z', "Z Axis", "Sort the object based on the Z axis."),
                        ('SELECTION', "Selection", "Sort the bones based on the order they were clicked in with \"Select in Renaming Order\""), ]


def register():
    id_store = bpy.types.Scene

    id_store.renaming_suffix_prefix_type = EnumProperty(name="Suffix or Prefix by Type",
                                                        items=prefixSuffixItems,
                                                        description="Add Prefix or Suffix to type",
                                                        default='SUF'
                                                        )

    id_store.renaming_object_types = EnumProperty(name="Renaming Objects",
                                                  items=renamingEntitiesItems,
                                                  description="Which kind of object to rename",
                                                  )

    id_store.renaming_object_types_specified = EnumProperty(name="Object Types",
                                                            items=enumObjectTypes,
                                                            description="Which kind of object to rename",
                                                            options={'ENUM_FLAG'},
                                                            default={'CURVE', 'LATTICE', 'SURFACE', 'MESH',
                                                                     'ARMATURE', 'LIGHT', 'CAMERA', 'EMPTY', 'GPENCIL',
                                                                     'FONT', 'SPEAKER', 'LIGHT_PROBE', 'VOLUME',
                                                                     'POINTCLOUD', 'CURVES'}
                                                            )

    id_store.renaming_sort_enum = EnumProperty(
        name="Sort by",
        description="Sort Objects based on following attribute",
        items=enum_sort_items,
        default='X',  # Set a default value
    )
    id_store.renaming_sort_bone_enum = EnumProperty(
        name="Sort by",
        description="Sort Bones based on following attribute",
        items=enum_sort_bone_items,
        default='X',  # Set a default value
    )

    id_store.renaming_new_name = StringProperty(
        name="New Name",
        description="Name pattern for renaming. Use @n for a numbered variable (configure its digits in Preferences). Use the Numerate section above to set the auto-suffix digit count or switch to letters",
        default='',
    )
    id_store.renaming_search = StringProperty(name='Search', default='')
    id_store.renaming_replace = StringProperty(name='Replace', default='')
    id_store.renaming_suffix = StringProperty(name="Suffix", default='')
    id_store.renaming_prefix = StringProperty(name="Prefix", default='')
    id_store.renaming_numerate = IntProperty(
        name="Padding",
        description="Digit count for the auto-numeration suffix appended when Numerate is enabled (e.g. 3 → 001, "
                    "002, …), and for the Set Padding / Letters → Number tools. Ignored when Letters is enabled "
                    "for the auto-numeration suffix. Does not affect the @n variable",
        default=3,
        min=0,
    )

    id_store.renaming_sorting = bpy.props.BoolProperty(
        name="Sort Target Objects",
        description="Sort the entries for renaming",
        default=False,
    )
    id_store.renaming_sort_reverse = BoolProperty(name="Reverse Sorting Order", default=False)

    id_store.renaming_only_selection = BoolProperty(name="Selected Objects", description="Rename Selected Objects",
                                                    default=True)

    id_store.renaming_matchcase = BoolProperty(name="Match Case", description="", default=True)
    id_store.renaming_useRegex = BoolProperty(name="Use Regex", description="", default=False)
    id_store.renaming_use_enumerate = BoolProperty(
        name="Use Numerate",
        description="Automatically appends an incrementing numeric suffix to each renamed object. Configure the digit count or switch to letters in the Numerate section above, and the digit count for the @n variable in Preferences",
        default=True,
    )
    id_store.renaming_trim_indices = IntVectorProperty(name="Trim Size", default=(0, 0), min=0, soft_min=0, size=2)

    id_store.renaming_active_only = BoolProperty(
        name="Active Only",
        description="Only rename the active layer on each object",
        default=False,
    )
    id_store.renaming_filter_by_index = BoolProperty(
        name="By Index",
        description="Only rename the layer at the specified index on each object",
        default=False,
    )
    id_store.renaming_index_target = IntProperty(name="Index", default=0, min=0)

    id_store.renaming_also_rename_data = BoolProperty(
        name="Also Rename Data",
        description="Also rename the linked data block (mesh, curve, etc.) to match the object name",
        default=False,
    )

    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)



def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)

    IDStore = bpy.types.Scene
    del IDStore.renaming_search
    del IDStore.renaming_new_name
    del IDStore.renaming_object_types
    del IDStore.renaming_suffix_prefix_type
    del IDStore.renaming_replace
    del IDStore.renaming_suffix
    del IDStore.renaming_prefix
    del IDStore.renaming_only_selection
    del IDStore.renaming_trim_indices
    del IDStore.renaming_also_rename_data
    del IDStore.renaming_active_only
    del IDStore.renaming_filter_by_index
    del IDStore.renaming_index_target

