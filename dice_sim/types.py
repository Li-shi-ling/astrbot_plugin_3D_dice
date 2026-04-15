from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

import numpy as np


@dataclass(frozen=True)
class MeshData:
    dice_type: str
    vertices: np.ndarray
    faces: np.ndarray
    result_normals: np.ndarray
    result_values: tuple[int, ...]
    result_rule: str
    result_centers: np.ndarray
    render_faces: tuple[tuple[int, ...], ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class BodyPose:
    position: tuple[float, float, float]
    orientation: tuple[float, float, float, float]


@dataclass(frozen=True)
class SimulationFrame:
    time_seconds: float
    poses: tuple[BodyPose, ...]


@dataclass(frozen=True)
class SimulationResult:
    frames: tuple[SimulationFrame, ...]
    final_poses: tuple[BodyPose, ...]
    seed: int


@dataclass(frozen=True)
class StyleOptions:
    die_color: str = "#d83a34"
    background_color: str = "#f5f7fb"
    ink_color: str = "#ffffff"
    label_color: str = "#20242c"


@dataclass(frozen=True)
class RollOptions:
    dice_type: str
    count: int = 1
    output_dir: Path | str | None = None
    output_path: Path | str | None = None
    seed: int | None = None
    width: int = 480
    height: int = 360
    fps: int = 12
    duration_ms: int = 2200
    style: StyleOptions = field(default_factory=StyleOptions)
    max_cache_files: int = 80
    cache_max_age_seconds: int = 604800


@dataclass(frozen=True)
class RollGifResult:
    gif_path: Path
    dice_type: str
    dice_count: int
    results: tuple[int, ...]
    total: int
    seed: int
    width: int
    height: int
    fps: int
    duration_ms: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "gif_path": str(self.gif_path),
            "dice_type": self.dice_type,
            "dice_count": self.dice_count,
            "results": list(self.results),
            "total": self.total,
            "seed": self.seed,
            "width": self.width,
            "height": self.height,
            "fps": self.fps,
            "duration_ms": self.duration_ms,
            "metadata": dict(self.metadata),
        }


FrameImages = Sequence[Any]
