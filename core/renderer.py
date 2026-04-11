from __future__ import annotations

import hashlib
import json
import math
import random
import shutil
import subprocess
from pathlib import Path
from urllib.parse import quote

from PIL import Image, ImageColor, ImageDraw

from .models import DiceRenderResult, DiceRequest, RenderConfig

RENDER_PIPELINE_VERSION = "cs-d6-v2-3d"
CAMERA_DISTANCE = 720.0
FACE_MAPPING = {
    "px": 2,
    "nx": 5,
    "py": 1,
    "ny": 6,
    "pz": 3,
    "nz": 4,
}
FACE_ORDER = ("pz", "px", "py", "ny", "nx", "nz")
FACE_NORMALS = {
    "px": (1.0, 0.0, 0.0),
    "nx": (-1.0, 0.0, 0.0),
    "py": (0.0, 1.0, 0.0),
    "ny": (0.0, -1.0, 0.0),
    "pz": (0.0, 0.0, 1.0),
    "nz": (0.0, 0.0, -1.0),
}
FACE_CORNERS = {
    "px": ((1, -1, -1), (1, -1, 1), (1, 1, 1), (1, 1, -1)),
    "nx": ((-1, -1, 1), (-1, -1, -1), (-1, 1, -1), (-1, 1, 1)),
    "py": ((-1, 1, -1), (1, 1, -1), (1, 1, 1), (-1, 1, 1)),
    "ny": ((-1, -1, 1), (1, -1, 1), (1, -1, -1), (-1, -1, -1)),
    "pz": ((-1, -1, 1), (-1, 1, 1), (1, 1, 1), (1, -1, 1)),
    "nz": ((1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, -1)),
}


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def _lerp(start: float, end: float, progress: float) -> float:
    return start + (end - start) * progress


def _ease_out_cubic(progress: float) -> float:
    return 1 - (1 - progress) ** 3


def _rgba(color: str, alpha: int = 255) -> tuple[int, int, int, int]:
    red, green, blue = ImageColor.getrgb(color)
    return red, green, blue, alpha


def _add(
    a: tuple[float, float, float], b: tuple[float, float, float]
) -> tuple[float, float, float]:
    return a[0] + b[0], a[1] + b[1], a[2] + b[2]


def _sub(
    a: tuple[float, float, float], b: tuple[float, float, float]
) -> tuple[float, float, float]:
    return a[0] - b[0], a[1] - b[1], a[2] - b[2]


