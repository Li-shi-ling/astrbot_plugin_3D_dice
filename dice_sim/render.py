from __future__ import annotations

import math
from functools import lru_cache
from typing import Iterable

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont

from .errors import RenderError
from .result import quaternion_to_matrix
from .types import MeshData, SimulationFrame, StyleOptions

GROUND_Z = 0.0
TABLE_MARGIN = 2.0
D6_FRONT_FACE_EPSILON = 1e-3
SCENE_ZOOM = 0.82
RESULT_LABEL_SECONDS = 5.0


def render_frames(
    mesh: MeshData,
    frames: Iterable[SimulationFrame],
    width: int,
    height: int,
    style: StyleOptions,
    final_values: tuple[int, ...],
    result_label_start_time: float | None = None,
) -> list[Image.Image]:
    try:
        frame_list = list(frames)
        if not frame_list:
            raise RenderError("No simulation frames were captured.")
        camera = _camera_matrix()
        scale, center, table_corners = _scene_view(mesh, frame_list, width, height, camera)
        label_start_time = (
            frame_list[-1].time_seconds - RESULT_LABEL_SECONDS
            if result_label_start_time is None
            else result_label_start_time
        )
        images = [
            _render_one(
                mesh,
                frame,
                width,
                height,
                style,
                final_values,
                camera,
                scale,
                center,
                table_corners,
                show_result_label=frame.time_seconds >= label_start_time,
            )
            for frame in frame_list
        ]
        if len(images) < 2:
            images.append(images[0].copy())
        return images
    except RenderError:
        raise
    except Exception as exc:
        raise RenderError(f"Software rendering failed: {exc}") from exc


