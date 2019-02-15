import bpy
from .renaming_utilities import getRenamingList,trimString

class VIEW3D_OT_renaming_popup(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "renaming.popup"
    bl_label = "Renaming Panel"

    message: bpy.props.StringProperty(
        name="message",
        description="message",
        default=''
    )
    @classmethod
    def poll(cls, context):
        user_preferences = context.preferences
        addon_prefs = user_preferences.addons[__name__].preferences
        return addon_prefs.renamingPanel_showPopup

    def execute(self, context):
        # self.report({'INFO'}, self.message)
        print(self.message)
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=600)

    def draw(self, context):
        wm = bpy.context.scene
        layout = self.layout
        box = layout.box()

        if len(wm.renaming_messages.message) <= 0:
            box.label(text="No Objects Renamed", icon="INFO")
        else:
            i = 0
            for msg in wm.renaming_messages.message:
                if msg is not None:
                    if msg['warning'] == False:
                        if (msg['newName'] is not None and msg['oldName'] is not None) and msg['oldName'] != msg[
                            'newName']:

                            if i == 0:
                                row = box.row(align=True)
                                row.alignment = 'EXPAND'
                                row.label(text="OBJECT TYPE")
                                row.label(text="NEW NAME")
                                row.label(text="OLD NAME")
                                row.separator()

                            row = box.row(align=True)
                            row.alignment = 'EXPAND'

                            if msg['obType'] is not False and msg['obIcon'] is not False:
                                row.label(text=str(msg['obType']), icon=msg['obIcon'])
                                # row.label(text = str(msg['obType']), icon = 'INFO')
                            else:
                                row.label(text=str(wm.renaming_object_types))

                            row.label(text=str(msg['newName']), icon='FILE_TICK')
                            row.label(text=str(msg['oldName']))

                            i += 1

                    else:
                        if msg['newName'] is not None and msg['oldName'] is not None:
                            box.label(text="Warning", icon="ERROR")
                            box.label(text="       " + "Name: " + str(msg['oldName']))
                            box.label(text="       " + msg['warning'])
                        else:
                            box.label(text="Warning", icon="ERROR")
                            box.label(text="       " + msg['warning'])
            if i == 0:
                box.label(text="No Objects Renamed", icon="INFO")
        wm.renaming_messages.clear()

