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
    settled: bool = False
    settle_time_seconds: float | None = None
    final_linear_speeds: tuple[float, ...] = field(default_factory=tuple)
    final_angular_speeds: tuple[float, ...] = field(default_factory=tuple)
    horizontal_travel: float = 0.0
    max_height: float = 0.0
    final_contact_vertices: tuple[int, ...] = field(default_factory=tuple)
    inter_body_contact_count: int = 0
    inter_body_contact_steps: int = 0


@dataclass(frozen=True)
class StyleOptions:
    die_color: str = "#ffffff"
    background_color: str = "#f5f7fb"
    ink_color: str = "#000000"
    edge_color: str = "#000000"
    label_color: str = "#000000"


@dataclass(frozen=True)
class RollOptions:
    dice_type: str
    count: int = 1
    output_dir: Path | str | None = None
    output_path: Path | str | None = None
    seed: int | None = None
    width: int = 640
    height: int = 480
    fps: int = 12
    duration_ms: int = 5000
    final_hold_ms: int = 3500
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
    final_hold_ms: int
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
            "final_hold_ms": self.final_hold_ms,
            "metadata": dict(self.metadata),
        }


FrameImages = Sequence[Any]
