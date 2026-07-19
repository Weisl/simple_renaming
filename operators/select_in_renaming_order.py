import math

import blf
import bpy
import gpu
from bpy_extras import view3d_utils
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
from mathutils.geometry import intersect_point_line

from .renaming_utilities import SELECTION_ORDER_KEY

HUD_TITLE = "Select in Renaming Order"
HUD_ROWS = (
    ("LMB", "Assign next order"),
    ("Enter", "Confirm"),
    ("Esc / RMB", "Cancel"),
)

COLOR_BACKDROP = (0.0, 0.0, 0.0, 0.6)
COLOR_TITLE = (1.0, 0.85, 0.2, 1.0)
COLOR_KEY = (1.0, 1.0, 1.0, 1.0)
COLOR_LABEL = (0.75, 0.75, 0.75, 1.0)
COLOR_COUNT = (0.6, 1.0, 0.6, 1.0)
COLOR_BADGE = (0.9, 0.45, 0.05, 0.95)
COLOR_BADGE_TEXT = (1.0, 1.0, 1.0, 1.0)

BONE_PICK_RADIUS_PX = 20


def _status_text(count):
    return f"Click in order ({count} assigned)  |  Enter: confirm  |  Esc/Right-click: cancel"


def _draw_tris(vertices, indices, color):
    shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'TRIS', {"pos": vertices}, indices=indices)
    gpu.state.blend_set('ALPHA')
    shader.bind()
    shader.uniform_float("color", color)
    batch.draw(shader)
    gpu.state.blend_set('NONE')


def _draw_box(left, right, bottom, top, color):
    vertices = ((left, bottom), (right, bottom), (left, top), (right, top))
    indices = ((0, 1, 2), (2, 1, 3))
    _draw_tris(vertices, indices, color)


def _draw_circle(center, radius, color, segments=20):
    verts = [center] + [
        (center[0] + radius * math.cos(2 * math.pi * i / segments),
         center[1] + radius * math.sin(2 * math.pi * i / segments))
        for i in range(segments + 1)
    ]
    indices = [(0, i, i + 1) for i in range(1, segments + 1)]
    _draw_tris(verts, indices, color)


def _dist_point_to_segment(p, a, b):
    if (a - b).length < 1e-6:
        return (p - a).length
    closest, t = intersect_point_line(p, a, b)
    t = max(0.0, min(1.0, t))
    closest = a + (b - a) * t
    return (p - closest).length


def _draw_viewport_hud(op, context):
    area = context.area
    font_id = 0
    ui_scale = context.preferences.view.ui_scale

    title_size = round(24 * ui_scale)
    body_size = round(20 * ui_scale)
    line_height = round(body_size * 1.8)
    key_col_width = round(130 * ui_scale)
    padding = round(20 * ui_scale)

    rows = [(f"{len(op._ordered)} {op._item_label}(s) ordered", None)] + list(HUD_ROWS)

    box_width = round(420 * ui_scale)
    box_height = padding * 2 + title_size + len(rows) * line_height
    center_x = area.width / 2
    box_left = center_x - box_width / 2
    box_right = center_x + box_width / 2
    box_bottom = round(10 * ui_scale)
    box_top = box_bottom + box_height

    _draw_box(box_left, box_right, box_bottom, box_top, COLOR_BACKDROP)

    text_left = box_left + padding
    y = box_top - padding - title_size

    blf.size(font_id, title_size)
    blf.color(font_id, *COLOR_TITLE)
    blf.position(font_id, text_left, y, 0)
    blf.draw(font_id, HUD_TITLE)

    for key, label in rows:
        y -= line_height
        blf.size(font_id, body_size)
        if label is None:
            blf.color(font_id, *COLOR_COUNT)
            blf.position(font_id, text_left, y, 0)
            blf.draw(font_id, key)
        else:
            blf.color(font_id, *COLOR_KEY)
            blf.position(font_id, text_left, y, 0)
            blf.draw(font_id, key)

            blf.color(font_id, *COLOR_LABEL)
            blf.position(font_id, text_left + key_col_width, y, 0)
            blf.draw(font_id, label)

    _draw_order_badges(op, context)


