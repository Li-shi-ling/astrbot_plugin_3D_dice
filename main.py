import asyncio
import re
from pathlib import Path

import astrbot.api.message_components as Comp
from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register
from astrbot.core.utils.astrbot_path import get_astrbot_temp_path

from .src.render_dice import render_dice_gif

DEFAULT_DICE_TYPE = "D6"
DEFAULT_DICE_COUNT = 1
DEFAULT_DURATION_MS = 2400
DEFAULT_FPS = 16
MAX_DICE_COUNT = 10
MAX_DURATION_MS = 10000
MAX_FPS = 30


@register(
    "astrbot_plugin_3D_dice",
    "Lishining",
    "Render animated 3D dice rolls and return the result as a GIF.",
    "1.0.0",
)
class DicePlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig | None = None):
        super().__init__(context)
        self.config = config or {}
        self.plugin_dir = Path(__file__).resolve().parent
        self.output_dir = Path(get_astrbot_temp_path()) / "astrbot_plugin_3D_dice"
        self.site_dir = self._resolve_optional_path(self.config.get("site_dir")) or (
            self.plugin_dir / "rollmydice_app"
        )
        self.browser_path = self._resolve_optional_path(self.config.get("browser_path"))
        self.default_duration = self._clamp_int(
            self.config.get("default_duration_ms", DEFAULT_DURATION_MS),
            minimum=500,
            maximum=MAX_DURATION_MS,
            fallback=DEFAULT_DURATION_MS,
        )
        self.default_fps = self._clamp_int(
            self.config.get("default_fps", DEFAULT_FPS),
            minimum=1,
            maximum=MAX_FPS,
            fallback=DEFAULT_FPS,
        )
        self.linux_render_mode = self._normalize_linux_render_mode(
            self.config.get("linux_render_mode", "auto")
        )

    async def initialize(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info("[3D_dice] Plugin initialized")

    @filter.command("dice", alias={"\u6295\u9ab0\u5b50", "r"})
    async def roll_dice(self, event: AstrMessageEvent, dice_expr: str = ""):
        """Roll a 3D dice animation. Examples: /dice, /dice d20, /dice 3d6."""

        if not dice_expr:
            parts = event.message_str.strip().split(maxsplit=1)
            dice_expr = parts[1] if len(parts) > 1 else ""

        try:
            dice_count, dice_type = self._parse_dice_expression(dice_expr)
        except ValueError as exc:
            yield event.plain_result(str(exc))
            return

        if not self.site_dir.exists():
            yield event.plain_result(
                "Dice assets directory is missing. Put the web app in "
                f"{self.site_dir} or configure `site_dir`."
            )
            return

        yield event.plain_result(f"Rolling {dice_count} {dice_type}...")

        try:
            result = await asyncio.to_thread(
                render_dice_gif,
                dice_type=dice_type,
                count=dice_count,
                duration=self.default_duration,
                fps=self.default_fps,
                browser=str(self.browser_path) if self.browser_path else None,
                output_dir=self.output_dir,
                site_dir=self.site_dir,
                linux_render_mode=self.linux_render_mode,
            )
        except FileNotFoundError as exc:
            yield event.plain_result(f"Runtime dependency missing: {exc}")
            return
        except Exception as exc:
            logger.exception("[3D_dice] Failed to render dice GIF")
            yield event.plain_result(f"Dice rendering failed: {exc}")
            return

        gif_path = Path(result["gif_path"])
        results = result.get("results", [])
        total = result.get("total")
        summary = f"{dice_count}{dice_type} -> {results}"
        if total is not None:
            summary = f"{summary} | total={total}"

        yield event.chain_result(
            [
                Comp.Plain(summary),
                Comp.Image.fromFileSystem(str(gif_path)),
            ]
        )

    async def terminate(self):
        logger.info("[3D_dice] Plugin terminated")

    def _parse_dice_expression(self, expression: str) -> tuple[int, str]:
        cleaned = expression.strip().upper()
        if not cleaned:
            return DEFAULT_DICE_COUNT, DEFAULT_DICE_TYPE

        match = re.fullmatch(r"(?:(\d+)\s*)?D(\d+)", cleaned)
        if not match:
            raise ValueError("Usage: /dice [d4|d6|d8|d20|NdX], for example /dice 3d6")

        count = int(match.group(1) or DEFAULT_DICE_COUNT)
        dice_faces = int(match.group(2))
        dice_type = f"D{dice_faces}"

        if count < 1 or count > MAX_DICE_COUNT:
            raise ValueError(f"Dice count must be between 1 and {MAX_DICE_COUNT}.")
        if dice_type not in {"D4", "D6", "D8", "D20"}:
            raise ValueError("Supported dice types: d4, d6, d8, d20.")

        return count, dice_type

    @staticmethod
    def _resolve_optional_path(raw_path: str | None) -> Path | None:
        if not raw_path:
            return None
        return Path(raw_path).expanduser().resolve()

    @staticmethod
    def _clamp_int(value: object, minimum: int, maximum: int, fallback: int) -> int:
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            return fallback
        return max(minimum, min(maximum, parsed))

    @staticmethod
    def _normalize_linux_render_mode(value: object) -> str:
        normalized = str(value or "auto").strip().lower()
        if normalized not in {"auto", "headless", "xvfb"}:
            return "auto"
        return normalized