def _dot(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(
    a: tuple[float, float, float], b: tuple[float, float, float]
) -> tuple[float, float, float]:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _scale(
    vector: tuple[float, float, float], factor: float
) -> tuple[float, float, float]:
    return vector[0] * factor, vector[1] * factor, vector[2] * factor


def _normalize(vector: tuple[float, float, float]) -> tuple[float, float, float]:
    length = math.sqrt(_dot(vector, vector))
    if length <= 1e-8:
        return (0.0, 0.0, 0.0)
    return vector[0] / length, vector[1] / length, vector[2] / length


def _rotate_xyz(
    point: tuple[float, float, float], rx: float, ry: float, rz: float
) -> tuple[float, float, float]:
    x, y, z = point

    cos_x = math.cos(rx)
    sin_x = math.sin(rx)
    y, z = y * cos_x - z * sin_x, y * sin_x + z * cos_x

    cos_y = math.cos(ry)
    sin_y = math.sin(ry)
    x, z = x * cos_y + z * sin_y, -x * sin_y + z * cos_y

    cos_z = math.cos(rz)
    sin_z = math.sin(rz)
    x, y = x * cos_z - y * sin_z, x * sin_z + y * cos_z
    return x, y, z


def _project_point(point: tuple[float, float, float]) -> tuple[float, float, float]:
    x, y, z = point
    scale = CAMERA_DISTANCE / max(120.0, CAMERA_DISTANCE - z)
    return x * scale, y * scale, z


def _target_orientation(face_value: int, random_y: float) -> tuple[float, float, float]:
    targets = {
        1: (0.0, random_y, 0.0),
        2: (0.0, random_y, -math.pi / 2),
        3: (math.pi / 2, random_y, 0.0),
        4: (-math.pi / 2, random_y, 0.0),
        5: (0.0, random_y, math.pi / 2),
        6: (math.pi, random_y, 0.0),
    }
    return targets[face_value]


def _pip_uv(value: int) -> list[tuple[float, float]]:
    inset = 0.28
    center = 0.5
    near = inset
    far = 1.0 - inset
    positions = {
        1: [(center, center)],
        2: [(near, near), (far, far)],
        3: [(near, near), (center, center), (far, far)],
        4: [(near, near), (far, near), (near, far), (far, far)],
        5: [(near, near), (far, near), (center, center), (near, far), (far, far)],
        6: [
            (near, near),
            (near, center),
            (near, far),
            (far, near),
            (far, center),
            (far, far),
        ],
    }
    return positions[value]


class CsDiceRenderer:
    def __init__(
        self, plugin_root: Path, cache_dir: Path, temp_dir: Path, config: RenderConfig
    ):
        self.plugin_root = plugin_root
        self.cache_dir = cache_dir
        self.temp_dir = temp_dir
        self.config = config
        self.preview_template_path = (
            self.plugin_root / "renderer" / "preview_template.html"
        )
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def render(self, request: DiceRequest) -> DiceRenderResult:
        self._validate_request(request)
        payload = request.to_payload()
        payload_hash = hashlib.sha256(
            json.dumps(
                {"pipeline_version": RENDER_PIPELINE_VERSION, "payload": payload},
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        gif_path = self.cache_dir / f"dice_{payload_hash}.gif"
        meta_path = self.cache_dir / f"dice_{payload_hash}.json"
        preview_path = self.cache_dir / f"dice_{payload_hash}.html"
        if gif_path.exists() and meta_path.exists():
            metadata = json.loads(meta_path.read_text(encoding="utf-8"))
            return DiceRenderResult(
                image_path=gif_path,
                values=metadata["values"],
                dice_labels=metadata["dice_labels"],
                preview_path=preview_path if preview_path.exists() else None,
                cached=True,
            )

        animation = self._build_animation(request)
        self._write_preview_html(preview_path, gif_path, request, animation)
        self._write_gif(gif_path, preview_path, request, animation)
        meta_path.write_text(
            json.dumps(
                {
                    "values": animation["values"],
                    "dice_labels": animation["dice_labels"],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        return DiceRenderResult(
            image_path=gif_path,
            values=animation["values"],
            dice_labels=animation["dice_labels"],
            preview_path=preview_path,
            cached=False,
        )

    def _validate_request(self, request: DiceRequest) -> None:
        unsupported = [spec.sides for spec in request.dice if spec.sides != 6]
        if unsupported:
            raise ValueError(
                "The cs.html 3D renderer currently supports d6 only. "
                f"Unsupported dice: {', '.join(f'd{sides}' for sides in unsupported)}"
            )

    def _build_animation(self, request: DiceRequest) -> dict:
        rng = random.Random(request.seed)
        dice_labels: list[str] = []
        values: list[int] = []
        dice_states: list[dict] = []
        stage_width = request.width
        stage_height = request.height
        spacing = min(150, stage_width * 0.24)
        total_dice = sum(spec.count for spec in request.dice)
        start_x = stage_width / 2 - ((total_dice - 1) * spacing) / 2

        die_index = 0
        for spec in request.dice:
            for count_index in range(spec.count):
                label = f"d6#{count_index + 1}"
                final_value = rng.randint(1, 6)
                final_yaw = rng.uniform(-math.pi, math.pi)
                target_rx, target_ry, target_rz = _target_orientation(
                    final_value, final_yaw
                )
                dice_labels.append(label)
                values.append(final_value)
                dice_states.append(
                    {
                        "label": label,
                        "final_value": final_value,
                        "spawn_x": start_x
                        + die_index * spacing
                        + rng.uniform(-120, 120),
                        "spawn_y": stage_height * 0.16 + rng.uniform(-36, 18),
                        "spawn_z": rng.uniform(-180, -40),
                        "land_x": start_x + die_index * spacing,
                        "land_y": stage_height * 0.64 + rng.uniform(-12, 12),
                        "land_z": rng.uniform(30, 90),
                        "lift": rng.uniform(150, 240),
                        "wobble": rng.uniform(5.0, 11.0),
                        "size": rng.uniform(stage_width * 0.12, stage_width * 0.145),
                        "start_rx": rng.uniform(-5.2, 5.2),
                        "start_ry": rng.uniform(-6.4, 6.4),
                        "start_rz": rng.uniform(-5.4, 5.4),
                        "mid_rx": rng.uniform(-11.0, 11.0),
                        "mid_ry": rng.uniform(-12.5, 12.5),
                        "mid_rz": rng.uniform(-11.0, 11.0),
                        "target_rx": target_rx,
                        "target_ry": target_ry,
                        "target_rz": target_rz,
                    }
                )
                die_index += 1

        frames: list[dict] = []
        for frame_index in range(request.frames):
            progress = frame_index / max(1, request.frames - 1)
            frame_dice: list[dict] = []
            particles: list[dict] = []
            for die_state in dice_states:
                settle_start = 0.78
                if progress < settle_start:
                    move = progress / settle_start
                    arc = math.sin(move * math.pi) * die_state["lift"]
                    x = (
                        die_state["spawn_x"]
                        + (die_state["land_x"] - die_state["spawn_x"]) * move
                    )
                    x += math.sin(move * math.pi * 2.0) * 26
                    y = (
                        die_state["spawn_y"]
                        + (die_state["land_y"] - die_state["spawn_y"]) * move
                        - arc
                    )
                    z = (
                        die_state["spawn_z"]
                        + (die_state["land_z"] - die_state["spawn_z"]) * move
                    )
                    z += math.sin(move * math.pi * 1.7) * 46
                    rx = die_state["start_rx"] + move * die_state["mid_rx"]
                    ry = die_state["start_ry"] + move * die_state["mid_ry"]
                    rz = die_state["start_rz"] + move * die_state["mid_rz"]
                    energy = 1.0 - move * 0.28
                else:
                    settle = _ease_out_cubic(
                        (progress - settle_start) / max(0.001, 1 - settle_start)
                    )
                    wobble = 1.0 - settle
                    x = (
                        die_state["land_x"]
                        + math.sin(progress * math.pi * 8)
                        * die_state["wobble"]
                        * wobble
                    )
                    y = (
                        die_state["land_y"]
                        + math.cos(progress * math.pi * 10)
                        * die_state["wobble"]
                        * 0.24
                        * wobble
                    )
                    z = (
                        die_state["land_z"]
                        + math.sin(progress * math.pi * 6) * 14 * wobble
                    )
                    rx = _lerp(
                        die_state["start_rx"] + die_state["mid_rx"],
                        die_state["target_rx"],
                        settle,
                    )
                    ry = _lerp(
                        die_state["start_ry"] + die_state["mid_ry"],
                        die_state["target_ry"],
                        settle,
                    )
                    rz = _lerp(
                        die_state["start_rz"] + die_state["mid_rz"],
                        die_state["target_rz"],
                        settle,
                    )
                    energy = 0.38 * wobble

                frame_dice.append(
                    {
                        "label": die_state["label"],
                        "x": x,
                        "y": y,
                        "z": z,
                        "size": die_state["size"],
                        "rx": rx,
                        "ry": ry,
                        "rz": rz,
                        "energy": _clamp(energy, 0.0, 1.0),
                        "face_value": die_state["final_value"],
                    }
                )

                for spark_index in range(5):
                    angle = progress * math.pi * 9 + spark_index * (math.pi * 0.4)
                    radius = die_state["size"] * (0.56 + spark_index * 0.08)
                    particles.append(
                        {
                            "x": x + math.cos(angle) * radius * (0.22 + energy * 0.18),
                            "y": y + math.sin(angle) * radius * 0.16 - energy * 6,
                            "z": z - 40 + spark_index * 16,
                            "radius": 2.2 + energy * 2.6,
                            "alpha": _clamp(0.06 + energy * 0.16, 0.0, 0.26),
                        }
                    )

            frames.append({"dice": frame_dice, "particles": particles})

        return {
            "theme": {
                "background_top": "#1a2520",
                "background_bottom": "#0a0f0d",
                "floor_color": "#1a2520",
                "accent": "#c9a227",
                "muted": "#6b7c72",
            },
            "frames": frames,
            "values": values,
            "dice_labels": dice_labels,
        }

    def _write_gif(
        self, gif_path: Path, preview_path: Path, request: DiceRequest, animation: dict
    ) -> None:
        if self._try_capture_gif_via_playwright(gif_path, preview_path, request):
            return
        self._write_gif_with_pillow(gif_path, request, animation)

    def _write_gif_with_pillow(
        self, gif_path: Path, request: DiceRequest, animation: dict
    ) -> None:
        frames: list[Image.Image] = []
        for frame in animation["frames"]:
            frames.append(self._draw_frame(request, animation["theme"], frame))

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

    def _try_capture_gif_via_playwright(
        self, gif_path: Path, preview_path: Path, request: DiceRequest
    ) -> bool:
        playwright = shutil.which(self.config.playwright_path) or shutil.which(
            "playwright"
        )
        if not playwright:
            return False

        frame_images: list[Image.Image] = []
        duration = max(20, int(1000 / max(1, request.fps)))
        encoded_preview = quote(preview_path.resolve().as_posix(), safe="/:")
        base_url = f"file:///{encoded_preview}"
        try:
            for frame_index in range(request.frames):
                screenshot_path = (
                    self.temp_dir / f"capture_{gif_path.stem}_{frame_index:04d}.png"
                )
                capture_url = f"{base_url}?capture=1&frame={frame_index}"
                subprocess.run(
                    [
                        playwright,
                        "screenshot",
                        "--browser",
                        "chromium",
                        "--viewport-size",
                        f"{request.width},{request.height}",
                        "--wait-for-selector",
                        "body[data-ready='1']",
                        capture_url,
                        str(screenshot_path),
                    ],
                    cwd=str(self.plugin_root),
                    check=True,
                    capture_output=True,
                    timeout=max(10, self.config.timeout_ms // 1000),
                )
                if not screenshot_path.exists() or screenshot_path.stat().st_size == 0:
                    raise RuntimeError(
                        f"Playwright did not produce a screenshot for frame {frame_index}."
                    )
                with Image.open(screenshot_path) as image:
                    frame_images.append(image.convert("RGBA"))
        except Exception:
            for image in frame_images:
                image.close()
            return False

        frame_images[0].save(
            gif_path,
            save_all=True,
            append_images=frame_images[1:],
            duration=duration,
            loop=0,
            disposal=2,
            optimize=False,
        )
        for image in frame_images:
            image.close()
        return True

    def _draw_frame(
        self, request: DiceRequest, theme: dict, frame: dict
    ) -> Image.Image:
        image = Image.new(
            "RGBA", (request.width, request.height), _rgba(theme["background_bottom"])
        )
        draw = ImageDraw.Draw(image, "RGBA")
        self._draw_stage_background(draw, request.width, request.height, theme)

        for particle in sorted(frame["particles"], key=lambda item: item["z"]):
            self._draw_particle(draw, particle)

        for die in sorted(frame["dice"], key=lambda item: (item["z"], item["y"])):
            self._draw_die(draw, die)
        return image

    def _draw_stage_background(
        self, draw: ImageDraw.ImageDraw, width: int, height: int, theme: dict
    ) -> None:
        top = ImageColor.getrgb(theme["background_top"])
        bottom = ImageColor.getrgb(theme["background_bottom"])
        for row in range(height):
            ratio = row / max(1, height - 1)
            color = tuple(
                int(top[index] + (bottom[index] - top[index]) * ratio)
                for index in range(3)
            )
            draw.line([(0, row), (width, row)], fill=color)

        glow_center = (width / 2, height * 0.2)
        for radius in range(int(width * 0.34), 10, -14):
            alpha = int(10 * radius / max(1, width * 0.34))
            draw.ellipse(
                [
                    (glow_center[0] - radius, glow_center[1] - radius * 0.65),
                    (glow_center[0] + radius, glow_center[1] + radius * 0.65),
                ],
                fill=_rgba(theme["accent"], alpha),
            )

        floor_y = int(height * 0.74)
        draw.rectangle(
            [(0, floor_y), (width, height)],
            fill=ImageColor.getrgb(theme["floor_color"]),
        )
        accent = _rgba(theme["accent"], 18)
        spacing = 28
        for start in range(-height, width + height, spacing):
            draw.line(
                [(start, floor_y), (start + height // 2, height)], fill=accent, width=1
            )
        for start in range(0, width + height, spacing):
            draw.line(
                [(start, floor_y), (start - height // 2, height)], fill=accent, width=1
            )

    def _draw_particle(self, draw: ImageDraw.ImageDraw, particle: dict) -> None:
        px, py, pz = _project_point((particle["x"], particle["y"], particle["z"]))
        radius = particle["radius"] * CAMERA_DISTANCE / max(120.0, CAMERA_DISTANCE - pz)
        alpha = int(255 * particle["alpha"])
        draw.ellipse(
            [(px - radius, py - radius), (px + radius, py + radius)],
            fill=_rgba("#d4af37", alpha),
        )

    def _visible_faces(self, die: dict) -> list[dict]:
        center = (die["x"], die["y"], die["z"])
        half = die["size"] / 2
        light = _normalize((-0.4, -0.8, 1.0))
        faces: list[dict] = []
        for face_key in FACE_ORDER:
            normal = _rotate_xyz(
                FACE_NORMALS[face_key], die["rx"], die["ry"], die["rz"]
            )
            if normal[2] <= -0.08:
                continue

            corners_3d: list[tuple[float, float, float]] = []
            projected: list[tuple[float, float]] = []
            for corner in FACE_CORNERS[face_key]:
                local = (corner[0] * half, corner[1] * half, corner[2] * half)
                world = _add(
                    _rotate_xyz(local, die["rx"], die["ry"], die["rz"]), center
                )
                corners_3d.append(world)
                px, py, _ = _project_point(world)
                projected.append((px, py))

            brightness = 0.72 + max(0.0, _dot(_normalize(normal), light)) * 0.38
            depth = sum(point[2] for point in corners_3d) / len(corners_3d)
            faces.append(
                {
                    "face_key": face_key,
                    "value": FACE_MAPPING[face_key],
                    "polygon": projected,
                    "corners": corners_3d,
                    "normal": normal,
                    "brightness": brightness,
                    "depth": depth,
                }
            )
        faces.sort(key=lambda item: item["depth"])
        return faces

    def _draw_die(self, draw: ImageDraw.ImageDraw, die: dict) -> None:
        shadow_w = die["size"] * (1.1 + die["energy"] * 0.45)
        shadow_h = die["size"] * (0.28 + die["energy"] * 0.08)
        sx, sy, sz = _project_point(
            (die["x"], die["y"] + die["size"] * 0.62, die["z"] - 60)
        )
        shadow_scale = CAMERA_DISTANCE / max(120.0, CAMERA_DISTANCE - sz)
        draw.ellipse(
            [
                (sx - shadow_w * shadow_scale, sy - shadow_h * shadow_scale),
                (sx + shadow_w * shadow_scale, sy + shadow_h * shadow_scale),
            ],
            fill=_rgba("#000000", int(68 + die["energy"] * 34)),
        )

        faces = self._visible_faces(die)
        for face in faces:
            fill = self._shade_face("#f4efe5", face["brightness"])
            outline = self._shade_face("#7b6844", face["brightness"] * 0.75)
            draw.polygon(face["polygon"], fill=fill, outline=outline)
            self._draw_face_gloss(draw, face)
            self._draw_face_pips(draw, face)

    def _shade_face(self, color: str, brightness: float) -> tuple[int, int, int, int]:
        base = ImageColor.getrgb(color)
        factor = _clamp(brightness, 0.55, 1.18)
        return (
            int(_clamp(base[0] * factor, 0, 255)),
            int(_clamp(base[1] * factor, 0, 255)),
            int(_clamp(base[2] * factor, 0, 255)),
            255,
        )

    def _draw_face_gloss(self, draw: ImageDraw.ImageDraw, face: dict) -> None:
        points = face["polygon"]
        if len(points) < 4:
            return
        top = points[1]
        right = points[2]
        left = points[0]
        gloss_poly = [
            (_lerp(left[0], top[0], 0.18), _lerp(left[1], top[1], 0.18)),
            (_lerp(left[0], right[0], 0.55), _lerp(left[1], right[1], 0.28)),
            (_lerp(top[0], right[0], 0.32), _lerp(top[1], right[1], 0.32)),
            (_lerp(left[0], top[0], 0.52), _lerp(left[1], top[1], 0.52)),
        ]
        draw.polygon(gloss_poly, fill=_rgba("#ffffff", 28))

    def _draw_face_pips(self, draw: ImageDraw.ImageDraw, face: dict) -> None:
        a, b, c, d = face["corners"]
        u_axis = _sub(b, a)
        v_axis = _sub(d, a)
        for u, v in _pip_uv(face["value"]):
            center = _add(_add(a, _scale(u_axis, u)), _scale(v_axis, v))
            center = _add(center, _scale(_normalize(face["normal"]), 3.0))
            px, py, pz = _project_point(center)
            local_size = CAMERA_DISTANCE / max(120.0, CAMERA_DISTANCE - pz)
            radius = 5.0 * local_size
            draw.ellipse(
                [
                    (px - radius + 1.3, py - radius + 1.3),
                    (px + radius + 1.3, py + radius + 1.3),
                ],
                fill=_rgba("#000000", 56),
            )
            draw.ellipse(
                [(px - radius, py - radius), (px + radius, py + radius)],
                fill=_rgba("#8b1a1a"),
            )
            inner = radius * 0.62
            draw.ellipse(
                [(px - inner, py - inner), (px + inner, py + inner)],
                fill=_rgba("#a52222"),
            )

    def _write_preview_html(
        self, preview_path: Path, gif_path: Path, request: DiceRequest, animation: dict
    ) -> None:
        template = self.preview_template_path.read_text(encoding="utf-8")
        values = animation["values"]
        dice_labels = animation["dice_labels"]
        summary = ", ".join(
            f"{label}={value}"
            for label, value in zip(dice_labels, values, strict=False)
        )
        dice_details = " / ".join(
            f"{label} -> {value}"
            for label, value in zip(dice_labels, values, strict=False)
        )
        command = " ".join(
            [
                "+".join(
                    f"{spec.count}d{spec.sides}"
                    if spec.count != 1
                    else f"d{spec.sides}"
                    for spec in request.dice
                ),
                f"theme={request.theme}",
                f"seed={request.seed}",
            ]
        )
        replacements = {
            "{{GIF_PATH}}": gif_path.name,
            "{{PRIMARY_RESULT}}": str(values[0]) if values else "-",
            "{{SUMMARY}}": summary or "No result",
            "{{THEME}}": request.theme,
            "{{SEED}}": str(request.seed),
            "{{WIDTH}}": str(request.width),
            "{{HEIGHT}}": str(request.height),
            "{{FRAMES}}": str(request.frames),
            "{{FPS}}": str(request.fps),
            "{{DICE_COUNT}}": str(request.dice_count),
            "{{DICE_DETAILS}}": dice_details or "No dice",
            "{{COMMAND}}": command,
            "{{PREVIEW_DATA_JSON}}": json.dumps(
                {
                    "theme": animation["theme"],
                    "frames": animation["frames"],
                    "values": values,
                    "dice_labels": dice_labels,
                    "summary": summary or "No result",
                    "fps": request.fps,
                },
                ensure_ascii=False,
            ),
        }
        html = template
        for placeholder, value in replacements.items():
            html = html.replace(placeholder, value)
        preview_path.write_text(html, encoding="utf-8")
