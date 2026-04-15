from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import astrbot.api.message_components as Comp
from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, StarTools, register

from .core import (
    CHROMIUM_INSTALLING_TEXT,
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
from .dice_runtime.render_dice import (
    close_persisted_session,
    detect_browser_path,
    ensure_chromium_browser,
    is_playwright_available,
    playwright_install_reminder,
    prewarm_render_worker,
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

        options = build_render_options(self.config)
        if options.prewarm_render_worker:
            browser_path = options.browser or await asyncio.to_thread(
                detect_browser_path
            )
            if not browser_path:
                logger.info(
                    "3D dice render worker prewarm skipped because no Chromium browser was found. "
                    "Chromium installation will only run on demand."
                )
                return
            try:
                await asyncio.to_thread(
                    prewarm_render_worker,
                    browser=browser_path,
                    width=options.width,
                    height=options.height,
                )
                logger.info("3D dice render worker prewarmed successfully.")
            except Exception as exc:
                logger.warning(
                    "3D dice render worker prewarm failed. Rendering will retry on demand: %s",
                    exc,
                )

    async def terminate(self) -> None:
        """插件卸载时关闭持久化浏览器会话。"""
        await asyncio.to_thread(close_persisted_session)

    @filter.command("3d_dice", alias={"3ddice", "dice3d", "roll3d", "投骰子", "骰子"})
    async def roll_dice(self, event: AstrMessageEvent):
        """Roll 3D dice and return an animated GIF."""
        if not is_playwright_available():
            logger.warning(playwright_install_reminder())
            yield event.plain_result(DEPENDENCY_UNAVAILABLE_TEXT)
            return

        try:
            request = parse_roll_request(event.message_str, self.config)
        except ValueError as exc:
            logger.info("3D dice rejected user request: %s", exc)
            yield event.plain_result(
                format_request_error(exc, self.config["max_count"])
            )
            return

        yield event.plain_result(
            f"正在投掷 {request.count} 个 {request.dice_type}，渲染 GIF 可能需要一点时间..."
        )

        options = build_render_options(self.config)
        browser_path = options.browser
        try:
            if self.auto_install_chromium and not browser_path:
                if not await asyncio.to_thread(detect_browser_path):
                    yield event.plain_result(CHROMIUM_INSTALLING_TEXT)
                setup_result = await asyncio.to_thread(ensure_chromium_browser, True)
                browser_path = setup_result.browser_path
                if setup_result.installed:
                    logger.info("3D dice installed Playwright Chromium on demand.")
            result = await asyncio.to_thread(
                render_dice_gif,
                dice_type=request.dice_type,
                count=request.count,
                duration=options.duration,
                fps=options.fps,
                browser=browser_path,
                output_dir=self.render_output_dir,
                width=options.width,
                height=options.height,
                gif_backend=options.gif_backend,
                ffmpeg_path=options.ffmpeg_path,
                screencast_quality=options.screencast_quality,
                better_render_quality=options.better_render_quality,
                parallel_result=options.parallel_result,
                result_timeout_ms=options.result_timeout_ms,
                result_mode=options.result_mode,
            )
        except Exception:
            logger.exception("3D dice render failed")
            yield event.plain_result(RENDER_FAILED_TEXT)
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
            logger.warning(playwright_install_reminder())
            yield event.plain_result(DEPENDENCY_UNAVAILABLE_TEXT)
            return

        yield event.plain_result(usage_text(self.config["max_count"]))
