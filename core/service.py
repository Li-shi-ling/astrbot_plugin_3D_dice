from __future__ import annotations

import random
from pathlib import Path

from astrbot.api import logger
from astrbot.core.star.star_tools import StarTools
from astrbot.core.utils.astrbot_path import get_astrbot_temp_path

from .models import DiceRenderResult, DiceRequest, RenderConfig
from .parser import (
    normalize_theme,
    parse_bool_option,
    parse_command_text,
    parse_dice_notation,
)
from .renderer import CsDiceRenderer

PLUGIN_NAME = "astrbot_plugin_3D_dice"


class DiceService:
    def __init__(self, plugin_root: Path, config: RenderConfig):
        self.plugin_root = plugin_root
        self.config = config
        self.data_dir = StarTools.get_data_dir(PLUGIN_NAME)
        self.cache_dir = self.data_dir / "cache"
        self.temp_dir = Path(get_astrbot_temp_path()) / PLUGIN_NAME
        self.renderer = CsDiceRenderer(
            plugin_root, self.cache_dir, self.temp_dir, config
        )

    def build_request(self, command_text: str) -> DiceRequest:
        parsed = parse_command_text(command_text)
        dice = parse_dice_notation(parsed.notation, self.config.max_dice_count)
        seed = int(parsed.options.get("seed", random.randint(1, 999_999_999)))
        width = int(parsed.options.get("width", self.config.width))
        height = int(parsed.options.get("height", self.config.height))
        fps = int(parsed.options.get("fps", self.config.fps))
        frames = int(parsed.options.get("frames", self.config.frames))
        theme = normalize_theme(parsed.options.get("theme", self.config.theme))
        transparent = parse_bool_option(parsed.options.get("transparent", "false"))

        if width < 200 or height < 200:
            raise ValueError("Width and height must be at least 200.")
        if fps < 8 or fps > 40:
            raise ValueError("FPS must be between 8 and 40.")
        if frames < 12 or frames > 120:
            raise ValueError("Frames must be between 12 and 120.")

        return DiceRequest(
            dice=dice,
            seed=seed,
            width=width,
            height=height,
            fps=fps,
            frames=frames,
            theme=theme,
            transparent=transparent,
            debug=self.config.debug,
        )

    def render_from_text(self, command_text: str) -> DiceRenderResult:
        request = self.build_request(command_text)
        logger.info(
            "Rendering dice animation with seed=%s dice=%s theme=%s",
            request.seed,
            [(spec.count, spec.sides) for spec in request.dice],
            request.theme,
        )
        return self.renderer.render(request)
