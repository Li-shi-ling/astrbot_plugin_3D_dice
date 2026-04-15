from __future__ import annotations

import math

from dice_sim import SUPPORTED_DICE_TYPES, create_mesh
from dice_sim.result import detect_result, quaternion_to_matrix
from dice_sim.types import BodyPose


def test_identity_result_is_in_range_for_all_dice() -> None:
    pose = BodyPose(position=(0.0, 0.0, 0.0), orientation=(0.0, 0.0, 0.0, 1.0))
    for dice_type in SUPPORTED_DICE_TYPES:
        mesh = create_mesh(dice_type)
        value = detect_result(mesh, pose)
        assert 1 <= value <= int(dice_type[1:])


def test_quaternion_matrix_rotates_x_to_y() -> None:
    angle = math.pi / 2
    quat = (0.0, 0.0, math.sin(angle / 2), math.cos(angle / 2))
    matrix = quaternion_to_matrix(quat)
    rotated = matrix @ [1.0, 0.0, 0.0]
    assert pytest_approx_tuple(rotated) == (0.0, 1.0, 0.0)


def test_d4_uses_top_vertex_rule() -> None:
    mesh = create_mesh("D4")
    pose = BodyPose(position=(0.0, 0.0, 0.0), orientation=(0.0, 0.0, 0.0, 1.0))
    matrix = quaternion_to_matrix(pose.orientation)
    rotated_vertices = mesh.vertices @ matrix.T
    top_vertex = int(
        max(range(len(mesh.vertices)), key=lambda idx: rotated_vertices[idx, 2])
    )
    expected = next(
        mesh.result_values[index]
        for index, surface in enumerate(mesh.render_faces)
        if top_vertex not in surface
    )
    value = detect_result(mesh, pose)
    assert value == expected
    assert mesh.result_rule == "top_vertex"


def pytest_approx_tuple(values):
    import pytest

    return tuple(pytest.approx(float(value), abs=1e-7) for value in values)
