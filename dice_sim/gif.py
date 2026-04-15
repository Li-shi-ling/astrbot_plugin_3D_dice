from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageSequence

from .errors import GifEncodeError, MissingDependencyError


def encode_gif(frames: list[Image.Image], output_path: Path, fps: int) -> Path:
    if len(frames) < 2:
        raise GifEncodeError("Animated GIF requires at least two frames.")
    try:
        import imageio.v2 as imageio  # type: ignore
    except Exception as exc:
        raise MissingDependencyError(
            "imageio is required for GIF encoding. Install requirements.txt."
        ) from exc

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        frame_duration_ms = max(
            20, int(math.ceil((1000 / max(1, fps)) / 10.0) * 10)
        )
        with imageio.get_writer(
            output_path,
            mode="I",
            duration=frame_duration_ms,
            loop=0,
        ) as writer:
            for frame in frames:
                writer.append_data(np.asarray(frame.convert("RGB")))
        if not output_path.exists() or output_path.stat().st_size <= 0:
            raise GifEncodeError("GIF encoder did not create a non-empty file.")
        with Image.open(output_path) as image:
            frame_count = getattr(image, "n_frames", 1)
            if frame_count < 2:
                raise GifEncodeError("Encoded GIF is not animated.")
            encoded_duration_ms = sum(
                frame.info.get("duration", 0) for frame in ImageSequence.Iterator(image)
            )
            if encoded_duration_ms <= 0:
                raise GifEncodeError("Encoded GIF has no frame delay metadata.")
        return output_path
    except GifEncodeError:
        raise
    except Exception as exc:
        raise GifEncodeError(f"Failed to encode GIF: {exc}") from exc
