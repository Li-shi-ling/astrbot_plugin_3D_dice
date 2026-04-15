from __future__ import annotations

import numpy as np

from dice_sim import SUPPORTED_DICE_TYPES, create_mesh


def test_all_supported_meshes_construct() -> None:
    for dice_type in SUPPORTED_DICE_TYPES:
        mesh = create_mesh(dice_type)
        assert mesh.vertices.shape[1] == 3
        assert mesh.faces.shape[1] == 3
        assert len(mesh.vertices) > 0
        assert len(mesh.faces) > 0
        assert len(mesh.result_normals) == len(mesh.result_values)
        assert len(mesh.result_centers) == len(mesh.result_values)
        assert set(mesh.result_values) == set(range(1, int(dice_type[1:]) + 1))
        assert np.allclose(np.linalg.norm(mesh.result_normals, axis=1), 1.0)


def test_d10_uses_ten_result_faces() -> None:
    mesh = create_mesh("d10")
    assert mesh.dice_type == "D10"
    assert len(mesh.result_values) == 10
    assert len(mesh.render_faces) == 10
    assert len(mesh.faces) == 20
