import bpy, re
from .renaming_utilities import getRenamingList,trimString, RENAMING_MESSAGES

from bpy.props import (
    BoolProperty,
    StringProperty,
)
from.renaming_utilities import callPopup


class VIEW3D_OT_add_type_suf_pre(bpy.types.Operator):
    """Add Type Suffix"""
    bl_idname = "renaming.add_sufpre_by_type"
    bl_label = "Add Type Suffix or Prefix"
    bl_description = "Adds the above defined Suffixes or Prefixes to all objects in your scene"
    bl_options = {'REGISTER', 'UNDO'}

    option: StringProperty()

    def getSelectionAll(self):
        useSelection = bpy.context.scene.type_pre_sub_only_selection

        if useSelection:
            return bpy.context.selected_objects.copy()
        else:
            return bpy.data.objects

    def renameSufPre(self, objList, preSuf = '', objectType = '', icon = ''):
        wm = bpy.context.scene

        switchSufPre = wm.renaming_sufpre_type # either use pre of suffix

        if preSuf is not '':
            for ent in objList:
                if hasattr(ent, 'name'):
                    oldName = ent.name
                    nameIsNew = True

                    if switchSufPre == 'SUF':
                        if ent.name.endswith(preSuf) == False:
                            newName = self.sufpreAdd(bpy.context, ent, preSuf)
                        else:
                            nameIsNew = False
                    else:
                        if ent.name.startswith(preSuf) == False:
                            newName = self.sufpreAdd(bpy.context, ent, preSuf)
                        else:
                            nameIsNew = False

                    if nameIsNew == True:
                        ent.name = newName
                        wm.renaming_messages.addMessage(oldName, ent.name, objectType, icon)
                else:
                        #wm.renaming_messages.addMessage(oldName, ent.name, objectType, 'OUTLINER_OB_EMPTY')
                        pass

    def empty(self):
        wm = bpy.context.scene
        objList = []

        for obj in self.getSelectionAll():
                if obj.type == 'EMPTY':
                    objList.append(obj)
        self.renameSufPre(objList, preSuf = wm.renaming_sufpre_empty, objectType = 'EMPTY', icon = 'OUTLINER_OB_EMPTY')
        return

    def mesh(self):
        wm = bpy.context.scene
        objList = []

        for obj in self.getSelectionAll():
                if obj.type == 'MESH':
                    objList.append(obj)
        self.renameSufPre(objList, preSuf = wm.renaming_sufpre_geometry, objectType = 'MESH', icon = 'OUTLINER_OB_MESH')
        return

    def material(self):
        wm = bpy.context.scene
        objList = []

        if wm.type_pre_sub_only_selection:
            for obj in bpy.context.selected_objects:
                for mat in obj.material_slots:
                    if mat is not None and mat.name != '':
                        objList.append(bpy.data.materials[mat.name])
        else:
            objList = list(bpy.data.materials)

        self.renameSufPre(objList, preSuf = wm.renaming_sufpre_material, objectType = 'MATERIAL', icon = 'MATERIAL')
        return

    def speakers(self):
        wm = bpy.context.scene
        objList = []

        for obj in self.getSelectionAll():
            if obj.type == 'SPEAKER':
                objList.append(obj)
        self.renameSufPre(objList, preSuf=wm.renaming_sufpre_speakers, objectType='SPEAKER', icon='OUTLINER_OB_SPEAKER')
        return

    def lightprops(self):
        wm = bpy.context.scene
        objList = []

        for obj in self.getSelectionAll():
            if obj.type == 'LIGHT_PROBE':
                objList.append(obj)
        self.renameSufPre(objList, preSuf=wm.renaming_sufpre_lightprops, objectType='LIGHT_PROBE', icon='OUTLINER_OB_LIGHTPROBE')
        return

    def data(self):
        wm = bpy.context.scene
        objList = []

        for obj in self.getSelectionAll():
            objList.append(obj.data)
        self.renameSufPre(objList, preSuf=wm.renaming_sufpre_data, objectType='DATA', icon='FILE_BLANK')
        return

    def camera(self):
        wm = bpy.context.scene
        objList = []

        for obj in self.getSelectionAll():
                if obj.type == 'CAMERA':
                    objList.append(obj)
        self.renameSufPre(objList, preSuf = wm.renaming_sufpre_cameras, objectType = 'CAMERA', icon = 'OUTLINER_OB_CAMERA')
        return

    def light(self):
        wm = bpy.context.scene
        objList = []

        for obj in self.getSelectionAll():
                if obj.type == 'LIGHT':
                    objList.append(obj)
        self.renameSufPre(objList, preSuf = wm.renaming_sufpre_lights, objectType = 'LIGHT', icon = 'LIGHT')
        return

    def armature(self):
        wm = bpy.context.scene
        objList = []

        for obj in self.getSelectionAll():
            if obj.type == 'ARMATURE':
                objList.append(obj)
        self.renameSufPre(objList, preSuf=wm.renaming_sufpre_armature, objectType='ARMATURE', icon='OUTLINER_OB_ARMATURE')
        return

    def lattice(self):

        wm = bpy.context.scene
        objList = []

        for obj in self.getSelectionAll():
            if obj.type == 'LATTICE':
                objList.append(obj)
        self.renameSufPre(objList, preSuf=wm.renaming_sufpre_lattice, objectType='LATTICE', icon='OUTLINER_OB_LATTICE')
        return

    def curve(self):
        wm = bpy.context.scene
        objList = []

        for obj in self.getSelectionAll():
            if obj.type == 'CURVE':
                objList.append(obj)
        self.renameSufPre(objList, preSuf=wm.renaming_sufpre_curve, objectType='CURVE', icon='OUTLINER_OB_CURVE')
        return

    def surface(self):
        wm = bpy.context.scene
        objList = []

        for obj in self.getSelectionAll():
            if obj.type == 'SURFACE':
                objList.append(obj)
        self.renameSufPre(objList, preSuf=wm.renaming_sufpre_surfaces, objectType='SURFACE', icon='OUTLINER_OB_SURFACE')
        return

    def text(self):
        wm = bpy.context.scene
        objList = []

        for obj in self.getSelectionAll():
            if obj.type == 'FONT':
                objList.append(obj)
        self.renameSufPre(objList, preSuf=wm.renaming_sufpre_text, objectType='FONT', icon='OUTLINER_OB_FONT')
        return

    def gpencil(self):
        wm = bpy.context.scene
        objList = []

        for obj in self.getSelectionAll():
            if obj.type == 'GPENCIL':
                objList.append(obj)
        self.renameSufPre(objList, preSuf=wm.renaming_sufpre_gpencil, objectType='GPENCIL', icon='OUTLINER_OB_GREASEPENCIL')
        return

    def metaball(self):
        wm = bpy.context.scene
        objList = []

        for obj in self.getSelectionAll():
            if obj.type == 'META':
                objList.append(obj)
        self.renameSufPre(objList, preSuf=wm.renaming_sufpre_metaball, objectType='META', icon='OUTLINER_OB_META')
        return

    def collection(self):
        wm = bpy.context.scene
        objList = []

        for col in bpy.data.collections:
            objList.append(col)
        self.renameSufPre(objList, preSuf=wm.renaming_sufpre_collection, objectType='COLLECTION', icon='GROUP')
        return

    def bone(self):
        wm = bpy.context.scene
        objList = []

        for obj in self.getSelectionAll():
            if obj.type == 'ARMATURE':
                for bone in obj.data.bones:
                    objList.append(obj)
        self.renameSufPre(objList, preSuf=wm.renaming_sufpre_bone, objectType='BONE', icon='BONE_DATA')
        return

    def errorMsg(self):
        pass

    def switch_type(self,argument):
        selection = bpy.context.selected_objects
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
            #16: 'speakers',
            #17: 'actions',
        }


        method = getattr(self, argument, lambda: "Invalid month")
        return method()

    def main(self, context, objectList, isSuffix, stringExtension):
        pass

    def execute(self, context):
        wm = context.scene
        self.switch_type(self.option)

        callPopup(context)
        return {'FINISHED'}

    def sufpreAdd(self, context, obj, sufpreName):
        wm = context.scene

        nName = obj.name
        if wm.renaming_sufpre_type == 'SUF':
            nName = nName + sufpreName
        else:
            nName = sufpreName + nName

        if nName not in bpy.data.objects:
            obj.name = nName
            return nName
        else:
            i = 1
            while (nName in bpy.data.objects):
                if wm.renaming_sufpre_type == 'SUF':
                    nName = obj.name + "_" + str(i) + sufpreName
                else:
                    nName = sufpreName + obj.name + "_" + str(i)
                i = i + 1

        obj.name = nName
        return nName

    # def suffixDataAdd(self, context, obj, sufpreName):
    #     wm = context.scene
    #
    #     nName = obj.data.name
    #     if wm.renaming_sufpre_type == 'SUF':
    #         nName = nName + sufpreName
    #     else:
    #         nName = sufpreName + nName
    #
    #     if nName not in bpy.data.meshes and nName not in bpy.data.lattices and nName not in bpy.data.curves and nName not in bpy.data.METABALL:
    #         obj.data.name = nName
    #         return nName
    #     else:
    #         i = 1
    #         while (
    #                 nName in bpy.data.meshes or nName in bpy.data.lattices or nName in bpy.data.curves or nName in bpy.data.METABALL):
    #             nName = obj.data.name + "_" + str(i)
    #             i = i + 1
    #         return nName

    # def sufpreMatAdd(self, context, mat, sufpreName):
    #     wm = context.scene
    #     nName = mat.name
    #     if wm.renaming_sufpre_type == 'SUF':
    #         nName = nName + sufpreName
    #     else:
    #         nName = sufpreName + nName
    #
    #     if nName not in bpy.data.materials:
    #         mat.name = nName
    #         return nName
    #     else:
    #         i = 1
    #         while (nName in bpy.data.materials):
    #             nName = mat.name + "_" + str(i)
    #             i = i + 1
    #         return nName

    # def suffixGrpAdd(self, context, grp, sufpreName):
    #     scene = context.scene
    #
    #     nName = grp.name
    #     if scene.renaming_sufpre_type == 'SUF':
    #         nName = nName + sufpreName
    #     else:
    #         nName = sufpreName + nName
    #
    #     if nName not in bpy.data.groups:
    #         grp.name = nName
    #         return nName
    #     else:
    #         i = 1
    #         while( nName in bpy.data.groups):
    #             nName = grp.name + "_" + str(i)
    #             i = i + 1
    #         return nName

    # def suffixArmAdd(self, context, arm, sufpreName):
    #     wm = context.scene
    #
    #     nName = arm.name
    #     if wm.renaming_sufpre_type == 'SUF':
    #         nName = nName + sufpreName
    #     else:
    #         nName = sufpreName + nName
    #
    #     if nName not in bpy.data.armatures:
    #         arm.name = nName
    #         return nName
    #     else:
    #         i = 1
    #         while (nName in bpy.data.armatures):
    #             nName = arm.name + "_" + str(i)
    #             i = i + 1
    #         return nName
