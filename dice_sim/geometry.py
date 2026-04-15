from __future__ import annotations

import math
from typing import Iterable

import numpy as np

from .errors import UnsupportedDiceError
from .types import MeshData

SUPPORTED_DICE_TYPES = ("D4", "D6", "D8", "D10", "D20")


def create_mesh(dice_type: str) -> MeshData:
    normalized = str(dice_type or "").strip().upper()
    factories = {
        "D4": _tetrahedron,
        "D6": _cube,
        "D8": _octahedron,
        "D10": _d10_trapezohedron,
        "D20": _icosahedron,
    }
    try:
        return factories[normalized]()
    except KeyError as exc:
        supported = ", ".join(SUPPORTED_DICE_TYPES)
        raise UnsupportedDiceError(
            f"Unsupported dice type {dice_type!r}. Supported: {supported}."
        ) from exc


def _tetrahedron() -> MeshData:
    vertices = np.array(
        [
            [1.0, 1.0, 1.0],
            [-1.0, -1.0, 1.0],
            [-1.0, 1.0, -1.0],
            [1.0, -1.0, -1.0],
        ],
        dtype=float,
    ) / math.sqrt(3.0)
    faces = _oriented_faces(vertices, [(0, 1, 2), (0, 3, 1), (0, 2, 3), (1, 3, 2)])
    normals, centers = _face_normals_and_centers(vertices, faces)
    return MeshData(
        dice_type="D4",
        vertices=vertices,
        faces=faces,
        result_normals=normals,
        result_values=(1, 2, 3, 4),
        result_rule="top_vertex",
        result_centers=centers,
        render_faces=tuple(tuple(face) for face in faces.tolist()),
    )


def _cube() -> MeshData:
    vertices = np.array(
        [
            [-1, -1, -1],
            [1, -1, -1],
            [1, 1, -1],
            [-1, 1, -1],
            [-1, -1, 1],
            [1, -1, 1],
            [1, 1, 1],
            [-1, 1, 1],
        ],
        dtype=float,
    )
    quads = (
        (0, 3, 2, 1),
        (4, 5, 6, 7),
        (0, 1, 5, 4),
        (1, 2, 6, 5),
        (2, 3, 7, 6),
        (3, 0, 4, 7),
    )
    faces = _triangulate_surfaces(quads)
    normals, centers = _surface_normals_and_centers(vertices, quads)
    return MeshData(
        dice_type="D6",
        vertices=vertices,
        faces=faces,
        result_normals=normals,
        result_values=(1, 6, 2, 3, 4, 5),
        result_rule="top_face",
        result_centers=centers,
        render_faces=quads,
    )


def _octahedron() -> MeshData:
    vertices = np.array(
        [
            [1, 0, 0],
            [-1, 0, 0],
            [0, 1, 0],
            [0, -1, 0],
            [0, 0, 1],
            [0, 0, -1],
        ],
        dtype=float,
    )
    faces = _oriented_faces(
        vertices,
        [
            (4, 0, 2),
            (4, 2, 1),
            (4, 1, 3),
            (4, 3, 0),
            (5, 2, 0),
            (5, 1, 2),
            (5, 3, 1),
            (5, 0, 3),
        ],
    )
    normals, centers = _face_normals_and_centers(vertices, faces)
    return MeshData(
        dice_type="D8",
        vertices=vertices,
        faces=faces,
        result_normals=normals,
        result_values=tuple(range(1, 9)),
        result_rule="top_face",
        result_centers=centers,
        render_faces=tuple(tuple(face) for face in faces.tolist()),
    )


def _d10_trapezohedron() -> MeshData:
    radius = 1.0
    pole_height = 1.18
    vertices: list[list[float]] = [[0, 0, pole_height], [0, 0, -pole_height]]
    ring: list[int] = []
    for idx in range(5):
        a = 2 * math.pi * idx / 5
        ring.append(len(vertices))
        vertices.append([radius * math.cos(a), radius * math.sin(a), 0.0])

    surfaces: list[tuple[int, int, int]] = []
    for idx in range(5):
        nxt = (idx + 1) % 5
        surfaces.append((0, ring[idx], ring[nxt]))
        surfaces.append((1, ring[nxt], ring[idx]))

    vertices_array = np.asarray(vertices, dtype=float)
    faces = _oriented_faces(vertices_array, surfaces)
    normals, centers = _face_normals_and_centers(vertices_array, faces)
    return MeshData(
        dice_type="D10",
        vertices=vertices_array,
        faces=faces,
        result_normals=normals,
        result_values=tuple(range(1, 11)),
        result_rule="top_face",
        result_centers=centers,
        render_faces=tuple(tuple(face) for face in faces.tolist()),
    )


