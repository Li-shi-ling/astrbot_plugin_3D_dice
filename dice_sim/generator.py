from __future__ import annotations

import random
from pathlib import Path

from .cache import build_output_path, cleanup_cache
from .errors import SimulationError, UnsupportedDiceError
from .geometry import SUPPORTED_DICE_TYPES, create_mesh
from .gif import encode_gif
from .physics import simulate_roll
from .render import render_frames
from .result import detect_result
from .types import RollGifResult, RollOptions, StyleOptions


def roll_gif(
    dice_type: str,
    *,
    count: int = 1,
    output_dir: Path | str | None = None,
    output_path: Path | str | None = None,
    seed: int | None = None,
    width: int = 640,
    height: int = 480,
    fps: int = 12,
    duration_ms: int = 5000,
    final_hold_ms: int = 3000,
    style: StyleOptions | None = None,
    max_cache_files: int = 80,
    cache_max_age_seconds: int = 604800,
) -> RollGifResult:
    options = RollOptions(
        dice_type=dice_type,
        count=count,
        output_dir=output_dir,
        output_path=output_path,
        seed=seed,
        width=width,
        height=height,
        fps=fps,
        duration_ms=duration_ms,
        final_hold_ms=final_hold_ms,
        style=style or StyleOptions(),
        max_cache_files=max_cache_files,
        cache_max_age_seconds=cache_max_age_seconds,
    )
    return roll_gif_with_options(options)


def roll_gif_with_options(options: RollOptions) -> RollGifResult:
    dice_type = str(options.dice_type or "").strip().upper()
    if dice_type not in SUPPORTED_DICE_TYPES:
        supported = ", ".join(SUPPORTED_DICE_TYPES)
        raise UnsupportedDiceError(f"Unsupported dice type {dice_type!r}. Supported: {supported}.")
    count = _clamp_int(options.count, 1, 6)
    width = _clamp_int(options.width, 240, 1024)
    height = _clamp_int(options.height, 240, 1024)
    fps = _clamp_int(options.fps, 4, 30)
    duration_ms = _clamp_int(options.duration_ms, 1500, 10000)
    final_hold_ms = _clamp_int(options.final_hold_ms, 3000, 5000)
    seed = int(options.seed if options.seed is not None else random.SystemRandom().randrange(1, 2**31))

    mesh = create_mesh(dice_type)
    simulation = simulate_roll(mesh, count, seed, duration_ms, fps, final_hold_ms)
    if not simulation.settled:
        raise SimulationError(
            f"{dice_type} did not settle within {duration_ms} ms; "
            "increase duration_ms or lower throw intensity."
        )
    values = tuple(detect_result(mesh, pose) for pose in simulation.final_poses)
    frames = render_frames(
        mesh,
        simulation.frames,
        width,
        height,
        options.style,
        values,
        simulation.result_label_start_seconds,
    )
    output_path = build_output_path(options.output_dir, dice_type, seed, options.output_path)
    encoded_path = encode_gif(frames, output_path, fps)
    cleanup_cache(options.output_dir, options.max_cache_files, options.cache_max_age_seconds)
    actual_duration_ms = int(round(simulation.frames[-1].time_seconds * 1000))
    result_label_start_ms = (
        None
        if simulation.result_label_start_seconds is None
        else int(round(simulation.result_label_start_seconds * 1000))
    )
    return RollGifResult(
        gif_path=encoded_path,
        dice_type=dice_type,
        dice_count=count,
        results=values,
        total=sum(values),
        seed=seed,
        width=width,
        height=height,
        fps=fps,
        duration_ms=duration_ms,
        final_hold_ms=final_hold_ms,
        metadata={
            "frames": len(frames),
            "actual_duration_ms": actual_duration_ms,
            "final_hold_ms": final_hold_ms,
            "settled": simulation.settled,
            "settle_time_ms": (
                None
                if simulation.settle_time_seconds is None
                else int(round(simulation.settle_time_seconds * 1000))
            ),
            "result_label_start_ms": result_label_start_ms,
            "result_visible_ms": (
                None
                if result_label_start_ms is None
                else actual_duration_ms - result_label_start_ms
            ),
            "final_linear_speeds": list(simulation.final_linear_speeds),
            "final_angular_speeds": list(simulation.final_angular_speeds),
            "final_contact_vertices": list(simulation.final_contact_vertices),
            "horizontal_travel": simulation.horizontal_travel,
            "max_height": simulation.max_height,
            "inter_body_contact_count": simulation.inter_body_contact_count,
            "inter_body_contact_steps": simulation.inter_body_contact_steps,
            "result_rule": mesh.result_rule,
            "renderer": "pillow-software",
            "physics": "pybullet-direct",
            "capture_mode": "until_settled",
        },
    )


def _clamp_int(value: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = minimum
    return max(minimum, min(parsed, maximum))
