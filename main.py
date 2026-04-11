from __future__ import annotations

from pathlib import Path

import astrbot.api.message_components as Comp
from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register

from .core.models import RenderConfig
from .core.service import DiceService


def _config_value(config: AstrBotConfig, key: str, default):
    value = config.get(key, default)
    return default if value in (None, "") else value


@register(
    "astrbot_plugin_3D_dice",
    "OpenAI Codex",
    "Render cs.html style animated 3D d6 GIFs.",
    "0.1.0",
)
class DicePlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig | None = None):
        super().__init__(context)
        self.config = config or AstrBotConfig()
        self.plugin_root = Path(__file__).resolve().parent
        self.service = DiceService(self.plugin_root, self._build_render_config())

    def _build_render_config(self) -> RenderConfig:
        return RenderConfig(
            playwright_path=str(
                _config_value(self.config, "playwright_path", "playwright")
            ),
            width=int(_config_value(self.config, "default_width", 480)),
            height=int(_config_value(self.config, "default_height", 480)),
            fps=int(_config_value(self.config, "default_fps", 20)),
            frames=int(_config_value(self.config, "default_frames", 36)),
            theme=str(_config_value(self.config, "default_theme", "classic")),
            max_dice_count=int(_config_value(self.config, "max_dice_count", 8)),
            timeout_ms=int(_config_value(self.config, "timeout_ms", 30000)),
            debug=bool(_config_value(self.config, "debug", False)),
        )

    @filter.command("dice")
    async def roll_dice(self, event: AstrMessageEvent):
        """Render cs.html style 3D d6 GIFs. Example: /dice 2d6 theme=ember seed=42"""
        try:
            result = self.service.render_from_text(event.message_str)
        except Exception as exc:
            logger.warning("Dice render failed: %s", exc)
            yield event.plain_result(
                f"Dice render failed: {exc}\nExample: /dice 2d6 theme=classic seed=42",
            )
            return

        chain = [
            Comp.Image.fromFileSystem(str(result.image_path)),
            Comp.Plain(f"{result.summary} | cached={result.cached}"),
        ]
        yield event.chain_result(chain)

    @filter.command("dice_help")
    async def dice_help(self, event: AstrMessageEvent):
        """Show dice plugin help."""
        yield event.plain_result(
            "\n".join(
                [
                    "Usage: /dice <notation> [theme=<name>] [seed=<int>] [width=<int>] [height=<int>] [fps=<int>] [frames=<int>] [transparent=true|false]",
                    "Supported dice: d6 only",
                    "Themes: classic, ember, emerald, midnight",
                    "Examples:",
                    "/dice d6",
                    "/dice 2d6 theme=ember",
                    "/dice 3d6 seed=42",
                ],
            ),
        )
