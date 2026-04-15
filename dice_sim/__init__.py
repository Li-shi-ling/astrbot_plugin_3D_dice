from __future__ import annotations

from .errors import (
    DiceSimError,
    GifEncodeError,
    MissingDependencyError,
    RenderError,
    SimulationError,
    UnsupportedDiceError,
)
from .generator import roll_gif, roll_gif_with_options
from .geometry import SUPPORTED_DICE_TYPES, create_mesh
from .types import RollGifResult, RollOptions, StyleOptions

__all__ = [
    "DiceSimError",
    "GifEncodeError",
    "MissingDependencyError",
    "RenderError",
    "RollGifResult",
    "RollOptions",
    "SUPPORTED_DICE_TYPES",
    "SimulationError",
    "StyleOptions",
    "UnsupportedDiceError",
    "create_mesh",
    "roll_gif",
    "roll_gif_with_options",
]