def _icosahedron() -> MeshData:
    phi = (1 + math.sqrt(5)) / 2
    vertices = np.array(
        [
            [-1, phi, 0],
            [1, phi, 0],
            [-1, -phi, 0],
            [1, -phi, 0],
            [0, -1, phi],
            [0, 1, phi],
            [0, -1, -phi],
            [0, 1, -phi],
            [phi, 0, -1],
            [phi, 0, 1],
            [-phi, 0, -1],
            [-phi, 0, 1],
        ],
        dtype=float,
    )
    vertices /= np.linalg.norm(vertices[0])
    faces = _oriented_faces(
        vertices,
        [
            (0, 11, 5),
            (0, 5, 1),
            (0, 1, 7),
            (0, 7, 10),
            (0, 10, 11),
            (1, 5, 9),
            (5, 11, 4),
            (11, 10, 2),
            (10, 7, 6),
            (7, 1, 8),
            (3, 9, 4),
            (3, 4, 2),
            (3, 2, 6),
            (3, 6, 8),
            (3, 8, 9),
            (4, 9, 5),
            (2, 4, 11),
            (6, 2, 10),
            (8, 6, 7),
            (9, 8, 1),
        ],
    )
    normals, centers = _face_normals_and_centers(vertices, faces)
    return MeshData(
        dice_type="D20",
        vertices=vertices,
        faces=faces,
        result_normals=normals,
        result_values=tuple(range(1, 21)),
        result_rule="top_face",
        result_centers=centers,
        render_faces=tuple(tuple(face) for face in faces.tolist()),
    )


def _triangulate_surfaces(surfaces: Iterable[tuple[int, ...]]) -> np.ndarray:
    triangles: list[tuple[int, int, int]] = []
    for surface in surfaces:
        if len(surface) == 3:
            triangles.append(surface)
        else:
            for idx in range(1, len(surface) - 1):
                triangles.append((surface[0], surface[idx], surface[idx + 1]))
    return np.asarray(triangles, dtype=np.int32)


def _oriented_faces(vertices: np.ndarray, faces: Iterable[tuple[int, int, int]]) -> np.ndarray:
    centroid = vertices.mean(axis=0)
    oriented: list[tuple[int, int, int]] = []
    for face in faces:
        pts = vertices[list(face)]
        normal = np.cross(pts[1] - pts[0], pts[2] - pts[0])
        center = pts.mean(axis=0)
        if np.dot(normal, center - centroid) < 0:
            oriented.append((face[0], face[2], face[1]))
        else:
            oriented.append(face)
    return np.asarray(oriented, dtype=np.int32)


def _orient_surfaces(
    vertices: np.ndarray, surfaces: Iterable[tuple[int, ...]]
) -> tuple[tuple[int, ...], ...]:
    centroid = vertices.mean(axis=0)
    oriented: list[tuple[int, ...]] = []
    for surface in surfaces:
        normal = _newell_normal(vertices[list(surface)])
        center = vertices[list(surface)].mean(axis=0)
        if np.dot(normal, center - centroid) < 0:
            oriented.append(tuple(reversed(surface)))
        else:
            oriented.append(surface)
    return tuple(oriented)


def _face_normals_and_centers(
    vertices: np.ndarray, faces: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    normals = []
    centers = []
    for face in faces:
        pts = vertices[face]
        normal = np.cross(pts[1] - pts[0], pts[2] - pts[0])
        normal = normal / np.linalg.norm(normal)
        normals.append(normal)
        centers.append(pts.mean(axis=0))
    return np.asarray(normals, dtype=float), np.asarray(centers, dtype=float)


def _surface_normals_and_centers(
    vertices: np.ndarray, surfaces: Iterable[tuple[int, ...]]
) -> tuple[np.ndarray, np.ndarray]:
    normals = []
    centers = []
    for surface in surfaces:
        pts = vertices[list(surface)]
        normal = _newell_normal(pts)
        norm = np.linalg.norm(normal)
        if norm == 0:
            normal = np.cross(pts[1] - pts[0], pts[2] - pts[0])
            norm = np.linalg.norm(normal)
        normals.append(normal / norm)
        centers.append(pts.mean(axis=0))
    return np.asarray(normals, dtype=float), np.asarray(centers, dtype=float)


def _newell_normal(points: np.ndarray) -> np.ndarray:
    normal = np.zeros(3, dtype=float)
    for idx, current in enumerate(points):
        nxt = points[(idx + 1) % len(points)]
        normal[0] += (current[1] - nxt[1]) * (current[2] + nxt[2])
        normal[1] += (current[2] - nxt[2]) * (current[0] + nxt[0])
        normal[2] += (current[0] - nxt[0]) * (current[1] + nxt[1])
    return normal
