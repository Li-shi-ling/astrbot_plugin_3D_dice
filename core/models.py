from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

SUPPORTED_SIDES = (6,)
DEFAULT_THEME = "classic"


@dataclass(slots=True)
class DiceSpec:
    count: int
    sides: int


@dataclass(slots=True)
class RenderConfig:
    playwright_path: str = "playwright"
    width: int = 480
    height: int = 480
    fps: int = 20
    frames: int = 36
    theme: str = DEFAULT_THEME
    max_dice_count: int = 8
    timeout_ms: int = 30_000
    debug: bool = False


@dataclass(slots=True)
class DiceRequest:
    dice: list[DiceSpec]
    seed: int
    width: int
    height: int
    fps: int
    frames: int
    theme: str = DEFAULT_THEME
    transparent: bool = False
    debug: bool = False
    output_path: Path | None = None

    @property
    def dice_count(self) -> int:
        return sum(spec.count for spec in self.dice)

    def to_payload(self) -> dict:
        return {
            "seed": self.seed,
            "width": self.width,
            "height": self.height,
            "fps": self.fps,
            "frames": self.frames,
            "theme": self.theme,
            "transparent": self.transparent,
            "dice": [{"count": spec.count, "sides": spec.sides} for spec in self.dice],
        }


@dataclass(slots=True)
class RenderedFrame:
    polygons: list[dict] = field(default_factory=list)
    labels: list[dict] = field(default_factory=list)


@dataclass(slots=True)
class DiceRenderResult:
    image_path: Path
    values: list[int]
    dice_labels: list[str]
    preview_path: Path | None = None
    cached: bool = False

    @property
    def summary(self) -> str:
        pairs = [
            f"{label}={value}" for label, value in zip(self.dice_labels, self.values)
        ]
        return "Roll result: " + ", ".join(pairs)