def _draw_order_badges(op, context):
    region = context.region
    rv3d = context.region_data
    font_id = 0
    ui_scale = context.preferences.view.ui_scale
    radius = round(16 * ui_scale)
    font_size = round(16 * ui_scale)

    for index, item in enumerate(op._ordered):
        world_pos = op.get_world_position(item)
        if world_pos is None:
            continue
        coord_2d = view3d_utils.location_3d_to_region_2d(region, rv3d, world_pos)
        if coord_2d is None:
            continue

        _draw_circle(coord_2d, radius, COLOR_BADGE)

        text = str(index + 1)
        blf.size(font_id, font_size)
        text_w, text_h = blf.dimensions(font_id, text)
        blf.color(font_id, *COLOR_BADGE_TEXT)
        blf.position(font_id, coord_2d[0] - text_w / 2, coord_2d[1] - text_h / 2, 0)
        blf.draw(font_id, text)


class VIEW3D_OT_select_in_renaming_order(bpy.types.Operator):
    """Click objects or bones one by one to set the order used when numbering during rename"""
    bl_idname = "renaming.select_in_renaming_order"
    bl_label = "Select in Renaming Order"
    bl_description = "Click objects or bones one by one to set the order used when numbering during rename"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        if context.area is None or context.area.type != 'VIEW_3D':
            self.report({'WARNING'}, "Activate this from a 3D Viewport")
            return {'CANCELLED'}

        # Which mode is valid depends on what's actually being renamed, not just
        # "any supported mode" — tagging object order only makes sense in Object
        # mode, the same way bone order only makes sense in Edit/Pose mode.
        target_is_bone = context.scene.renaming_object_types == 'BONE'
        if target_is_bone:
            if context.mode not in {'EDIT_ARMATURE', 'POSE'}:
                self.report({'WARNING'}, "Bone ordering requires Edit or Pose mode")
                return {'CANCELLED'}
        else:
            if context.mode != 'OBJECT':
                self.report({'WARNING'}, "Object ordering requires Object mode")
                return {'CANCELLED'}

        self._pick_mode = context.mode
        self._ordered = []

        if self._pick_mode == 'OBJECT':
            self._item_label = "object"
            self._armature_obj = None
            for obj in bpy.data.objects:
                if SELECTION_ORDER_KEY in obj:
                    del obj[SELECTION_ORDER_KEY]
            bpy.ops.object.select_all(action='DESELECT')
        else:
            self._item_label = "bone"
            self._armature_obj = context.object
            for arm in bpy.data.armatures:
                for bone in arm.bones:
                    if SELECTION_ORDER_KEY in bone:
                        del bone[SELECTION_ORDER_KEY]
            if self._pick_mode == 'EDIT_ARMATURE':
                bpy.ops.armature.select_all(action='DESELECT')
            else:  # POSE
                bpy.ops.pose.select_all(action='DESELECT')

        self._draw_handle = bpy.types.SpaceView3D.draw_handler_add(
            _draw_viewport_hud, (self, context), 'WINDOW', 'POST_PIXEL')
        context.workspace.status_text_set(_status_text(0))
        context.window_manager.modal_handler_add(self)
        context.area.tag_redraw()
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                self._handle_click(context, event)
            return {'RUNNING_MODAL'}

        if event.type in {'RET', 'NUMPAD_ENTER'} and event.value == 'PRESS':
            count = len(self._ordered)
            self._finish(context)
            self.report({'INFO'}, f"Renaming order set for {count} {self._item_label}(s)")
            return {'FINISHED'}

        if event.type in {'ESC', 'RIGHTMOUSE'} and event.value == 'PRESS':
            count = len(self._ordered)
            self._cancel()
            self._finish(context)
            self.report({'INFO'}, f"Cancelled — cleared order on {count} {self._item_label}(s)")
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def _handle_click(self, context, event):
        if self._pick_mode == 'OBJECT':
            self._handle_object_click(context, event)
        else:
            self._handle_bone_click(context, event)

    def _handle_object_click(self, context, event):
        # scene.ray_cast() only intersects actual mesh geometry, so it never
        # hits cameras, lights, empties, armatures, etc. view3d.select() is
        # Blender's own click-selection operator (what a normal LMB click
        # runs), so it picks any object type through the same mechanism the
        # viewport already uses to render/click them.
        coord = (int(event.mouse_region_x), int(event.mouse_region_y))
        result = bpy.ops.view3d.select(location=coord, extend=True, deselect=False, toggle=False)

        if 'FINISHED' not in result:
            return

        obj = context.view_layer.objects.active
        if obj is None:
            return

        if obj in self._ordered:
            self.report({'INFO'}, f"{obj.name} is already order {obj[SELECTION_ORDER_KEY] + 1}")
            return

        self._assign_order(context, obj, obj.name)

    def _handle_bone_click(self, context, event):
        region = context.region
        rv3d = context.region_data
        mouse = Vector((event.mouse_region_x, event.mouse_region_y))
        ui_scale = context.preferences.view.ui_scale

        armature_obj = self._armature_obj
        matrix_world = armature_obj.matrix_world
        bones = armature_obj.data.edit_bones if self._pick_mode == 'EDIT_ARMATURE' else armature_obj.pose.bones

        best = None
        best_dist = BONE_PICK_RADIUS_PX * ui_scale
        for b in bones:
            head_2d = view3d_utils.location_3d_to_region_2d(region, rv3d, matrix_world @ b.head)
            tail_2d = view3d_utils.location_3d_to_region_2d(region, rv3d, matrix_world @ b.tail)
            if head_2d is None or tail_2d is None:
                continue
            dist = _dist_point_to_segment(mouse, head_2d, tail_2d)
            if dist < best_dist:
                best_dist = dist
                best = b

        if best is None:
            return

        if self._pick_mode == 'EDIT_ARMATURE':
            bone_data = armature_obj.data.bones.get(best.name)
        else:
            bone_data = best.bone

        if bone_data is None:
            self.report({'WARNING'},
                       f"{best.name} isn't in the armature's committed bone data yet "
                       "(exit and re-enter Edit Mode once, then try again)")
            return

        if bone_data in self._ordered:
            self.report({'INFO'}, f"{bone_data.name} is already order {bone_data[SELECTION_ORDER_KEY] + 1}")
            return

        if self._pick_mode == 'EDIT_ARMATURE':
            best.select = True
            best.select_head = True
            best.select_tail = True
        else:
            # Bone.select was removed in favor of PoseBone.select in Blender 5.x;
            # 4.x only exposes it on the underlying Bone.
            if hasattr(best, 'select'):
                best.select = True
            else:
                best.bone.select = True

        self._assign_order(context, bone_data, bone_data.name)

    def _assign_order(self, context, tagged_item, name):
        tagged_item[SELECTION_ORDER_KEY] = len(self._ordered)
        self._ordered.append(tagged_item)
        order_number = len(self._ordered)
        self.report({'INFO'}, f"Order {order_number}: {name}")
        context.workspace.status_text_set(_status_text(order_number))

    def get_world_position(self, item):
        if self._pick_mode == 'OBJECT':
            return item.matrix_world.translation.copy()

        armature_obj = self._armature_obj
        if self._pick_mode == 'EDIT_ARMATURE':
            bone = armature_obj.data.edit_bones.get(item.name)
        else:
            bone = armature_obj.pose.bones.get(item.name)
        if bone is None:
            return None

        return armature_obj.matrix_world @ ((bone.head + bone.tail) / 2)

    def _cancel(self):
        for item in self._ordered:
            if SELECTION_ORDER_KEY in item:
                del item[SELECTION_ORDER_KEY]
            if self._pick_mode == 'OBJECT':
                item.select_set(False)
            elif self._pick_mode == 'EDIT_ARMATURE':
                edit_bone = self._armature_obj.data.edit_bones.get(item.name)
                if edit_bone is not None:
                    edit_bone.select = False
                    edit_bone.select_head = False
                    edit_bone.select_tail = False
            else:  # POSE
                if hasattr(item, 'select'):  # Blender 4.x: Bone.select
                    item.select = False
                else:  # Blender 5.x: selection lives on PoseBone
                    pose_bone = self._armature_obj.pose.bones.get(item.name)
                    if pose_bone is not None:
                        pose_bone.select = False
        self._ordered = []

    def _finish(self, context):
        bpy.types.SpaceView3D.draw_handler_remove(self._draw_handle, 'WINDOW')
        context.workspace.status_text_set(None)
        context.area.tag_redraw()
