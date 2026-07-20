import bpy


class VIEW3D_PT_error_popup(bpy.types.Panel):
    """Tooltip"""
    bl_idname = "POPUP_PT_error"
    bl_label = "Renaming Info"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_ui_units_x = 30

    def draw(self, context):

        layout = self.layout
        box = layout.box()
        wm = context.scene

        messages = wm.renaming_error_messages

        if len(messages.message) <= 0:
            box.label(text="Unknown Error", icon="INFO")
        else:
            for msg in messages.message:
                if msg is not None:
                    row = box.row(align=False)
                    # row.alignment = 'EXPAND'

                    if msg['isError']:
                        row.label(text=str('Error'), icon='ERROR')
                        row = box.row(align=False)
                        row.label(text=str(msg['message']), icon='ERROR')
                    else:
                        row.label(text=str('Warning'), icon='ERROR')
                        row = box.row(align=False)
                        row.label(text=str(msg['message']), icon='CANCEL')

        messages.clear()
        return


class VIEW3D_PT_info_popup(bpy.types.Panel):
    """Tooltip"""
    bl_idname = "POPUP_PT_info"
    bl_label = "Renaming Info"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_ui_units_x = 30

    def draw(self, context):

        layout = self.layout

        box = layout.box()
        wm = context.scene
        infos = wm.renaming_info_messages

        if len(infos.message) <= 0:
            box.label(text="No Objects Validated", icon="INFO")
        else:
            i = 0
            for msg in infos.message:
                if msg is not None:
                    if msg['message'] is not None:

                        row = box.row(align=True)
                        row.alignment = 'EXPAND'

                        if msg['obType'] is not False and msg['obIcon'] is not False:
                            row.label(text=str(msg['obType']), icon=msg['obIcon'])
                            # row.label(text = str(msg['obType']), icon = 'INFO')
                        else:
                            row.label(text=str(wm.renaming_object_types))

                        row.label(text=str(msg['assetName']), icon='FILE_TICK')
                        row.label(text=str(msg['oldName']))

                        i += 1

        infos.clear()


class VIEW3D_PT_renaming_popup(bpy.types.Panel):
    """Tooltip"""
    bl_idname = "POPUP_PT_popup"
    bl_label = "Renaming Info"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_ui_units_x = 30

    def draw(self, context):
        wm = context.scene

        layout = self.layout
        box = layout.box()

        messages = [m for m in wm.renaming_messages.message if m is not None]
        warnings = [m for m in messages if m['warning']]

        if len(messages) <= 0:
            box.label(text="No Objects Renamed", icon="INFO")
        else:
            i = 0
            for msg in messages:
                if not msg['warning']:
                    if (msg['new_name'] is not None and msg['oldName'] is not None) and msg['oldName'] != msg[
                        'new_name']:

                        if i == 0:
                            row = box.row(align=True)
                            row.alignment = 'EXPAND'
                            row.label(text="Object Type")
                            row.label(text="New Name")
                            row.label(text="Old Name")
                            box.separator(type='LINE')

                        row = box.row(align=True)
                        row.alignment = 'EXPAND'

                        if msg['obType'] is not False and msg['obIcon'] is not False:
                            row.label(text=str(msg['obType']), icon=msg['obIcon'])
                        else:
                            row.label(text=str(wm.renaming_object_types))

                        row.label(text=str(msg['new_name']), icon='FILE_TICK')
                        row.label(text=str(msg['oldName']))

                        i += 1

            if warnings:
                if i > 0:
                    box.separator(type='LINE')

                # Skipped entities were left at their original name (see
                # apply_rename), so there's no separate "current name" to
                # show — oldName and new_name are always identical here.
                skipped = [m for m in warnings if m['oldName'] is not None]
                general = [m for m in warnings if m['oldName'] is None]

                if skipped:
                    box.label(text="Skipped (Name Conflicts)", icon='ERROR')
                    for msg in skipped:
                        row = box.row(align=True)
                        row.label(text=str(msg['oldName']), icon='ERROR')
                        row.label(text=str(msg['warning']))

                for msg in general:
                    row = box.row(align=True)
                    row.label(text=str(msg['warning']), icon='ERROR')

            if i == 0 and not warnings:
                box.label(text="No Objects Renamed", icon="INFO")
        wm.renaming_messages.clear()
