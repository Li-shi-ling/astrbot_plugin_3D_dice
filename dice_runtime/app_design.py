from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

PLUGIN_DIR = Path(__file__).resolve().parents[1]
DEFAULT_SITE_DIR = PLUGIN_DIR / "dice_roller_app"
D10_RING_HEIGHT_RATIO = 0.1056
D10_RING_RADIUS_RATIO = 0.75
D10_POLAR_HEIGHT_RATIO = 1.0


@dataclass(frozen=True)
class DicePhysicsDesign:
    dice_type: str
    body_kind: str
    geometry: str
    mass: float
    friction: float
    restitution: float
    angular_damping: float
    linear_damping: float
    size_scale: float


@dataclass(frozen=True)
class DiceAppDesign:
    page_chunk: Path
    dice: dict[str, DicePhysicsDesign]
    d4_result_normals: dict[int, tuple[int, int, int]]
    d8_result_normals: dict[int, tuple[int, int, int]]
    roll_impulse_expression: str


PHYSICS_DESIGN: dict[str, DicePhysicsDesign] = {
    "D4": DicePhysicsDesign(
        "D4", "convex_polyhedron", "TetrahedronGeometry", 40, 0.15, 0.5, 0.3, 0.1, 0.84
    ),
    "D6": DicePhysicsDesign("D6", "box", "box mesh", 50, 0.1, 0.6, 0.3, 0.1, 0.5),
    "D8": DicePhysicsDesign(
        "D8", "convex_polyhedron", "OctahedronGeometry", 45, 0.12, 0.5, 0.3, 0.1, 0.715
    ),
    "D10": DicePhysicsDesign(
        "D10",
        "convex_polyhedron",
        "PentagonalTrapezohedron",
        48,
        0.12,
        0.5,
        0.3,
        0.1,
        0.55,
    ),
    "D20": DicePhysicsDesign(
        "D20", "convex_polyhedron", "IcosahedronGeometry", 52, 0.1, 0.5, 0.3, 0.1, 0.77
    ),
}

D4_RESULT_NORMALS: dict[int, tuple[int, int, int]] = {
    1: (1, 1, 1),
    2: (1, -1, -1),
    3: (-1, 1, -1),
    4: (-1, -1, 1),
}

D8_RESULT_NORMALS: dict[int, tuple[int, int, int]] = {
    1: (1, 1, 1),
    2: (-1, 1, 1),
    3: (1, -1, 1),
    4: (1, 1, -1),
    5: (-1, -1, 1),
    6: (-1, 1, -1),
    7: (1, -1, -1),
    8: (-1, -1, -1),
}

ROLL_IMPULSE_EXPRESSION = (
    "wakeUp(); position=spawn; "
    "velocity=((random-.5)*20, random*15+10, (random-.5)*20); "
    "angularVelocity=((random-.5)*50, (random-.5)*50, (random-.5)*50); "
    "wakeUp()"
)

SOURCE_MARKERS = (
    "TetrahedronGeometry",
    "OctahedronGeometry",
    "IcosahedronGeometry",
    "velocity.set((Math.random()-.5)*20",
    "angularVelocity.set((Math.random()-.5)*50",
    "let M={4:{mass:40",
    "V={4:.84",
    "T.wakeUp&&T.wakeUp()",
    "T.position&&T.position.set&&T.position.set(...b)",
    "r=.1056*e",
    "n=.1056*t",
)


def d10_kite_planarity_errors(size: float = 1.0) -> list[float]:
    top = (0.0, D10_POLAR_HEIGHT_RATIO * size, 0.0)
    bottom = (0.0, -D10_POLAR_HEIGHT_RATIO * size, 0.0)
    upper = [
        (
            math.cos(index / 5 * math.pi * 2) * D10_RING_RADIUS_RATIO * size,
            D10_RING_HEIGHT_RATIO * size,
            math.sin(index / 5 * math.pi * 2) * D10_RING_RADIUS_RATIO * size,
        )
        for index in range(5)
    ]
    lower = [
        (
            math.cos(index / 5 * math.pi * 2 + math.pi / 5)
            * D10_RING_RADIUS_RATIO
            * size,
            -D10_RING_HEIGHT_RATIO * size,
            math.sin(index / 5 * math.pi * 2 + math.pi / 5)
            * D10_RING_RADIUS_RATIO
            * size,
        )
        for index in range(5)
    ]

    errors = []
    for index in range(5):
        errors.append(
            _point_to_plane_distance(
                lower[index],
                top,
                upper[index],
                upper[(index + 1) % 5],
            )
        )
    for index in range(5):
        errors.append(
            _point_to_plane_distance(
                upper[(index + 1) % 5],
                bottom,
                lower[index],
                lower[(index + 1) % 5],
            )
        )
    return errors


def _point_to_plane_distance(
    point: tuple[float, float, float],
    plane_a: tuple[float, float, float],
    plane_b: tuple[float, float, float],
    plane_c: tuple[float, float, float],
) -> float:
    ab = _subtract(plane_b, plane_a)
    ac = _subtract(plane_c, plane_a)
    ap = _subtract(point, plane_a)
    normal = _cross(ab, ac)
    normal_length = math.sqrt(sum(component * component for component in normal))
    if normal_length == 0:
        return float("inf")
    return abs(_dot(ap, normal)) / normal_length


def _subtract(
    left: tuple[float, float, float],
    right: tuple[float, float, float],
) -> tuple[float, float, float]:
    return (left[0] - right[0], left[1] - right[1], left[2] - right[2])


def _cross(
    left: tuple[float, float, float],
    right: tuple[float, float, float],
) -> tuple[float, float, float]:
    return (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )


def _dot(
    left: tuple[float, float, float],
    right: tuple[float, float, float],
) -> float:
    return left[0] * right[0] + left[1] * right[1] + left[2] * right[2]


def find_dice_page_chunk(site_dir: Path | None = None) -> Path:
    root = Path(site_dir or DEFAULT_SITE_DIR).resolve()
    chunk_dir = root / "_next" / "static" / "chunks"
    if not chunk_dir.exists():
        raise FileNotFoundError(f"Next chunk directory not found: {chunk_dir}")

    candidates = []
    for path in chunk_dir.glob("*.js"):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        score = sum(marker in text for marker in SOURCE_MARKERS)
        if score:
            candidates.append((score, path))

    if not candidates:
        raise FileNotFoundError(f"Could not find dice page chunk under: {chunk_dir}")

    candidates.sort(key=lambda item: (-item[0], item[1].name))
    return candidates[0][1]


def verify_dice_page_chunk(path: Path) -> None:
    text = Path(path).read_text(encoding="utf-8")
    missing = [marker for marker in SOURCE_MARKERS if marker not in text]
    if missing:
        raise ValueError(f"Dice page chunk is missing expected markers: {missing}")


def load_reverse_engineered_design(site_dir: Path | None = None) -> DiceAppDesign:
    page_chunk = find_dice_page_chunk(site_dir)
    verify_dice_page_chunk(page_chunk)
    return DiceAppDesign(
        page_chunk=page_chunk,
        dice=PHYSICS_DESIGN,
        d4_result_normals=D4_RESULT_NORMALS,
        d8_result_normals=D8_RESULT_NORMALS,
        roll_impulse_expression=ROLL_IMPULSE_EXPRESSION,
    )
