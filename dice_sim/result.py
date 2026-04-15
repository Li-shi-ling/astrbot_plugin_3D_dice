from __future__ import annotations

import numpy as np

from .types import BodyPose, MeshData


def detect_result(mesh: MeshData, pose: BodyPose) -> int:
    matrix = quaternion_to_matrix(pose.orientation)
    world_normals = mesh.result_normals @ matrix.T
    if mesh.result_rule == "bottom_face":
        index = int(np.argmin(world_normals[:, 2]))
    else:
        index = int(np.argmax(world_normals[:, 2]))
    value = int(mesh.result_values[index])
    _validate_value(mesh.dice_type, value)
    return value


def quaternion_to_matrix(quat_xyzw: tuple[float, float, float, float]) -> np.ndarray:
    x, y, z, w = quat_xyzw
    norm = (x * x + y * y + z * z + w * w) ** 0.5
    if norm == 0:
        return np.eye(3)
    x, y, z, w = x / norm, y / norm, z / norm, w / norm
    return np.array(
        [
            [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
        ],
        dtype=float,
    )


def _validate_value(dice_type: str, value: int) -> None:
    sides = int(dice_type.upper().removeprefix("D"))
    if value < 1 or value > sides:
        raise ValueError(f"{dice_type} result {value} is outside 1-{sides}.")