def _render_one(
    mesh: MeshData,
    frame: SimulationFrame,
    width: int,
    height: int,
    style: StyleOptions,
    final_values: tuple[int, ...],
    camera: np.ndarray,
    scale: float,
    center: np.ndarray,
    table_corners: np.ndarray,
    show_result_label: bool,
) -> Image.Image:
    image = Image.new("RGB", (width, height), _hex(style.background_color))
    draw = ImageDraw.Draw(image)
    _draw_ground(draw, table_corners, camera, width, height, scale, center)

    projected_bodies = []
    for body_index, pose in enumerate(frame.poses):
        rotation = quaternion_to_matrix(pose.orientation)
        world_points = mesh.vertices @ rotation.T + np.asarray(pose.position)
        camera_points = world_points @ camera.T
        top_vertex = (
            int(np.argmax(world_points[:, 2])) if mesh.dice_type == "D4" else -1
        )
        projected = _project_world(world_points, camera, width, height, scale, center)
        projected_bodies.append(
            (body_index, projected, camera_points, world_points, top_vertex)
        )
        _draw_shadow(draw, world_points, camera, width, height, scale, center)

    surfaces_to_draw = []
    for (
        body_index,
        projected,
        camera_points,
        _world_points,
        top_vertex,
    ) in projected_bodies:
        for surface_index, surface in enumerate(mesh.render_faces):
            pts = projected[list(surface)]
            face_camera_points = camera_points[list(surface)]
            depth = float(pts[:, 2].mean())
            surfaces_to_draw.append(
                (
                    depth,
                    body_index,
                    surface_index,
                    surface,
                    pts,
                    face_camera_points,
                    top_vertex,
                )
            )
    surfaces_to_draw.sort(key=lambda item: item[0])

    base_color = np.asarray(_hex(style.die_color), dtype=float)
    ink_color = _hex(style.ink_color)
    edge_color = _hex(style.edge_color)
    light = np.array([0.2, -0.45, 0.87], dtype=float)
    light /= np.linalg.norm(light)
    d4_vertex_values = _d4_vertex_values(mesh) if mesh.dice_type == "D4" else {}
    number_decals: list[tuple[np.ndarray, str]] = []
    d4_face_decals: list[tuple[np.ndarray, tuple[int, ...], int]] = []

    for (
        _depth,
        _body_index,
        surface_index,
        surface,
        pts,
        face_camera_points,
        top_vertex,
    ) in surfaces_to_draw:
        polygon_points = pts[:, :2]
        if _polygon_area(polygon_points) <= 1:
            continue
        normal = _surface_camera_normal(pts)
        d6_front_facing = _d6_face_is_visible(face_camera_points)
        if mesh.dice_type == "D6" and not d6_front_facing:
            continue
        shade = 0.72 + 0.28 * max(0.0, float(np.dot(normal, light)))
        color = tuple(int(np.clip(channel * shade, 0, 255)) for channel in base_color)
        polygon = [tuple(point) for point in polygon_points]
        if mesh.dice_type == "D4":
            draw.polygon(polygon, fill=color)
            draw.line(polygon + [polygon[0]], fill=edge_color, width=2)
            show_d4_labels = normal[2] > 0.08 or top_vertex in surface
            if show_d4_labels and surface_index < len(mesh.result_values):
                d4_face_decals.append(
                    (polygon_points.copy(), tuple(surface), top_vertex)
                )
        elif mesh.dice_type == "D6":
            draw.polygon(polygon, fill=color)
            if surface_index < len(mesh.result_values):
                _draw_d6_face_pips(
                    draw,
                    polygon_points.copy(),
                    mesh,
                    surface,
                    int(mesh.result_values[surface_index]),
                    ink_color,
                )
            draw.line(polygon + [polygon[0]], fill=edge_color, width=2)
        else:
            draw.polygon(polygon, fill=color)
            draw.line(polygon + [polygon[0]], fill=edge_color, width=2)
            if normal[2] > 0.08 and surface_index < len(mesh.result_values):
                number_decals.append(
                    (polygon_points.copy(), str(mesh.result_values[surface_index]))
                )

    for polygon_points, text in number_decals:
        _draw_face_number(image, polygon_points, text, ink_color)
    for polygon_points, surface, top_vertex in d4_face_decals:
        _draw_d4_face_numbers(
            image,
            polygon_points,
            surface,
            top_vertex,
            d4_vertex_values,
            ink_color,
        )

    if show_result_label:
        label_font = _font(max(13, min(width, height) // 22))
        result_text = _result_text(mesh.dice_type, final_values)
        bbox = draw.textbbox((0, 0), result_text, font=label_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        label_left = 12
        label_top = 12
        padding_x = 12
        padding_y = 7
        draw.rounded_rectangle(
            [
                label_left,
                label_top,
                min(width - 12, label_left + text_width + padding_x * 2),
                label_top + text_height + padding_y * 2,
            ],
            radius=6,
            fill=(255, 255, 255),
            outline=(0, 0, 0),
        )
        draw.text(
            (label_left + padding_x - bbox[0], label_top + padding_y - bbox[1]),
            result_text,
            fill=_hex(style.label_color),
            font=label_font,
        )
    return image


def _scene_view(
    mesh: MeshData,
    frames: list[SimulationFrame],
    width: int,
    height: int,
    camera: np.ndarray,
) -> tuple[float, np.ndarray, np.ndarray]:
    all_points = []
    world_points_for_bounds = []
    for frame in frames:
        for pose in frame.poses:
            rotation = quaternion_to_matrix(pose.orientation)
            world_points = mesh.vertices @ rotation.T + np.asarray(pose.position)
            world_points_for_bounds.append(world_points)
            all_points.append(world_points @ camera.T)
    if not all_points:
        table_corners = _table_corners(np.array([[-2, -2, 0], [2, 2, 0]], dtype=float))
        return min(width, height) * 0.18, np.zeros(2), table_corners
    table_corners = _table_corners(np.concatenate(world_points_for_bounds, axis=0))
    all_points.append(table_corners @ camera.T)
    combined = np.concatenate(all_points, axis=0)
    x_span = float(np.ptp(combined[:, 0]))
    y_span = float(np.ptp(combined[:, 1]))
    span = max(3.0, x_span, y_span * 1.15)
    scale = min(width, height) * SCENE_ZOOM / span
    center = np.array(
        [
            (combined[:, 0].min() + combined[:, 0].max()) / 2,
            (combined[:, 1].min() + combined[:, 1].max()) / 2,
        ],
        dtype=float,
    )
    return scale, center, table_corners


def _camera_matrix() -> np.ndarray:
    yaw = math.radians(28)
    tilt = math.radians(54)
    right = np.array([math.cos(yaw), math.sin(yaw), 0.0], dtype=float)
    ground_forward = np.array([-math.sin(yaw), math.cos(yaw), 0.0], dtype=float)
    screen_up = np.array(
        [
            -ground_forward[0] * math.sin(tilt),
            -ground_forward[1] * math.sin(tilt),
            math.cos(tilt),
        ],
        dtype=float,
    )
    depth = np.array(
        [
            ground_forward[0] * math.cos(tilt),
            ground_forward[1] * math.cos(tilt),
            math.sin(tilt),
        ],
        dtype=float,
    )
    return np.vstack([right, screen_up, depth])


def _draw_ground(
    draw: ImageDraw.ImageDraw,
    table_corners: np.ndarray,
    camera: np.ndarray,
    width: int,
    height: int,
    scale: float,
    center: np.ndarray,
) -> None:
    projected = _project_world(table_corners, camera, width, height, scale, center)
    polygon = [tuple(point) for point in projected[:, :2]]
    draw.polygon(polygon, fill=(232, 235, 240), outline=(0, 0, 0))
    for start, end in ((0, 1), (1, 2), (2, 3), (3, 0)):
        draw.line(
            [tuple(projected[start, :2]), tuple(projected[end, :2])],
            fill=(0, 0, 0),
            width=1,
        )


def _draw_shadow(
    draw: ImageDraw.ImageDraw,
    world_points: np.ndarray,
    camera: np.ndarray,
    width: int,
    height: int,
    scale: float,
    center: np.ndarray,
) -> None:
    ground_points = world_points.copy()
    ground_points[:, 2] = GROUND_Z
    projected = _project_world(ground_points, camera, width, height, scale, center)
    min_x, min_y = projected[:, 0].min(), projected[:, 1].min()
    max_x, max_y = projected[:, 0].max(), projected[:, 1].max()
    cx = (min_x + max_x) / 2
    cy = (min_y + max_y) / 2
    rx = max(14, (max_x - min_x) * 0.45)
    ry = max(5, (max_y - min_y) * 0.11)
    draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(183, 190, 202))


def _d4_vertex_values(mesh: MeshData) -> dict[int, int]:
    values: dict[int, int] = {}
    for vertex_index in range(len(mesh.vertices)):
        for face_index, surface in enumerate(mesh.render_faces):
            if vertex_index not in surface and face_index < len(mesh.result_values):
                values[vertex_index] = int(mesh.result_values[face_index])
                break
    return values


def _draw_face_number(
    image: Image.Image,
    points: np.ndarray,
    text: str,
    ink_color: tuple[int, int, int],
) -> None:
    area = _polygon_area(points)
    if area < 18:
        return
    texture_size = 384
    source_polygon = _texture_polygon(len(points), texture_size)
    texture = _face_number_texture(text, len(points), ink_color, texture_size)
    _draw_textured_polygon(image, points, source_polygon, texture)


def _draw_d6_face_pips(
    draw: ImageDraw.ImageDraw,
    points: np.ndarray,
    mesh: MeshData,
    surface: tuple[int, ...],
    value: int,
    ink_color: tuple[int, int, int],
) -> None:
    area = _polygon_area(points)
    if area < 18 or len(surface) != 4:
        return
    corners = _d6_face_uv_corners(mesh, surface, points)
    if corners is None:
        return
    p00, p10, p01 = corners
    u_axis = p10 - p00
    v_axis = p01 - p00
    radius = max(1.5, min(np.linalg.norm(u_axis), np.linalg.norm(v_axis)) * 0.065)
    for u, v in _d6_pip_uvs(value):
        center = p00 + u_axis * u + v_axis * v
        draw.ellipse(
            [
                float(center[0] - radius),
                float(center[1] - radius),
                float(center[0] + radius),
                float(center[1] + radius),
            ],
            fill=ink_color,
        )


def _d6_face_uv_corners(
    mesh: MeshData, surface: tuple[int, ...], points: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray] | None:
    local_points = mesh.vertices[list(surface)]
    ranges = np.ptp(local_points, axis=0)
    varying_axes = [axis for axis, span in enumerate(ranges) if span > 1e-6]
    if len(varying_axes) != 2:
        return None

    u_axis, v_axis = varying_axes
    u_values = local_points[:, u_axis]
    v_values = local_points[:, v_axis]
    u_min, u_max = float(u_values.min()), float(u_values.max())
    v_min, v_max = float(v_values.min()), float(v_values.max())
    if abs(u_max - u_min) < 1e-6 or abs(v_max - v_min) < 1e-6:
        return None

    corners: dict[tuple[int, int], np.ndarray] = {}
    for screen_point, u_value, v_value in zip(points, u_values, v_values):
        u = int(round((float(u_value) - u_min) / (u_max - u_min)))
        v = int(round((v_max - float(v_value)) / (v_max - v_min)))
        corners[(u, v)] = np.asarray(screen_point, dtype=float)
    try:
        return corners[(0, 0)], corners[(1, 0)], corners[(0, 1)]
    except KeyError:
        return None


def _draw_d4_face_numbers(
    image: Image.Image,
    points: np.ndarray,
    surface: tuple[int, ...],
    top_vertex: int,
    vertex_values: dict[int, int],
    ink_color: tuple[int, int, int],
) -> None:
    area = _polygon_area(points)
    if area < 18:
        return
    texture_size = 384
    source_polygon = _texture_polygon(len(points), texture_size)
    face_center = source_polygon.mean(axis=0)
    labels = []
    for vertex_index, source_point in zip(surface, source_polygon):
        value = vertex_values.get(vertex_index)
        if value is None:
            continue
        vertex_weight = 0.48 if vertex_index == top_vertex else 0.72
        label_position = (
            face_center * (1.0 - vertex_weight) + source_point * vertex_weight
        )
        labels.append((str(value), tuple(float(coord) for coord in label_position)))
    if not labels:
        return
    texture = _labeled_face_texture(
        tuple(labels),
        ink_color,
        texture_size,
        int(texture_size * 0.24),
    )
    _draw_textured_polygon(image, points, source_polygon, texture)


def _draw_textured_polygon(
    image: Image.Image,
    destination_polygon: np.ndarray,
    source_polygon: np.ndarray,
    texture: Image.Image,
) -> None:
    min_x = max(0, int(math.floor(float(destination_polygon[:, 0].min()) - 2)))
    min_y = max(0, int(math.floor(float(destination_polygon[:, 1].min()) - 2)))
    max_x = min(image.width, int(math.ceil(float(destination_polygon[:, 0].max()) + 2)))
    max_y = min(
        image.height, int(math.ceil(float(destination_polygon[:, 1].max()) + 2))
    )
    if max_x <= min_x or max_y <= min_y:
        return

    output_size = (max_x - min_x, max_y - min_y)
    destination = destination_polygon - np.array([min_x, min_y], dtype=float)
    triangles = _polygon_triangles(len(destination))
    for triangle in triangles:
        src_triangle = source_polygon[list(triangle)]
        dst_triangle = destination[list(triangle)]
        coeffs = _affine_coefficients(src_triangle, dst_triangle)
        try:
            transform_affine = Image.Transform.AFFINE
        except AttributeError:
            transform_affine = Image.AFFINE
        warped = texture.transform(
            output_size,
            transform_affine,
            coeffs,
            resample=_bicubic_resample(),
        )
        mask = Image.new("L", output_size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.polygon([tuple(point) for point in dst_triangle], fill=255)
        alpha = ImageChops.multiply(warped.getchannel("A"), mask)
        warped.putalpha(alpha)
        image.paste(warped, (min_x, min_y), warped)


def _texture_polygon(point_count: int, texture_size: int) -> np.ndarray:
    margin = texture_size * 0.14
    if point_count == 3:
        return np.array(
            [
                [texture_size * 0.50, margin],
                [texture_size - margin, texture_size - margin],
                [margin, texture_size - margin],
            ],
            dtype=float,
        )
    return np.array(
        [
            [margin, margin],
            [texture_size - margin, margin],
            [texture_size - margin, texture_size - margin],
            [margin, texture_size - margin],
        ],
        dtype=float,
    )


def _polygon_triangles(point_count: int) -> tuple[tuple[int, int, int], ...]:
    return tuple((0, idx, idx + 1) for idx in range(1, point_count - 1))


def _affine_coefficients(
    source_triangle: np.ndarray, destination_triangle: np.ndarray
) -> tuple[float, float, float, float, float, float]:
    rows = []
    values = []
    for source, destination in zip(source_triangle, destination_triangle):
        x, y = float(destination[0]), float(destination[1])
        rows.append([x, y, 1.0, 0.0, 0.0, 0.0])
        rows.append([0.0, 0.0, 0.0, x, y, 1.0])
        values.extend([float(source[0]), float(source[1])])
    coeffs = np.linalg.solve(
        np.asarray(rows, dtype=float), np.asarray(values, dtype=float)
    )
    return tuple(float(value) for value in coeffs)


@lru_cache(maxsize=256)
def _face_number_texture(
    text: str,
    point_count: int,
    ink_color: tuple[int, int, int],
    texture_size: int,
) -> Image.Image:
    if point_count == 3:
        center = (texture_size / 2, texture_size * 0.60)
        font_size = int(texture_size * (0.34 if len(text) == 1 else 0.27))
    else:
        center = (texture_size / 2, texture_size / 2)
        font_size = int(texture_size * (0.46 if len(text) == 1 else 0.34))
    return _labeled_face_texture(((text, center),), ink_color, texture_size, font_size)


def _d6_pip_uvs(value: int) -> tuple[tuple[float, float], ...]:
    left = 0.34
    center = 0.50
    right = 0.66
    top = 0.32
    middle = 0.50
    bottom = 0.68
    layouts = {
        1: ((center, middle),),
        2: ((left, top), (right, bottom)),
        3: ((left, top), (center, middle), (right, bottom)),
        4: ((left, top), (right, top), (left, bottom), (right, bottom)),
        5: (
            (left, top),
            (right, top),
            (center, middle),
            (left, bottom),
            (right, bottom),
        ),
        6: (
            (left, top),
            (right, top),
            (left, middle),
            (right, middle),
            (left, bottom),
            (right, bottom),
        ),
    }
    return layouts.get(int(value), ())


@lru_cache(maxsize=512)
def _labeled_face_texture(
    labels: tuple[tuple[str, tuple[float, float]], ...],
    ink_color: tuple[int, int, int],
    texture_size: int,
    font_size: int | None = None,
) -> Image.Image:
    image = Image.new("RGBA", (texture_size, texture_size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    size = font_size or int(texture_size * 0.16)
    font = _texture_font(size)
    for text, center in labels:
        _draw_centered_texture_text(draw, text, center, font, size, ink_color)
    return image


def _draw_centered_texture_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    center: tuple[float, float],
    font: ImageFont.ImageFont,
    size: int,
    ink_color: tuple[int, int, int],
) -> None:
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    if text_width <= 0 or text_height <= 0:
        return
    draw.text(
        (
            center[0] - text_width / 2 - bbox[0],
            center[1] - text_height / 2 - bbox[1],
        ),
        text,
        font=font,
        fill=(*ink_color, 255),
        stroke_width=max(1, size // 18),
        stroke_fill=(255, 255, 255, 255),
    )


def _bicubic_resample() -> int:
    try:
        return Image.Resampling.BICUBIC
    except AttributeError:
        return Image.BICUBIC


def _project_world(
    world_points: np.ndarray,
    camera: np.ndarray,
    width: int,
    height: int,
    scale: float,
    center: np.ndarray,
) -> np.ndarray:
    cam_points = world_points @ camera.T
    return np.column_stack(
        [
            width / 2 + (cam_points[:, 0] - center[0]) * scale,
            height * 0.62 - (cam_points[:, 1] - center[1]) * scale,
            cam_points[:, 2],
        ]
    )


def _table_corners(world_points: np.ndarray) -> np.ndarray:
    min_x = float(world_points[:, 0].min()) - TABLE_MARGIN
    max_x = float(world_points[:, 0].max()) + TABLE_MARGIN
    min_y = float(world_points[:, 1].min()) - TABLE_MARGIN
    max_y = float(world_points[:, 1].max()) + TABLE_MARGIN
    return np.array(
        [
            [min_x, min_y, GROUND_Z],
            [max_x, min_y, GROUND_Z],
            [max_x, max_y, GROUND_Z],
            [min_x, max_y, GROUND_Z],
        ],
        dtype=float,
    )


def _surface_camera_normal(points: np.ndarray) -> np.ndarray:
    normal = np.cross(points[1] - points[0], points[2] - points[0])
    norm = np.linalg.norm(normal)
    if norm == 0:
        return np.array([0.0, 0.0, 1.0])
    return normal / norm


def _d6_face_is_visible(camera_points: np.ndarray) -> bool:
    normal = _surface_camera_normal(camera_points)
    return normal[2] < -D6_FRONT_FACE_EPSILON


def _polygon_area(points: np.ndarray) -> float:
    x = points[:, 0]
    y = points[:, 1]
    return abs(float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))) / 2)


def _result_text(dice_type: str, values: tuple[int, ...]) -> str:
    detail = "+".join(str(value) for value in values)
    return f"{dice_type} = {detail}  total {sum(values)}"


def _hex(value: str) -> tuple[int, int, int]:
    text = str(value or "").strip().lstrip("#")
    if len(text) != 6:
        return (255, 255, 255)
    try:
        return tuple(int(text[idx : idx + 2], 16) for idx in (0, 2, 4))
    except ValueError:
        return (255, 255, 255)


def _font(size: int) -> ImageFont.ImageFont:
    for font_name in ("arialbd.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(font_name, size=size)
        except Exception:
            pass
    return ImageFont.load_default()


def _texture_font(size: int) -> ImageFont.ImageFont:
    for font_name in ("arial.ttf", "segoeui.ttf", "arialbd.ttf"):
        try:
            return ImageFont.truetype(font_name, size=size)
        except Exception:
            pass
    return ImageFont.load_default()
