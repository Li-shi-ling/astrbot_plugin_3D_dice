from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageColor, ImageDraw, ImageFont

from .models import DiceRenderResult, DiceRequest, RenderConfig


def _rgba(color: str, alpha: int = 255) -> tuple[int, int, int, int]:
    red, green, blue = ImageColor.getrgb(color)
    return red, green, blue, alpha


class NodeRenderer:
    def __init__(
        self, plugin_root: Path, cache_dir: Path, temp_dir: Path, config: RenderConfig
    ):
        self.plugin_root = plugin_root
        self.cache_dir = cache_dir
        self.temp_dir = temp_dir
        self.config = config
        self.cli_path = self.plugin_root / "renderer" / "cli.js"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def render(self, request: DiceRequest) -> DiceRenderResult:
        payload = request.to_payload()
        payload_hash = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8"),
        ).hexdigest()
        gif_path = self.cache_dir / f"dice_{payload_hash}.gif"
        meta_path = self.cache_dir / f"dice_{payload_hash}.json"
        if gif_path.exists() and meta_path.exists():
            metadata = json.loads(meta_path.read_text(encoding="utf-8"))
            return DiceRenderResult(
                image_path=gif_path,
                values=metadata["values"],
                dice_labels=metadata["dice_labels"],
                cached=True,
            )

        request_path = self.temp_dir / f"request_{payload_hash}.json"
        response_path = self.temp_dir / f"response_{payload_hash}.json"
        request_path.write_text(json.dumps(payload), encoding="utf-8")

        subprocess.run(
            [
                self.config.node_path,
                str(self.cli_path),
                "--input",
                str(request_path),
                "--output",
                str(response_path),
            ],
            cwd=str(self.plugin_root),
            check=True,
            capture_output=True,
            text=True,
            timeout=max(1, self.config.timeout_ms // 1000),
        )

        response = json.loads(response_path.read_text(encoding="utf-8"))
        self._write_gif(gif_path, response, request)
        meta_path.write_text(
            json.dumps(
                {
                    "values": response["values"],
                    "dice_labels": response["dice_labels"],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        return DiceRenderResult(
            image_path=gif_path,
            values=response["values"],
            dice_labels=response["dice_labels"],
            cached=False,
        )

    def _write_gif(self, gif_path: Path, response: dict, request: DiceRequest) -> None:
        frames: list[Image.Image] = []
        font = ImageFont.load_default()
        for frame in response["frames"]:
            frames.append(
                self._render_frame(
                    frame=frame,
                    theme=response["theme"],
                    transparent=request.transparent,
                    font=font,
                ),
            )
        duration = max(20, int(1000 / max(1, request.fps)))
        frames[0].save(
            gif_path,
            save_all=True,
            append_images=frames[1:],
            duration=duration,
            loop=0,
            disposal=2,
            optimize=False,
        )

    def _render_frame(
        self,
        frame: dict,
        theme: dict,
        transparent: bool,
        font: ImageFont.ImageFont,
    ) -> Image.Image:
        size = (int(theme["width"]), int(theme["height"]))
        if transparent:
            image = Image.new("RGBA", size, (0, 0, 0, 0))
        else:
            image = Image.new("RGBA", size, _rgba(theme["background_top"]))
            draw = ImageDraw.Draw(image)
            self._draw_background(draw, size, theme)

        draw = ImageDraw.Draw(image)
        for polygon in frame["polygons"]:
            points = [tuple(point) for point in polygon["points"]]
            draw.polygon(
                points,
                fill=_rgba(polygon["fill"], polygon.get("alpha", 255)),
                outline=_rgba(polygon["outline"]),
            )

        for label in frame["labels"]:
            text = str(label["text"])
            bbox = draw.textbbox((0, 0), text, font=font)
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            x = label["x"] - width / 2
            y = label["y"] - height / 2
            draw.text((x + 1, y + 1), text, fill=_rgba("#111111", 120), font=font)
            draw.text((x, y), text, fill=_rgba(label["color"]), font=font)
        return image

    def _draw_background(
        self, draw: ImageDraw.ImageDraw, size: tuple[int, int], theme: dict
    ) -> None:
        width, height = size
        top = ImageColor.getrgb(theme["background_top"])
        bottom = ImageColor.getrgb(theme["background_bottom"])
        for row in range(height):
            ratio = row / max(1, height - 1)
            color = tuple(
                int(top[index] + (bottom[index] - top[index]) * ratio)
                for index in range(3)
            )
            draw.line([(0, row), (width, row)], fill=color)
        horizon = int(height * 0.73)
        draw.rectangle(
            [(0, horizon), (width, height)],
            fill=ImageColor.getrgb(theme["floor_color"]),
        )
