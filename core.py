from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from .dice_sim import SUPPORTED_DICE_TYPES, RollGifResult, StyleOptions
except ImportError:  # Allows direct test imports from the plugin directory.
    from dice_sim import SUPPORTED_DICE_TYPES, RollGifResult, StyleOptions

COMMAND_NAMES = ("3d_dice", "3ddice", "dice3d", "roll3d", "投骰子", "骰子")
MAX_APP_DICE_COUNT = 6
DEFAULT_DICE_TYPE = "D6"
DEFAULT_DICE_COUNT = 1
DEFAULT_DURATION_MS = 5000
DEFAULT_FINAL_HOLD_MS = 3000
DEFAULT_FPS = 12
DEFAULT_WIDTH = 640
DEFAULT_HEIGHT = 480

DEPENDENCY_UNAVAILABLE_TEXT = (
    "3D骰子功能还没准备好：缺少 Python 物理/GIF 依赖。"
    "请联系管理员执行 pip install -r requirements.txt 后再试。"
)
RENDER_FAILED_TEXT = (
    "这次3D骰子没有生成成功，详细错误已经写入日志。"
    "请稍后再试，或联系管理员查看 AstrBot 日志。"
)


@dataclass(frozen=True)
class DiceRollRequest:
    dice_type: str
    count: int
    seed: int | None = None


@dataclass(frozen=True)
class DiceRenderOptions:
    duration_ms: int
    final_hold_ms: int
    fps: int
    width: int
    height: int
    seed: int | None
    style: StyleOptions
    max_cache_files: int
    cache_max_age_seconds: int


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
    seed = _parse_seed(cleaned)

    dice_type = normalized_config["default_dice_type"]
    count = normalized_config["default_count"]

    compact_match = re.search(r"\b([1-9]\d*)\s*d\s*(\d+)\b", cleaned, re.IGNORECASE)
    if compact_match:
        count = normalize_dice_count(compact_match.group(1), normalized_config["max_count"])
        dice_type = normalize_dice_type(f"D{compact_match.group(2)}")
        return DiceRollRequest(dice_type=dice_type, count=count, seed=seed)

    dice_match = re.search(r"\bd\s*(\d+)\b", cleaned, re.IGNORECASE)
    if dice_match:
        dice_type = normalize_dice_type(f"D{dice_match.group(1)}")

    count_match = re.search(
        r"(?:\bcount\s*=\s*|\bcount\s+|\b数量\s*=?\s*)([1-9]\d*)\b",
        cleaned,
        re.IGNORECASE,
    )
    if count_match:
        count = normalize_dice_count(count_match.group(1), normalized_config["max_count"])

    return DiceRollRequest(dice_type=dice_type, count=count, seed=seed)


def normalize_config(config: dict[str, Any]) -> dict[str, Any]:
    max_count = _int_in_range(
        config.get("max_count", MAX_APP_DICE_COUNT), 1, MAX_APP_DICE_COUNT
    )
    default_count = normalize_dice_count(config.get("default_count", DEFAULT_DICE_COUNT), max_count)
    seed = _optional_int(config.get("seed"))
    return {
        "default_dice_type": normalize_dice_type(config.get("default_dice_type", DEFAULT_DICE_TYPE)),
        "default_count": default_count,
        "max_count": max_count,
        "duration_ms": _int_in_range(
            config.get("duration_ms", config.get("duration", DEFAULT_DURATION_MS)),
            800,
            10000,
        ),
        "final_hold_ms": _int_in_range(
            config.get("final_hold_ms", DEFAULT_FINAL_HOLD_MS),
            3000,
            5000,
        ),
        "fps": _int_in_range(config.get("fps", DEFAULT_FPS), 4, 30),
        "width": _int_in_range(config.get("width", DEFAULT_WIDTH), 240, 1024),
        "height": _int_in_range(config.get("height", DEFAULT_HEIGHT), 240, 1024),
        "seed": seed,
        "die_color": _optional_color(config.get("die_color"), "#ffffff"),
        "background_color": _optional_color(config.get("background_color"), "#f5f7fb"),
        "max_cache_files": _int_in_range(config.get("max_cache_files", 80), 1, 1000),
        "cache_max_age_seconds": _int_in_range(config.get("cache_max_age_seconds", 604800), 0, 31536000),
    }


def build_render_options(config: dict[str, Any] | None = None) -> DiceRenderOptions:
    normalized = normalize_config(config or {})
    return DiceRenderOptions(
        duration_ms=normalized["duration_ms"],
        final_hold_ms=normalized["final_hold_ms"],
        fps=normalized["fps"],
        width=normalized["width"],
        height=normalized["height"],
        seed=normalized["seed"],
        style=StyleOptions(
            die_color=normalized["die_color"],
            background_color=normalized["background_color"],
        ),
        max_cache_files=normalized["max_cache_files"],
        cache_max_age_seconds=normalized["cache_max_age_seconds"],
    )


def format_success_text(result: RollGifResult | dict[str, Any]) -> str:
    data = result.as_dict() if isinstance(result, RollGifResult) else dict(result)
    dice_type = str(data["dice_type"]).upper()
    results = [int(value) for value in data["results"]]
    total = int(data["total"])
    seed = int(data["seed"])
    detail = " + ".join(str(value) for value in results)
    return f"3D dice result: {dice_type} x {len(results)} = {detail}; total {total}; seed {seed}"


def format_request_error(error: Exception, max_count: int = MAX_APP_DICE_COUNT) -> str:
    message = str(error)
    if "Unsupported dice type" in message:
        supported = "/".join(SUPPORTED_DICE_TYPES)
        return f"这个骰子类型暂时不支持。当前可用：{supported}。\n{usage_text(max_count)}"
    if "count" in message.lower() or "integer" in message.lower():
        return f"骰子数量需要在 1 到 {max_count} 之间。\n{usage_text(max_count)}"
    return f"指令格式没有识别出来。\n{usage_text(max_count)}"


def usage_text(max_count: int = MAX_APP_DICE_COUNT) -> str:
    supported = "/".join(SUPPORTED_DICE_TYPES)
    return (
        f"Usage: /roll3d [dice] [count] [seed=123], for example "
        f"/roll3d D20, /roll3d 2D6, or /roll3d D10 count=2 seed=42. "
        f"Supported: {supported}, count 1-{max_count}."
    )


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


def _parse_seed(message: str) -> int | None:
    match = re.search(r"(?:--seed\s+|\bseed\s*=\s*)(-?\d+)\b", message, re.IGNORECASE)
    if not match:
        return None
    return int(match.group(1))


def _int_in_range(value: Any, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = minimum
    return max(minimum, min(parsed, maximum))


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        return None


def _optional_color(value: Any, default: str) -> str:
    text = str(value or default).strip()
    if re.fullmatch(r"#[0-9a-fA-F]{6}", text):
        return text
    return default
