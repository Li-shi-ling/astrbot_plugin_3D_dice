from __future__ import annotations

import importlib.util

import pytest
from PIL import Image

from dice_sim import SUPPORTED_DICE_TYPES, roll_gif


@pytest.mark.skipif(importlib.util.find_spec("pybullet") is None, reason="pybullet is not installed")
@pytest.mark.parametrize("dice_type", SUPPORTED_DICE_TYPES)
def test_roll_gif_writes_animated_file_for_supported_dice(tmp_path, dice_type: str) -> None:
    result = roll_gif(
        dice_type,
        output_dir=tmp_path,
        seed=123,
        width=240,
        height=240,
        fps=4,
        duration_ms=900,
    )
    assert result.gif_path.exists()
    assert result.results
    assert 1 <= result.results[0] <= int(dice_type.removeprefix("D"))
    with Image.open(result.gif_path) as image:
        assert getattr(image, "n_frames", 1) > 1
