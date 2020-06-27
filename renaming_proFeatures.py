import bpy
from bpy.props import StringProperty


class RENAMING_MT_variableMenu(bpy.types.Menu):
    bl_label = "Renaming Variables"
    bl_idname = "MENU_MT_renaming_variables"

    def draw(self, context):
        layout = self.layout

        wm = bpy.context.scene

        layout.operator("object.renaming_inuptvariables", text="RANDOM").nameingPreset = "RANDOM"
        layout.operator("object.renaming_inuptvariables", text="NUMBER").nameingPreset = "NUMBER"
        layout.separator()
        layout.operator("object.renaming_inuptvariables", text="LOW").nameingPreset = "LOW"
        layout.operator("object.renaming_inuptvariables", text="HIGH").nameingPreset = "HIGH"
        layout.operator("object.renaming_inuptvariables", text="CAGE").nameingPreset = "CAGE"
        layout.separator()
        layout.operator("object.renaming_inuptvariables", text='FILE').nameingPreset = 'FILE'
        layout.operator("object.renaming_inuptvariables", text="TIME").nameingPreset = "TIME"
        layout.operator("object.renaming_inuptvariables", text="DATE").nameingPreset = "DATE"
        layout.separator()
        layout.operator("object.renaming_inuptvariables", text="USER1").nameingPreset = "USER1"
        layout.operator("object.renaming_inuptvariables", text="USER2").nameingPreset = "USER2"
        layout.operator("object.renaming_inuptvariables", text="USER3").nameingPreset = "USER3"

        if wm.renaming_object_types == 'OBJECT':
            layout.separator()
            layout.operator("object.renaming_inuptvariables", text="PARENT").nameingPreset = "PARENT"
            layout.operator("object.renaming_inuptvariables", text="ACTIVE").nameingPreset = "ACTIVE"
            layout.operator("object.renaming_inuptvariables", text='FILE').nameingPreset = 'OBJECT'
            layout.operator("object.renaming_inuptvariables", text="TYPE").nameingPreset = "TYPE"
            layout.operator("object.renaming_inuptvariables", text="COLLECTION").nameingPreset = "COLLECTION"


class VIEW3D_OT_inputVariables(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.renaming_inuptvariables"
    bl_label = "Simple Object Operator"

    nameingPreset: StringProperty()

    def execute(self, context):
        # wm = context.scene
        # replaceName = VariableReplacer.replaceInputString(context, wm.renaming_newName)

        # The print function works fine
        nameingPreset = self.nameingPreset
        # print (self.nameingPreset)
        nameVar = ""

        # print('T changed to ', nameingPreset)
        if nameingPreset == 'FILE':
            nameVar = "@f"
        if nameingPreset == 'OBJECT':
            nameVar = "@o"
        if nameingPreset == "HIGH":
            nameVar = "@h"
        if nameingPreset == "LOW":
            nameVar = "@l"
        if nameingPreset == "CAGE":
            nameVar = "@b"
        if nameingPreset == "DATE":
            nameVar = "@d"
        if nameingPreset == "ACTIVE":
            nameVar = "@a"
        if nameingPreset == "USER1":
            nameVar = "@u1"
        if nameingPreset == "USER2":
            nameVar = "@u2"
        if nameingPreset == "USER3":
            nameVar = "@u3"
        if nameingPreset == "TIME":
            nameVar = "@i"
        if nameingPreset == "TYPE":
            nameVar = "@t"
        if nameingPreset == "PARENT":
            nameVar = "@p"
        if nameingPreset == "NUMBER":
            nameVar = "@n"
        if nameingPreset == "RANDOM":
            nameVar = "@r"
        if nameingPreset == "COLLECTION":
            nameVar = "@c"

        scn = context.scene
        if scn.renaming_inputContext == 'newName':
            context.scene.renaming_newName += str(nameVar)
        if scn.renaming_inputContext == 'prefix':
            context.scene.renaming_prefix += str(nameVar)
        if scn.renaming_inputContext == 'suffix':
            context.scene.renaming_suffix += str(nameVar)
        if scn.renaming_inputContext == 'search':
            context.scene.renaming_search += str(nameVar)
        if scn.renaming_inputContext == 'replace':
            context.scene.renaming_replace += str(nameVar)

        return {'FINISHED'}


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

    context.scene.renaming_newName += str(nameVar)
