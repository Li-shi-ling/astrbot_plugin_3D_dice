from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SUPPORTED_DICE_TYPES = ("D4", "D6", "D8", "D20")
COMMAND_NAMES = ("3d_dice", "3ddice", "dice3d", "roll3d", "投骰子", "骰子")
MAX_APP_DICE_COUNT = 6
DEFAULT_DICE_TYPE = "D6"
DEFAULT_DICE_COUNT = 1
DEFAULT_DURATION_MS = 2400
DEFAULT_FPS = 16
DEFAULT_WIDTH = 900
DEFAULT_HEIGHT = 1400


@dataclass(frozen=True)
class DiceRollRequest:
    dice_type: str
    count: int


@dataclass(frozen=True)
class DiceRenderOptions:
    duration: int
    fps: int
    browser: str | None
    better_render_quality: bool
    width: int
    height: int
    parallel_result: bool


def normalize_dice_type(value: Any) -> str:
    dice_type = str(value or "").strip().upper()
    if dice_type not in SUPPORTED_DICE_TYPES:
        supported = ", ".join(SUPPORTED_DICE_TYPES)
        raise ValueError(f"Unsupported dice type: {value}. Supported: {supported}.")
    return dice_type


def normalize_dice_count(value: Any, max_count: int = MAX_APP_DICE_COUNT) -> int:
    try:
        count = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Dice count must be an integer.") from exc

    effective_max = max(1, min(int(max_count), MAX_APP_DICE_COUNT))
    if count < 1 or count > effective_max:
        raise ValueError(f"Dice count must be between 1 and {effective_max}.")
    return count


def parse_roll_request(
    message: str, config: dict[str, Any] | None = None
) -> DiceRollRequest:
    normalized_config = normalize_config(config or {})
    cleaned = _strip_command_name(message)

    dice_type = normalized_config["default_dice_type"]
    count = normalized_config["default_count"]

    compact_match = re.search(r"\b([1-6])\s*d\s*(4|6|8|20)\b", cleaned, re.IGNORECASE)
    if compact_match:
        count = normalize_dice_count(
            compact_match.group(1), normalized_config["max_count"]
        )
        dice_type = normalize_dice_type(f"D{compact_match.group(2)}")
        return DiceRollRequest(dice_type=dice_type, count=count)

    dice_match = re.search(r"\bd\s*(4|6|8|20)\b", cleaned, re.IGNORECASE)
    if dice_match:
        dice_type = normalize_dice_type(f"D{dice_match.group(1)}")

    count_match = re.search(
        r"(?:\bcount\s*=\s*|\b数量\s*=?\s*|\b)([1-6])\b", cleaned, re.IGNORECASE
    )
    if count_match:
        count = normalize_dice_count(
            count_match.group(1), normalized_config["max_count"]
        )

    unsupported_match = re.search(r"\bd\s*(\d+)\b", cleaned, re.IGNORECASE)
    if (
        unsupported_match
        and f"D{unsupported_match.group(1)}".upper() not in SUPPORTED_DICE_TYPES
    ):
        normalize_dice_type(f"D{unsupported_match.group(1)}")

    unsupported_compact_match = re.search(
        r"\b[1-6]\s*d\s*(\d+)\b", cleaned, re.IGNORECASE
    )
    if (
        unsupported_compact_match
        and f"D{unsupported_compact_match.group(1)}".upper() not in SUPPORTED_DICE_TYPES
    ):
        normalize_dice_type(f"D{unsupported_compact_match.group(1)}")

    return DiceRollRequest(dice_type=dice_type, count=count)


def normalize_config(config: dict[str, Any]) -> dict[str, Any]:
    max_count = _int_in_range(
        config.get("max_count", MAX_APP_DICE_COUNT), 1, MAX_APP_DICE_COUNT
    )
    default_count = normalize_dice_count(
        config.get("default_count", DEFAULT_DICE_COUNT), max_count
    )
    return {
        "default_dice_type": normalize_dice_type(
            config.get("default_dice_type", DEFAULT_DICE_TYPE)
        ),
        "default_count": default_count,
        "max_count": max_count,
        "duration": _int_in_range(
            config.get("duration", DEFAULT_DURATION_MS), 1000, 8000
        ),
        "fps": _int_in_range(config.get("fps", DEFAULT_FPS), 4, 30),
        "browser": _optional_path_string(config.get("browser")),
        "auto_install_chromium": _bool_value(config.get("auto_install_chromium", True)),
        "better_render_quality": _bool_value(config.get("better_render_quality", True)),
        "width": _int_in_range(config.get("width", DEFAULT_WIDTH), 320, 1920),
        "height": _int_in_range(config.get("height", DEFAULT_HEIGHT), 320, 2400),
        "parallel_result": _bool_value(config.get("parallel_result", False)),
    }


def build_render_options(config: dict[str, Any] | None = None) -> DiceRenderOptions:
    normalized = normalize_config(config or {})
    return DiceRenderOptions(
        duration=normalized["duration"],
        fps=normalized["fps"],
        browser=normalized["browser"],
        better_render_quality=normalized["better_render_quality"],
        width=normalized["width"],
        height=normalized["height"],
        parallel_result=normalized["parallel_result"],
    )


def format_success_text(result: dict[str, Any]) -> str:
    dice_type = str(result["dice_type"]).upper()
    results = [int(value) for value in result["results"]]
    total = int(result["total"])
    dice_count = int(result.get("dice_count") or len(results) or 1)
    suffix = (
        " (fallback result; visual parsing timed out)" if result.get("fallback") else ""
    )
    if not results:
        return f"3D dice result: {dice_type} x {dice_count}; total {total}{suffix}"
    detail = " + ".join(str(value) for value in results)
    return f"3D dice result: {dice_type} x {len(results)} = {detail}; total {total}{suffix}"


def usage_text(max_count: int = MAX_APP_DICE_COUNT) -> str:
    supported = "/".join(SUPPORTED_DICE_TYPES)
    return f"Usage: /3d_dice [dice] [count], for example /3d_dice D20 2 or /3d_dice 2D6. Supported: {supported}, count 1-{max_count}."


def output_directory(base_dir: Path) -> Path:
    return Path(base_dir).resolve() / "outputs"


def _strip_command_name(message: str) -> str:
    cleaned = str(message or "").strip()
    if not cleaned:
        return ""
    first, _, rest = cleaned.partition(" ")
    command = first.lstrip("/").lower()
    if command in {name.lower() for name in COMMAND_NAMES}:
        return rest.strip()
    return cleaned


def _int_in_range(value: Any, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = minimum
    return max(minimum, min(parsed, maximum))


def _optional_path_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _bool_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() not in {"", "0", "false", "no", "off"}
    return bool(value)
