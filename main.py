from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import astrbot.api.message_components as Comp
from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, StarTools, register

from .core import (
    DEPENDENCY_UNAVAILABLE_TEXT,
    RENDER_FAILED_TEXT,
    build_render_options,
    format_request_error,
    format_success_text,
    normalize_config,
    output_directory,
    parse_roll_request,
    usage_text,
)
from .dice_sim import DiceSimError, MissingDependencyError, roll_gif


@register(
    "astrbot_plugin_3D_dice",
    "Lishining",
    "Generate Python-simulated 3D dice roll GIFs.",
    "2.0.0",
    "https://github.com/Li-shi-ling/astrbot_plugin_3D_dice",
)
class ThreeDDicePlugin(Star):
    def __init__(
        self, context: Context, config: AstrBotConfig | dict[str, Any] | None = None
    ):
        super().__init__(context)
        self.config = normalize_config(dict(config or {}))
        self.data_dir = Path(StarTools.get_data_dir("astrbot_plugin_3D_dice"))
        self.render_output_dir = output_directory(self.data_dir)
        self.render_output_dir.mkdir(parents=True, exist_ok=True)

    @filter.command("3d_dice", alias={"3ddice", "dice3d", "roll3d", "投骰子", "骰子"})
    async def roll_dice(self, event: AstrMessageEvent):
        try:
            request = parse_roll_request(event.message_str, self.config)
        except ValueError as exc:
            logger.info("3D dice rejected user request: %s", exc)
            yield event.plain_result(format_request_error(exc, self.config["max_count"]))
            return

        options = build_render_options(self.config)
        seed = request.seed if request.seed is not None else options.seed
        yield event.plain_result(
            f"正在用 Python 物理仿真投掷 {request.count} 个 {request.dice_type}，GIF 生成可能需要一点时间..."
        )

        try:
            result = await asyncio.to_thread(
                roll_gif,
                request.dice_type,
                count=request.count,
                output_dir=self.render_output_dir,
                seed=seed,
                width=options.width,
                height=options.height,
                fps=options.fps,
                duration_ms=options.duration_ms,
                final_hold_ms=options.final_hold_ms,
                style=options.style,
                max_cache_files=options.max_cache_files,
                cache_max_age_seconds=options.cache_max_age_seconds,
            )
        except MissingDependencyError:
            logger.exception("3D dice dependency unavailable")
            yield event.plain_result(DEPENDENCY_UNAVAILABLE_TEXT)
            return
        except DiceSimError:
            logger.exception("3D dice generation failed")
            yield event.plain_result(RENDER_FAILED_TEXT)
            return
        except Exception:
            logger.exception("Unexpected 3D dice generation failure")
            yield event.plain_result(RENDER_FAILED_TEXT)
            return

        gif_path = str(Path(result.gif_path).resolve())
        yield event.chain_result(
            [
                Comp.Plain(format_success_text(result)),
                Comp.Image.fromFileSystem(gif_path),
            ]
        )

    @filter.command("3d_dice_help", alias={"骰子帮助", "投骰子帮助"})
    async def help(self, event: AstrMessageEvent):
        yield event.plain_result(usage_text(self.config["max_count"]))
