from __future__ import annotations


class DiceSimError(Exception):
    """Base exception for Python dice GIF generation."""


class UnsupportedDiceError(DiceSimError, ValueError):
    """Raised when a requested die type is not implemented."""


class MissingDependencyError(DiceSimError, ImportError):
    """Raised when an optional runtime dependency is unavailable."""


class SimulationError(DiceSimError):
    """Raised when the physics simulation fails."""


class RenderError(DiceSimError):
    """Raised when software frame rendering fails."""


class GifEncodeError(DiceSimError):
    """Raised when animated GIF encoding or validation fails."""
