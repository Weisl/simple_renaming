import bpy
from bpy.props import (
    StringProperty,
)

from ..operators.renaming_utilities import callRenamingPopup


class VIEW3D_OT_add_type_suf_pre(bpy.types.Operator):
    """Add Type Suffix"""
    bl_idname = "renaming.add_suffix_prefix_by_type"
    bl_label = "Add Type Suffix or Prefix"
    bl_description = "Adds the above defined Suffixes or Prefixes to all objects in your scene"
    bl_options = {'REGISTER', 'UNDO'}

    option: StringProperty()

    def getSelectionAll(self):

        context = self.context
        useSelection = context.scene.type_pre_sub_only_selection

        if useSelection:
            return context.selected_objects.copy()
        else:
            return bpy.data.objects

    def renameSufPre(self, obj_list, pre_suffix='', object_type='', icon=''):
        context = self.context
        wm = context.scene

        switch_suf_pre = wm.renaming_suffix_prefix_type  # either use pre of suffix

        if pre_suffix != '':
            for ent in obj_list:
                if hasattr(ent, 'name'):
                    old_name = ent.name
                    name_is_new = True

                    if switch_suf_pre == 'SUF':
                        if not ent.name.endswith(pre_suffix):
                            new_name = self.sufpreAdd(context, ent, pre_suffix)
                        else:
                            name_is_new = False
                    else:
                        if not ent.name.startswith(pre_suffix):
                            new_name = self.sufpreAdd(context, ent, pre_suffix)
                        else:
                            name_is_new = False

                    if name_is_new:
                        ent.name = new_name
                        wm.renaming_messages.addMessage(old_name, ent.name, object_type, icon)
                else:
                    # wm.renaming_messages.addMessage(old_name, ent.name, objectType, 'OUTLINER_OB_EMPTY')
                    pass

    def empty(self):
        context = self.context
        wm = context.scene
        obj_list = []

        for obj in self.getSelectionAll():
            if obj.type == 'EMPTY':
                obj_list.append(obj)
        self.renameSufPre(obj_list, pre_suffix=wm.renaming_suffix_prefix_empty, object_type='EMPTY',
                          icon='OUTLINER_OB_EMPTY')
        return

    def mesh(self):
        context = self.context
        wm = context.scene
        obj_list = []

        for obj in self.getSelectionAll():
            if obj.type == 'MESH':
                obj_list.append(obj)
        self.renameSufPre(obj_list, pre_suffix=wm.renaming_suffix_prefix_geometry, object_type='MESH',
                          icon='OUTLINER_OB_MESH')
        return

    def material(self):
        context = self.context
        wm = context.scene
        obj_list = []

        if wm.type_pre_sub_only_selection:
            for obj in context.selected_objects:
                for mat in obj.material_slots:
                    if mat != None and mat.name != '':
                        obj_list.append(bpy.data.materials[mat.name])
        else:
            obj_list = list(bpy.data.materials)

        self.renameSufPre(obj_list, pre_suffix=wm.renaming_suffix_prefix_material, object_type='MATERIAL',
                          icon='MATERIAL')
        return

    def speakers(self):
        context = self.context
        wm = context.scene
        objList = []

        for obj in self.getSelectionAll():
            if obj.type == 'SPEAKER':
                objList.append(obj)
        self.renameSufPre(objList, pre_suffix=wm.renaming_suffix_prefix_speakers, object_type='SPEAKER',
                          icon='OUTLINER_OB_SPEAKER')
        return

    def lightprops(self):
        context = self.context
        wm = context.scene
        objList = []

        for obj in self.getSelectionAll():
            if obj.type == 'LIGHT_PROBE':
                objList.append(obj)
        self.renameSufPre(objList, pre_suffix=wm.renaming_suffix_prefix_lightprops, object_type='LIGHT_PROBE',
                          icon='OUTLINER_OB_LIGHTPROBE')
        return

    def data(self):
        context = self.context
        wm = context.scene
        objList = []

        for obj in self.getSelectionAll():
            objList.append(obj.data)
        self.renameSufPre(objList, pre_suffix=wm.renaming_suffix_prefix_data, object_type='DATA', icon='FILE_BLANK')
        return

    def camera(self):
        context = self.context
        wm = context.scene
        objList = []

        for obj in self.getSelectionAll():
            if obj.type == 'CAMERA':
                objList.append(obj)
        self.renameSufPre(objList, pre_suffix=wm.renaming_suffix_prefix_cameras, object_type='CAMERA',
                          icon='OUTLINER_OB_CAMERA')
        return

    def light(self):
        context = self.context
        wm = context.scene
        objList = []

        for obj in self.getSelectionAll():
            if obj.type == 'LIGHT':
                objList.append(obj)
        self.renameSufPre(objList, pre_suffix=wm.renaming_suffix_prefix_lights, object_type='LIGHT', icon='LIGHT')
        return

    def armature(self):
        context = self.context
        wm = context.scene
        objList = []

        for obj in self.getSelectionAll():
            if obj.type == 'ARMATURE':
                objList.append(obj)
        self.renameSufPre(objList, pre_suffix=wm.renaming_suffix_prefix_armature, object_type='ARMATURE',
                          icon='OUTLINER_OB_ARMATURE')
        return

    def lattice(self):

        wm = bpy.context.scene
        objList = []

        for obj in self.getSelectionAll():
            if obj.type == 'LATTICE':
                objList.append(obj)
        self.renameSufPre(objList, pre_suffix=wm.renaming_suffix_prefix_lattice, object_type='LATTICE',
                          icon='OUTLINER_OB_LATTICE')
        return

    def curve(self):
        context = self.context
        wm = context.scene
        objList = []

        for obj in self.getSelectionAll():
            if obj.type == 'CURVE':
                objList.append(obj)
        self.renameSufPre(objList, pre_suffix=wm.renaming_suffix_prefix_curve, object_type='CURVE',
                          icon='OUTLINER_OB_CURVE')
        return

    def surface(self):
        context = self.context
        wm = context.scene
        objList = []

        for obj in self.getSelectionAll():
            if obj.type == 'SURFACE':
                objList.append(obj)
        self.renameSufPre(objList, pre_suffix=wm.renaming_suffix_prefix_surfaces, object_type='SURFACE',
                          icon='OUTLINER_OB_SURFACE')
        return

    def text(self):
        context = self.context
        wm = context.scene
        objList = []

        for obj in self.getSelectionAll():
            if obj.type == 'FONT':
                objList.append(obj)
        self.renameSufPre(objList, pre_suffix=wm.renaming_suffix_prefix_text, object_type='FONT',
                          icon='OUTLINER_OB_FONT')
        return

    def gpencil(self):
        context = self.context
        wm = context.scene
        objList = []

        for obj in self.getSelectionAll():
            if obj.type == 'GPENCIL':
                objList.append(obj)
        self.renameSufPre(objList, pre_suffix=wm.renaming_suffix_prefix_gpencil, object_type='GPENCIL',
                          icon='OUTLINER_OB_GREASEPENCIL')
        return

    def metaball(self):
        context = self.context
        wm = context.scene
        objList = []

        for obj in self.getSelectionAll():
            if obj.type == 'META':
                objList.append(obj)
        self.renameSufPre(objList, pre_suffix=wm.renaming_suffix_prefix_metaball, object_type='META',
                          icon='OUTLINER_OB_META')
        return

    def collection(self):
        context = self.context
        wm = context.scene
        objList = []

        for col in bpy.data.collections:
            objList.append(col)
        self.renameSufPre(objList, pre_suffix=wm.renaming_suffix_prefix_collection, object_type='COLLECTION',
                          icon='GROUP')
        return

    def bone(self):
        context = self.context
        wm = context.scene
        objList = []

        for obj in self.getSelectionAll():
            if obj.type == 'ARMATURE':
                for bone in obj.data.bones:
                    objList.append(obj)
        self.renameSufPre(objList, pre_suffix=wm.renaming_suffix_prefix_bone, object_type='BONE', icon='BONE_DATA')
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

    def errorMsg(self):
        pass

    def switch_type(self, argument):
        context = self.context
        selection = context.selected_objects
        all = bpy.data.objects

        switcher = {
            1: 'empty',
            2: 'mesh',
            3: 'camera',
            4: 'light',
            5: 'armature',
            6: 'lattice',
            7: 'curve',
            8: 'surface',
            9: 'text',
            10: 'gpencil',
            11: 'metaball',
            12: 'collection',
            13: 'bone',
            14: 'material',
            15: 'data',
            16: 'all',
            # 17: 'actions',
        }

        method = getattr(self, argument, lambda: "Invalid month")
        return method()

    def main(self, context, objectList, isSuffix, stringExtension):
        pass

    def execute(self, context):
        self.context = context

        wm = context.scene
        self.switch_type(self.option)

        callRenamingPopup(context)
        return {'FINISHED'}

    def sufpreAdd(self, context, obj, sufpreName):
        wm = context.scene

        nName = obj.name
        if wm.renaming_suffix_prefix_type == 'SUF':
            nName = nName + sufpreName
        else:
            nName = sufpreName + nName

        if nName not in bpy.data.objects:
            obj.name = nName
            return nName
        else:
            i = 1
            while (nName in bpy.data.objects):
                if wm.renaming_suffix_prefix_type == 'SUF':
                    nName = obj.name + "_" + str(i) + sufpreName
                else:
                    nName = sufpreName + obj.name + "_" + str(i)
                i = i + 1

        obj.name = nName
        return nName
