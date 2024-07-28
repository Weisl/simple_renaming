import bpy
from bpy.props import StringProperty


class RENAMING_MT_variableMenu(bpy.types.Menu):
    bl_label = "Renaming Variables"
    bl_idname = "MENU_MT_renaming_variables"

    def draw(self, context):
        layout = self.layout

        wm = bpy.context.scene

        layout.operator("object.renaming_multivariables", text="RANDOM").renaming_variables = "RANDOM"
        layout.operator("object.renaming_multivariables", text="NUMBER").renaming_variables = "NUMBER"
        layout.separator()
        layout.operator("object.renaming_multivariables", text="LOW").renaming_variables = "LOW"
        layout.operator("object.renaming_multivariables", text="HIGH").renaming_variables = "HIGH"
        layout.operator("object.renaming_multivariables", text="CAGE").renaming_variables = "CAGE"
        layout.separator()
        layout.operator("object.renaming_multivariables", text='FILE').renaming_variables = 'FILE'
        layout.operator("object.renaming_multivariables", text="TIME").renaming_variables = "TIME"
        layout.operator("object.renaming_multivariables", text="DATE").renaming_variables = "DATE"
        layout.separator()
        layout.operator("object.renaming_multivariables", text="USER1").renaming_variables = "USER1"
        layout.operator("object.renaming_multivariables", text="USER2").renaming_variables = "USER2"
        layout.operator("object.renaming_multivariables", text="USER3").renaming_variables = "USER3"

        if wm.renaming_object_types == 'OBJECT':
            layout.separator()
            layout.operator("object.renaming_multivariables", text="PARENT").renaming_variables = "PARENT"
            layout.operator("object.renaming_multivariables", text="DATA").renaming_variables = "DATA"
            layout.operator("object.renaming_multivariables", text="ACTIVE").renaming_variables = "ACTIVE"
            layout.operator("object.renaming_multivariables", text='FILE').renaming_variables = 'OBJECT'
            layout.operator("object.renaming_multivariables", text="TYPE").renaming_variables = "TYPE"
            layout.operator("object.renaming_multivariables", text="COLLECTION").renaming_variables = "COLLECTION"


class VIEW3D_OT_inputVariables(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.renaming_multivariables"
    bl_label = "Simple Object Operator"

    renaming_variables: StringProperty()

    def execute(self, context):
        # wm = context.scene
        # replaceName = VariableReplacer.replaceInputString(context, wm.renaming_newName)

        # The print function works fine
        renaming_variables = self.renaming_variables
        # print (self.renaming_variables)
        name_var = ""

        # print('T changed to ', renaming_variables)
        if renaming_variables == 'FILE':
            name_var = "@f"
        if renaming_variables == 'OBJECT':
            name_var = "@o"
        if renaming_variables == "HIGH":
            name_var = "@h"
        if renaming_variables == "LOW":
            name_var = "@l"
        if renaming_variables == "CAGE":
            name_var = "@b"
        if renaming_variables == "DATE":
            name_var = "@d"
        if renaming_variables == "ACTIVE":
            name_var = "@a"
        if renaming_variables == "USER1":
            name_var = "@u1"
        if renaming_variables == "USER2":
            name_var = "@u2"
        if renaming_variables == "USER3":
            name_var = "@u3"
        if renaming_variables == "TIME":
            name_var = "@i"
        if renaming_variables == "TYPE":
            name_var = "@t"
        if renaming_variables == "PARENT":
            name_var = "@p"
        if renaming_variables == "DATA":
            name_var = "@m"
        if renaming_variables == "NUMBER":
            name_var = "@n"
        if renaming_variables == "RANDOM":
            name_var = "@r"
        if renaming_variables == "COLLECTION":
            name_var = "@c"

        scn = context.scene
        if scn.renaming_inputContext == 'newName':
            context.scene.renaming_newName += str(name_var)
        if scn.renaming_inputContext == 'prefix':
            context.scene.renaming_prefix += str(name_var)
        if scn.renaming_inputContext == 'suffix':
            context.scene.renaming_suffix += str(name_var)
        if scn.renaming_inputContext == 'search':
            context.scene.renaming_search += str(name_var)
        if scn.renaming_inputContext == 'replace':
            context.scene.renaming_replace += str(name_var)

        return {'FINISHED'}
