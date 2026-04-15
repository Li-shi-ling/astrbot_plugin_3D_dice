from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

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
        with imageio.get_writer(output_path, mode="I", duration=1 / max(1, fps), loop=0) as writer:
            for frame in frames:
                writer.append_data(np.asarray(frame.convert("RGB")))
        if not output_path.exists() or output_path.stat().st_size <= 0:
            raise GifEncodeError("GIF encoder did not create a non-empty file.")
        with Image.open(output_path) as image:
            frame_count = getattr(image, "n_frames", 1)
            if frame_count < 2:
                raise GifEncodeError("Encoded GIF is not animated.")
        return output_path
    except GifEncodeError:
        raise
    except Exception as exc:
        raise GifEncodeError(f"Failed to encode GIF: {exc}") from exc
