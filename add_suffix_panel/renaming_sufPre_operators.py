import bpy
from bpy.props import (
    StringProperty,
)

from ..operators.renaming_utilities import call_renaming_popup


def suffix_prefix_add(context, obj, suffix_prefix_name):
    wm = context.scene

    new_name = obj.name
    if wm.renaming_suffix_prefix_type == 'SUF':
        new_name = new_name + suffix_prefix_name
    else:
        new_name = suffix_prefix_name + new_name

    if new_name not in bpy.data.objects:
        obj.name = new_name
        return new_name
    else:
        i = 1
        while new_name in bpy.data.objects:
            if wm.renaming_suffix_prefix_type == 'SUF':
                new_name = obj.name + "_" + str(i) + suffix_prefix_name
            else:
                new_name = suffix_prefix_name + obj.name + "_" + str(i)
            i = i + 1

    obj.name = new_name
    return new_name


class VIEW3D_OT_add_type_suf_pre(bpy.types.Operator):
    """Add Type Suffix"""
    bl_idname = "renaming.add_suffix_prefix_by_type"
    bl_label = "Add Type Suffix or Prefix"
    bl_description = "Adds the above defined Suffixes or Prefixes to all objects in your scene"
    bl_options = {'REGISTER', 'UNDO'}

    option: StringProperty()

    def __init__(self):
        self.context = None

    def get_selection_all(self):

        context = self.context
        use_selection = context.scene.type_pre_sub_only_selection

        if use_selection:
            return context.selected_objects.copy()
        else:
            return bpy.data.objects

    def rename_suffix_prefix(self, obj_list, pre_suffix='', object_type='', icon=''):
        context = self.context
        wm = context.scene
        new_name = ''

        switch_suf_pre = wm.renaming_suffix_prefix_type  # either use pre of suffix

        if pre_suffix != '':
            for ent in obj_list:
                if hasattr(ent, 'name'):
                    old_name = ent.name
                    name_is_new = True

                    if switch_suf_pre == 'SUF':
                        if not ent.name.endswith(pre_suffix):
                            new_name = suffix_prefix_add(context, ent, pre_suffix)
                        else:
                            name_is_new = False
                    else:
                        if not ent.name.startswith(pre_suffix):
                            new_name = suffix_prefix_add(context, ent, pre_suffix)
                        else:
                            name_is_new = False

                    if name_is_new:
                        ent.name = new_name
                        wm.renaming_messages.add_message(old_name, ent.name, object_type, icon)
                else:
                    # wm.renaming_messages.add_message(old_name, ent.name, objectType, 'OUTLINER_OB_EMPTY')
                    pass

    def empty(self):
        context = self.context
        wm = context.scene
        obj_list = []

        for obj in self.get_selection_all():
            if obj.type == 'EMPTY':
                obj_list.append(obj)
        self.rename_suffix_prefix(obj_list, pre_suffix=wm.renaming_suffix_prefix_empty, object_type='EMPTY',
                          icon='OUTLINER_OB_EMPTY')
        return

    def mesh(self):
        context = self.context
        wm = context.scene
        obj_list = []

        for obj in self.get_selection_all():
            if obj.type == 'MESH':
                obj_list.append(obj)
        self.rename_suffix_prefix(obj_list, pre_suffix=wm.renaming_suffix_prefix_geometry, object_type='MESH',
                          icon='OUTLINER_OB_MESH')
        return

    def material(self):
        context = self.context
        wm = context.scene
        obj_list = []

        if wm.type_pre_sub_only_selection:
            for obj in context.selected_objects:
                for mat in obj.material_slots:
                    if mat is not None and mat.name != '':
                        obj_list.append(bpy.data.materials[mat.name])
        else:
            obj_list = list(bpy.data.materials)

        self.rename_suffix_prefix(obj_list, pre_suffix=wm.renaming_suffix_prefix_material, object_type='MATERIAL',
                          icon='MATERIAL')
        return

    def speakers(self):
        context = self.context
        wm = context.scene
        obj_list = []

        for obj in self.get_selection_all():
            if obj.type == 'SPEAKER':
                obj_list.append(obj)
        self.rename_suffix_prefix(obj_list, pre_suffix=wm.renaming_suffix_prefix_speakers, object_type='SPEAKER',
                          icon='OUTLINER_OB_SPEAKER')
        return

    def lightprops(self):
        context = self.context
        wm = context.scene
        obj_list = []

        for obj in self.get_selection_all():
            if obj.type == 'LIGHT_PROBE':
                obj_list.append(obj)
        self.rename_suffix_prefix(obj_list, pre_suffix=wm.renaming_suffix_prefix_lightprops, object_type='LIGHT_PROBE',
                          icon='OUTLINER_OB_LIGHTPROBE')
        return

    def data(self):
        context = self.context
        wm = context.scene
        obj_list = []

        for obj in self.get_selection_all():
            obj_list.append(obj.data)
        self.rename_suffix_prefix(obj_list, pre_suffix=wm.renaming_suffix_prefix_data, object_type='DATA', icon='FILE_BLANK')
        return

    def camera(self):
        context = self.context
        wm = context.scene
        obj_list = []

        for obj in self.get_selection_all():
            if obj.type == 'CAMERA':
                obj_list.append(obj)
        self.rename_suffix_prefix(obj_list, pre_suffix=wm.renaming_suffix_prefix_cameras, object_type='CAMERA',
                          icon='OUTLINER_OB_CAMERA')
        return

    def light(self):
        context = self.context
        wm = context.scene
        obj_list = []

        for obj in self.get_selection_all():
            if obj.type == 'LIGHT':
                obj_list.append(obj)
        self.rename_suffix_prefix(obj_list, pre_suffix=wm.renaming_suffix_prefix_lights, object_type='LIGHT', icon='LIGHT')
        return

    def armature(self):
        context = self.context
        wm = context.scene
        obj_list = []

        for obj in self.get_selection_all():
            if obj.type == 'ARMATURE':
                obj_list.append(obj)
        self.rename_suffix_prefix(obj_list, pre_suffix=wm.renaming_suffix_prefix_armature, object_type='ARMATURE',
                          icon='OUTLINER_OB_ARMATURE')
        return

    def lattice(self):

        wm = bpy.context.scene
        obj_list = []

        for obj in self.get_selection_all():
            if obj.type == 'LATTICE':
                obj_list.append(obj)
        self.rename_suffix_prefix(obj_list, pre_suffix=wm.renaming_suffix_prefix_lattice, object_type='LATTICE',
                          icon='OUTLINER_OB_LATTICE')
        return

    def curve(self):
        context = self.context
        wm = context.scene
        obj_list = []

        for obj in self.get_selection_all():
            if obj.type == 'CURVE':
                obj_list.append(obj)
        self.rename_suffix_prefix(obj_list, pre_suffix=wm.renaming_suffix_prefix_curve, object_type='CURVE',
                          icon='OUTLINER_OB_CURVE')
        return

    def surface(self):
        context = self.context
        wm = context.scene
        obj_list = []

        for obj in self.get_selection_all():
            if obj.type == 'SURFACE':
                obj_list.append(obj)
        self.rename_suffix_prefix(obj_list, pre_suffix=wm.renaming_suffix_prefix_surfaces, object_type='SURFACE',
                          icon='OUTLINER_OB_SURFACE')
        return

    def text(self):
        context = self.context
        wm = context.scene
        obj_list = []

        for obj in self.get_selection_all():
            if obj.type == 'FONT':
                obj_list.append(obj)
        self.rename_suffix_prefix(obj_list, pre_suffix=wm.renaming_suffix_prefix_text, object_type='FONT',
                          icon='OUTLINER_OB_FONT')
        return

    def gpencil(self):
        context = self.context
        wm = context.scene
        obj_list = []

        for obj in self.get_selection_all():
            if obj.type == 'GPENCIL':
                obj_list.append(obj)
        self.rename_suffix_prefix(obj_list, pre_suffix=wm.renaming_suffix_prefix_gpencil, object_type='GPENCIL',
                          icon='OUTLINER_OB_GREASEPENCIL')
        return

    def metaball(self):
        context = self.context
        wm = context.scene
        obj_list = []

        for obj in self.get_selection_all():
            if obj.type == 'META':
                obj_list.append(obj)
        self.rename_suffix_prefix(obj_list, pre_suffix=wm.renaming_suffix_prefix_metaball, object_type='META',
                          icon='OUTLINER_OB_META')
        return

    def collection(self):
        context = self.context
        wm = context.scene
        obj_list = []

        for col in bpy.data.collections:
            obj_list.append(col)
        self.rename_suffix_prefix(obj_list, pre_suffix=wm.renaming_suffix_prefix_collection, object_type='COLLECTION',
                          icon='GROUP')
        return

    def bone(self):
        context = self.context
        wm = context.scene
        obj_list = []

        for obj in self.get_selection_all():
            if obj.type == 'ARMATURE':
                for bone in obj.data.bones:
                    obj_list.append(bone)
        self.rename_suffix_prefix(obj_list, pre_suffix=wm.renaming_suffix_prefix_bone, object_type='BONE', icon='BONE_DATA')
        return

    def all(self):
        self.empty()
        self.mesh()
        self.camera()
        self.light()
        self.armature()
        self.lattice()
        self.curve()
        self.surface()
        self.text()
        self.gpencil()
        self.metaball()
        self.collection()
        self.bone()
        self.material()
        self.data()

    def error_msg(self):
        pass

    def switch_type(self, argument):
        method = getattr(self, argument, lambda: "Invalid Type")
        return method()

    def main(self, context, object_list, is_suffix, string_extension):
        pass

    def execute(self, context):
        self.context = context

        self.switch_type(self.option)

        call_renaming_popup(context)
        return {'FINISHED'}
