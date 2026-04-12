from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

PLUGIN_DIR = Path(__file__).resolve().parents[1]
DEFAULT_SITE_DIR = PLUGIN_DIR / "dice_roller_app"


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
        "D10", "convex_polyhedron", "PentagonalTrapezohedron", 48, 0.12, 0.5, 0.3, 0.1, 0.55
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
    '{sides:10,label:"D10"}',
)


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
