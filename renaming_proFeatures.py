import bpy
from bpy.props import StringProperty

class RENAMING_MT_variableMenu(bpy.types.Menu):
    bl_label = "Renaming Variables"
    bl_idname = "renaming.mt_menu"

    def draw(self, context):
        layout = self.layout

        layout.operator("object.renaming_inuptvariables", text = 'FILE').nameingPreset = 'FILE'
        layout.operator("object.renaming_inuptvariables", text = "HIGH").nameingPreset = "HIGH"
        layout.operator("object.renaming_inuptvariables", text = "LOW").nameingPreset = "LOW"
        layout.operator("object.renaming_inuptvariables", text = 'FILE').nameingPreset = 'OBJECT'
        layout.operator("object.renaming_inuptvariables", text = "HIGH").nameingPreset = "HIGH"
        layout.operator("object.renaming_inuptvariables", text = "LOW").nameingPreset = "LOW"
        layout.operator("object.renaming_inuptvariables", text = "CAGE").nameingPreset = "CAGE"
        layout.operator("object.renaming_inuptvariables", text = "DATE").nameingPreset = "DATE"
        layout.operator("object.renaming_inuptvariables", text = "ACTIVE").nameingPreset = "ACTIVE"
        layout.operator("object.renaming_inuptvariables", text = "USER1").nameingPreset = "USER1"
        layout.operator("object.renaming_inuptvariables", text = "USER2").nameingPreset = "USER2"
        layout.operator("object.renaming_inuptvariables", text = "USER3").nameingPreset = "USER3"
        layout.operator("object.renaming_inuptvariables", text = "TIME").nameingPreset = "TIME"
        layout.operator("object.renaming_inuptvariables", text = "TYPE").nameingPreset = "TYPE"
        layout.operator("object.renaming_inuptvariables", text = "PARENT").nameingPreset = "PARENT"
        layout.operator("object.renaming_inuptvariables", text = "NUMBER").nameingPreset = "NUMBER"



class VIEW3D_OT_inputVariables(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.renaming_inuptvariables"
    bl_label = "Simple Object Operator"

    nameingPreset: StringProperty()

    def execute(self, context):
        #wm = context.scene
        #replaceName = VariableReplacer.replaceInputString(context, wm.renaming_newName)


        # The print function works fine
        nameingPreset = self.nameingPreset
        print (self.nameingPreset)
        nameVar = ""

        print('T changed to ', nameingPreset)
        if nameingPreset == 'FILE':
            nameVar = "@f"
        if nameingPreset == 'OBJECT':
            nameVar = "@o"
        if nameingPreset == "HIGH":
            nameVar = "@h"
        if nameingPreset == "LOW":
            nameVar = "@l"
        if nameingPreset == "CAGE":
            nameVar = "@c"
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
            nameVar = "@t"
        if nameingPreset == "TYPE":
            nameVar = "@y"
        if nameingPreset == "PARENT":
            nameVar = "@p"
        if nameingPreset == "NUMBER":
            nameVar = "@n"

        scn = bpy.context.scene
        if scn.renaming_inputContext == 'newName':
            bpy.context.scene.renaming_newName += str(nameVar)
        if scn.renaming_inputContext == 'prefix':
            bpy.context.scene.renaming_prefix += str(nameVar)
        if scn.renaming_inputContext == 'suffix':
            bpy.context.scene.renaming_suffix += str(nameVar)

        return {'FINISHED'}
