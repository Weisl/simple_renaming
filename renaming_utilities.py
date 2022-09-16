import bpy
from bpy.app.handlers import persistent
from bpy.types import PoseBone, EditBone


def trimString(string, size):
    list1 = string
    list2 = list1[:-size]
    return ''.join(list2)


def getRenamingList(context, overrideSelection=False):
    scene = context.scene
    renamingList = []
    switchEditMode = False

    onlySelection = scene.renaming_only_selection
    if overrideSelection == True:
        onlySelection = False

    if scene.renaming_object_types == 'OBJECT':
        if onlySelection == True:
            ordered_selection = get_ordered_selection_objects()
            for obj in ordered_selection:
                if obj.type in scene.renaming_object_types_specified:
                    renamingList.append(obj)
        else:
            for obj in bpy.data.objects:
                if obj.type in scene.renaming_object_types_specified:
                    renamingList.append(obj)

    elif scene.renaming_object_types == 'DATA':
        if onlySelection == True:
            for obj in context.selected_objects:
                if obj.data not in renamingList:
                    renamingList.append(obj.data)
        else:
            for obj in bpy.data.objects:
                if obj.data not in renamingList:
                    renamingList.append(obj.data)

    elif scene.renaming_object_types == 'MATERIAL':
        if onlySelection == True:
            for obj in context.selected_objects:
                for mat in obj.material_slots:
                    if mat is not None and mat.name != '':
                        renamingList.append(bpy.data.materials[mat.name])
        else:
            renamingList = list(bpy.data.materials)

    elif scene.renaming_object_types == 'IMAGE':
        renamingList = list(bpy.data.images)

    elif scene.renaming_object_types == 'BONE':
        modeOld = context.mode

        if onlySelection == True:

            selection_and_active = context.selected_objects.copy()
            if context.object not in selection_and_active:
                selection_and_active.append(context.object)

            selectedBones = []

            if modeOld == 'OBJECT':
                errorMsg = "Renaming only selected Bones is only supported for EDIT and POSE mode by now."
                return None, None, errorMsg

            elif modeOld == 'POSE':
                selectedBones = context.selected_pose_bones.copy()

            else:  # if modeOld == 'EDIT_ARMATURE'
                selectedBones = context.selected_editable_bones.copy()
                switchEditMode = True

            armatures = []
            for obj in selection_and_active:
                if obj.type == 'ARMATURE':
                    armatures.append(obj.data)

            # TODO: Save armature for bones
            for selected_bone in selectedBones:
                for arm in armatures:
                    if modeOld == 'POSE':
                        name = selected_bone.name
                        for bone in arm.bones:
                            if name == bone.name:
                                newBone = PoseBone(arm.bones[name])
                                renamingList.append(newBone)
                    else:  # modeOld == 'EDIT_ARMATURE':
                        for bone in arm.edit_bones:
                            if selected_bone == bone:
                                newBone = EditBone(selected_bone)
                                renamingList.append(newBone)

        else:  # if onlySelection == False
            for arm in bpy.data.armatures:
                if modeOld == 'EDIT_ARMATURE':
                    for bone in arm.edit_bones:
                        newBone = EditBone(bone)
                        renamingList.append(newBone)
                else:  # modeOld == 'POSE' or modeOld == 'OBJECT'
                    for bone in arm.bones:
                        newBone = PoseBone(bone)
                        renamingList.append(newBone)

    elif scene.renaming_object_types == 'COLLECTION':
        if bpy.context.space_data.type == 'OUTLINER' and onlySelection == True:
            selected_collections = [c for c in context.selected_ids if c.bl_rna.identifier == "Collection"]
            for col in selected_collections:
                renamingList.append(col)
        else:
            renamingList = list(bpy.data.collections)

    elif scene.renaming_object_types == 'SHAPEKEYS':
        if onlySelection == True:
            for obj in context.selected_objects:
                for shape in obj.data.shape_keys.key_blocks:
                    renamingList.append(shape)
        else:  # onlySelection == False:
            for key_grp in bpy.data.shape_keys:
                for key in key_grp.key_blocks:
                    renamingList.append(key)

    elif context.scene.renaming_object_types == 'VERTEXGROUPS':
        if onlySelection == True:
            for obj in context.selected_objects:
                for vtx in obj.vertex_groups:
                    renamingList.append(vtx)
        else:
            for obj in bpy.data.objects:
                for vtx in obj.vertex_groups:
                    renamingList.append(vtx)

    elif context.scene.renaming_object_types == 'UVMAPS':
        obj_list = context.selected_objects.copy() if onlySelection == True else bpy.data.objects

        for obj in obj_list:
            if obj.type != 'MESH':
                continue
            for uv in obj.data.uv_layers:
                renamingList.append(uv)

    elif context.scene.renaming_object_types == 'FACEMAPS':
        obj_list = context.selected_objects.copy() if onlySelection == True else bpy.data.objects

        for obj in obj_list:
            if obj.type != 'MESH':
                continue
            for face_map in obj.face_maps:
                renamingList.append(face_map)

    elif context.scene.renaming_object_types == 'COLORATTRIBUTES':
        obj_list = context.selected_objects.copy() if onlySelection == True else bpy.data.objects

        for obj in obj_list:
            if obj.type != 'MESH':
                continue
            for color_attribute in obj.data.color_attributes:
                renamingList.append(color_attribute)

    elif context.scene.renaming_object_types == 'ATTRIBUTES':
        obj_list = context.selected_objects.copy() if onlySelection == True else bpy.data.objects

        for obj in obj_list:
            if obj.type != 'MESH':
                continue
            for attribute in obj.data.attributes:
                renamingList.append(attribute)

    elif scene.renaming_object_types == 'ACTIONS':
        renamingList = list(bpy.data.actions)

    # renamingList.sort(key=lambda x: x.name, reverse=False)
    return renamingList, switchEditMode, None


