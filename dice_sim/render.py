from __future__ import annotations

import math
from typing import Iterable

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .errors import RenderError
from .result import quaternion_to_matrix
from .types import MeshData, SimulationFrame, StyleOptions


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
        images = [
            _render_one(mesh, frame, width, height, style, final_values, camera)
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
) -> Image.Image:
    image = Image.new("RGB", (width, height), _hex(style.background_color))
    draw = ImageDraw.Draw(image)
    _draw_ground(draw, width, height)

    projected_bodies = []
    all_cam_points = []
    for pose in frame.poses:
        rotation = quaternion_to_matrix(pose.orientation)
        points = mesh.vertices @ rotation.T + np.asarray(pose.position)
        cam_points = points @ camera.T
        all_cam_points.append(cam_points)
    if all_cam_points:
        combined = np.concatenate(all_cam_points, axis=0)
        span = max(2.8, float(np.ptp(combined[:, 0])), float(np.ptp(combined[:, 1])))
        scale = min(width, height) * 0.58 / span
        center = np.array([combined[:, 0].mean(), combined[:, 1].mean()])
    else:
        scale = min(width, height) * 0.18
        center = np.zeros(2)

    for body_index, pose in enumerate(frame.poses):
        rotation = quaternion_to_matrix(pose.orientation)
        world_points = mesh.vertices @ rotation.T + np.asarray(pose.position)
        cam_points = world_points @ camera.T
        projected = np.column_stack(
            [
                width / 2 + (cam_points[:, 0] - center[0]) * scale,
                height * 0.62 - (cam_points[:, 1] - center[1]) * scale,
                cam_points[:, 2],
            ]
        )
        projected_bodies.append((body_index, projected, world_points))
        _draw_shadow(draw, projected, width, height)

    surfaces_to_draw = []
    for body_index, projected, _world_points in projected_bodies:
        for surface_index, surface in enumerate(mesh.render_faces):
            pts = projected[list(surface)]
            depth = float(pts[:, 2].mean())
            surfaces_to_draw.append((depth, body_index, surface_index, surface, pts))
    surfaces_to_draw.sort(key=lambda item: item[0])

    base_color = np.asarray(_hex(style.die_color), dtype=float)
    ink_color = _hex(style.ink_color)
    font = _font(max(12, min(width, height) // 20))
    light = np.array([0.2, -0.45, 0.87], dtype=float)
    light /= np.linalg.norm(light)

    for _depth, _body_index, surface_index, surface, pts in surfaces_to_draw:
        if _polygon_area(pts[:, :2]) <= 1:
            continue
        normal = _surface_camera_normal(pts)
        shade = 0.58 + 0.42 * max(0.0, float(np.dot(normal, light)))
        color = tuple(int(np.clip(channel * shade, 0, 255)) for channel in base_color)
        polygon = [tuple(point) for point in pts[:, :2]]
        draw.polygon(polygon, fill=color, outline=(64, 70, 82))
        if normal[2] > 0.12 and surface_index < len(mesh.result_values):
            center = pts[:, :2].mean(axis=0)
            text = str(mesh.result_values[surface_index])
            bbox = draw.textbbox((0, 0), text, font=font)
            draw.text(
                (center[0] - (bbox[2] - bbox[0]) / 2, center[1] - (bbox[3] - bbox[1]) / 2),
                text,
                fill=ink_color,
                font=font,
            )

    label_font = _font(max(13, min(width, height) // 22))
    result_text = _result_text(mesh.dice_type, final_values)
    draw.rounded_rectangle(
        [12, 12, min(width - 12, 20 + len(result_text) * 8), 42],
        radius=6,
        fill=(255, 255, 255),
        outline=(214, 220, 230),
    )
    draw.text((22, 20), result_text, fill=_hex(style.label_color), font=label_font)
    return image


def _camera_matrix() -> np.ndarray:
    yaw = math.radians(38)
    pitch = math.radians(28)
    yaw_matrix = np.array(
        [
            [math.cos(yaw), 0, math.sin(yaw)],
            [0, 1, 0],
            [-math.sin(yaw), 0, math.cos(yaw)],
        ]
    )
    pitch_matrix = np.array(
        [
            [1, 0, 0],
            [0, math.cos(pitch), -math.sin(pitch)],
            [0, math.sin(pitch), math.cos(pitch)],
        ]
    )
    return pitch_matrix @ yaw_matrix


def _draw_ground(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    y = int(height * 0.78)
    draw.rectangle([0, y, width, height], fill=(231, 235, 242))
    draw.line([0, y, width, y], fill=(203, 211, 224), width=2)


def _draw_shadow(
    draw: ImageDraw.ImageDraw, projected: np.ndarray, width: int, height: int
) -> None:
    min_x, min_y = projected[:, 0].min(), projected[:, 1].min()
    max_x, max_y = projected[:, 0].max(), projected[:, 1].max()
    cx = (min_x + max_x) / 2
    cy = min(height * 0.79, max_y + 14)
    rx = max(14, (max_x - min_x) * 0.45)
    ry = max(5, (max_y - min_y) * 0.11)
    draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(183, 190, 202))


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
        return (216, 58, 52)
    try:
        return tuple(int(text[idx : idx + 2], 16) for idx in (0, 2, 4))
    except ValueError:
        return (216, 58, 52)


def _font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("arial.ttf", size=size)
    except Exception:
        return ImageFont.load_default()
