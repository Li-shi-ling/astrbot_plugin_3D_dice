from __future__ import annotations

import math
from typing import Iterable

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .errors import RenderError
from .result import quaternion_to_matrix
from .types import MeshData, SimulationFrame, StyleOptions

GROUND_Z = 0.0
TABLE_MARGIN = 1.25


def render_frames(
    mesh: MeshData,
    frames: Iterable[SimulationFrame],
    width: int,
    height: int,
    style: StyleOptions,
    final_values: tuple[int, ...],
) -> list[Image.Image]:
    try:
        frame_list = list(frames)
        if not frame_list:
            raise RenderError("No simulation frames were captured.")
        camera = _camera_matrix()
        scale, center, table_corners = _scene_view(mesh, frame_list, width, height, camera)
        result_label_start = max(0, len(frame_list) - 3)
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
                show_result_label=index >= result_label_start,
            )
            for index, frame in enumerate(frame_list)
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
        top_vertex = (
            int(np.argmax(world_points[:, 2])) if mesh.dice_type == "D4" else -1
        )
        projected = _project_world(world_points, camera, width, height, scale, center)
        projected_bodies.append((body_index, projected, world_points, top_vertex))
        _draw_shadow(draw, world_points, camera, width, height, scale, center)

    surfaces_to_draw = []
    for body_index, projected, _world_points, top_vertex in projected_bodies:
        for surface_index, surface in enumerate(mesh.render_faces):
            pts = projected[list(surface)]
            depth = float(pts[:, 2].mean())
            surfaces_to_draw.append(
                (
                    depth,
                    body_index,
                    surface_index,
                    surface,
                    pts,
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
    d4_tip_decals: list[tuple[np.ndarray, str, float]] = []

    for (
        _depth,
        _body_index,
        surface_index,
        surface,
        pts,
        top_vertex,
    ) in surfaces_to_draw:
        polygon_points = pts[:, :2]
        if _polygon_area(polygon_points) <= 1:
            continue
        normal = _surface_camera_normal(pts)
        shade = 0.72 + 0.28 * max(0.0, float(np.dot(normal, light)))
        color = tuple(int(np.clip(channel * shade, 0, 255)) for channel in base_color)
        polygon = [tuple(point) for point in polygon_points]
        draw.polygon(polygon, fill=color)
        draw.line(polygon + [polygon[0]], fill=edge_color, width=2)
        if mesh.dice_type == "D4":
            show_d4_labels = normal[2] > 0.08 or top_vertex in surface
            if show_d4_labels and surface_index < len(mesh.result_values):
                face_center = polygon_points.mean(axis=0)
                area = _polygon_area(polygon_points)
                for vertex_index, point in zip(surface, polygon_points):
                    value = d4_vertex_values.get(vertex_index)
                    if value is None:
                        continue
                    vertex_weight = 0.42 if vertex_index == top_vertex else 0.72
                    label_position = (
                        face_center * (1.0 - vertex_weight) + point * vertex_weight
                    )
                    d4_tip_decals.append((label_position, str(value), area))
        elif normal[2] > 0.08 and surface_index < len(mesh.result_values):
            number_decals.append(
                (polygon_points.copy(), str(mesh.result_values[surface_index]))
            )

    for polygon_points, text in number_decals:
        _draw_face_number(image, polygon_points, text, ink_color)
    for center, text, area in d4_tip_decals:
        _draw_tip_number(image, center, text, ink_color, area)

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
    scale = min(width, height) * 0.70 / span
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
    if area < 24:
        return
    edge_vectors = [
        points[(idx + 1) % len(points)] - points[idx] for idx in range(len(points))
    ]
    edge = max(edge_vectors, key=lambda vector: float(np.linalg.norm(vector)))
    edge_length = float(np.linalg.norm(edge))
    if edge_length < 8:
        return

    angle = math.degrees(math.atan2(float(edge[1]), float(edge[0])))
    while angle <= -90:
        angle += 180
    while angle > 90:
        angle -= 180
    if area < 180:
        angle = 0

    text_scale = 0.72 if len(text) == 1 else 0.58
    edge_scale = 0.70 if len(text) == 1 else 0.58
    minimum_size = 14 if len(text) == 1 else 12
    size = int(
        max(
            minimum_size,
            min(36, math.sqrt(area) * text_scale, edge_length * edge_scale),
        )
    )
    _paste_number_text(image, points.mean(axis=0), text, ink_color, size, angle)


def _draw_tip_number(
    image: Image.Image,
    center: np.ndarray,
    text: str,
    ink_color: tuple[int, int, int],
    face_area: float,
) -> None:
    if face_area < 24:
        return
    size = int(max(12, min(28, math.sqrt(face_area) * 0.40)))
    _paste_number_text(image, center, text, ink_color, size, 0.0)


def _paste_number_text(
    image: Image.Image,
    center: np.ndarray,
    text: str,
    ink_color: tuple[int, int, int],
    size: int,
    angle: float,
) -> None:
    font = _font(size)
    probe = Image.new("L", (1, 1))
    probe_draw = ImageDraw.Draw(probe)
    bbox = probe_draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    if text_width <= 0 or text_height <= 0:
        return

    padding = max(3, size // 4)
    tile = Image.new(
        "RGBA",
        (text_width + padding * 2, text_height + padding * 2),
        (255, 255, 255, 0),
    )
    tile_draw = ImageDraw.Draw(tile)
    tile_draw.text(
        (padding - bbox[0], padding - bbox[1]),
        text,
        font=font,
        fill=(*ink_color, 255),
        stroke_width=max(1, size // 9),
        stroke_fill=(255, 255, 255, 255),
    )
    try:
        resample = Image.Resampling.BICUBIC
    except AttributeError:
        resample = Image.BICUBIC
    rotated = tile.rotate(angle, resample=resample, expand=True)
    paste_at = (
        int(round(float(center[0]) - rotated.width / 2)),
        int(round(float(center[1]) - rotated.height / 2)),
    )
    image.paste(rotated, paste_at, rotated)


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
