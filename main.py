from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import astrbot.api.message_components as Comp
from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, StarTools, register

from .core import (
    build_render_options,
    format_success_text,
    normalize_config,
    output_directory,
    parse_roll_request,
    usage_text,
)
from .dice_runtime.render_dice import (
    ensure_chromium_browser,
    is_playwright_available,
    playwright_install_reminder,
    render_dice_gif,
)


@register(
    "astrbot_plugin_3D_dice",
    "Lishining",
    "Roll 3D animated dice and return the result as a GIF.",
    "1.0.0",
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
        self.auto_install_chromium = bool(
            self.config.get("auto_install_chromium", True)
        )

    async def initialize(self) -> None:
        if not is_playwright_available():
            logger.warning(playwright_install_reminder())
            return

        if not self.auto_install_chromium or self.config.get("browser"):
            return

        try:
            setup_result = await asyncio.to_thread(ensure_chromium_browser, True)
        except Exception as exc:
            logger.warning(
                "3D dice Chromium auto-install failed. Rendering will retry on demand: %s",
                exc,
            )
            return

        if setup_result.installed:
            logger.info("3D dice installed Playwright Chromium automatically.")

    @filter.command("3d_dice", alias={"3ddice", "dice3d", "roll3d", "投骰子", "骰子"})
    async def roll_dice(self, event: AstrMessageEvent):
        """Roll 3D dice and return an animated GIF."""
        if not is_playwright_available():
            yield event.plain_result(playwright_install_reminder())
            return

        try:
            request = parse_roll_request(event.message_str, self.config)
        except ValueError as exc:
            yield event.plain_result(f"{exc}\n{usage_text(self.config['max_count'])}")
            return

        yield event.plain_result(
            f"Rolling {request.count} {request.dice_type} dice. Rendering may take a moment..."
        )

        options = build_render_options(self.config)
        try:
            if self.auto_install_chromium and not options.browser:
                await asyncio.to_thread(ensure_chromium_browser, True)
            result = await asyncio.to_thread(
                render_dice_gif,
                dice_type=request.dice_type,
                count=request.count,
                duration=options.duration,
                fps=options.fps,
                browser=options.browser,
                output_dir=self.render_output_dir,
                width=options.width,
                height=options.height,
            )
        except Exception as exc:
            logger.exception("3D dice render failed")
            yield event.plain_result(f"3D dice render failed: {exc}")
            return

        gif_path = str(Path(result["gif_path"]).resolve())
        yield event.chain_result(
            [
                Comp.Plain(format_success_text(result)),
                Comp.Image.fromFileSystem(gif_path),
            ]
        )

    @filter.command("3d_dice_help", alias={"骰子帮助", "投骰子帮助"})
    async def help(self, event: AstrMessageEvent):
        """Show 3D dice usage."""
        if not is_playwright_available():
            yield event.plain_result(playwright_install_reminder())
            return

        yield event.plain_result(usage_text(self.config["max_count"]))