def callRenamingPopup(context):
    preferences = context.preferences
    addon_prefs = preferences.addons[__package__].preferences

    if addon_prefs.renamingPanel_showPopup == True:
        bpy.ops.wm.call_panel(name="POPUP_PT_popup")
    return


def callInfoPopup(context):
    bpy.ops.wm.call_panel(name="POPUP_PT_info")
    return


def callErrorPopup(context):
    bpy.ops.wm.call_panel(name="POPUP_PT_error")
    return


def get_ordered_selection_objects():
    tagged_objects = []
    for o in bpy.data.objects:
        order_index = o.get("selection_order", -1)
        if order_index >= 0:
            tagged_objects.append((order_index, o))
    tagged_objects = sorted(tagged_objects, key=lambda item: item[0])
    return [o for i, o in tagged_objects]


def clear_order_flag(obj):
    try:
        del obj["selection_order"]
    except KeyError:
        pass


def update_selection_order():
    if not bpy.context.selected_objects:
        for o in bpy.data.objects:
            clear_order_flag(o)
        return
    selection_order = get_ordered_selection_objects()
    idx = 0
    for o in selection_order:
        if not o.select_get():
            selection_order.remove(o)
            clear_order_flag(o)
        else:
            o["selection_order"] = idx
            idx += 1
    for o in bpy.context.selected_objects:
        if o not in selection_order:
            o["selection_order"] = len(selection_order)
            selection_order.append(o)


# persistent is needed for handler to work in addons https://docs.blender.org/api/current/bpy.app.handlers.html
@persistent
def PostChange(scene):
    if bpy.context.mode != "OBJECT":
        return
    is_selection_update = any(
        not u.is_updated_geometry
        and not u.is_updated_transform
        and not u.is_updated_shading
        for u in bpy.context.view_layer.depsgraph.updates
    )
    if is_selection_update:
        update_selection_order()


def register():
    bpy.app.handlers.depsgraph_update_post.append(PostChange)


def unregister():
    bpy.app.handlers.depsgraph_update_post.remove(PostChange)
