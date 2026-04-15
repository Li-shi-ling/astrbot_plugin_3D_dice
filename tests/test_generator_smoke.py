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
        duration_ms=5000,
    )
    assert result.gif_path.exists()
    assert result.results
    assert 1 <= result.results[0] <= int(dice_type.removeprefix("D"))
    assert result.metadata["capture_mode"] == "until_settled"
    assert result.metadata["settled"] is True
    assert result.metadata["actual_duration_ms"] > 0
    assert result.metadata["settle_time_ms"] is not None
    assert result.metadata["final_hold_ms"] == 3000
    assert (
        result.metadata["actual_duration_ms"]
        >= result.metadata["settle_time_ms"] + result.metadata["final_hold_ms"]
    )
    assert max(result.metadata["final_linear_speeds"]) < 0.18
    assert max(result.metadata["final_angular_speeds"]) < 0.35
    assert min(result.metadata["final_contact_vertices"]) >= 3
    assert result.metadata["horizontal_travel"] > 4.0
    assert result.metadata["max_height"] > 2.8
    with Image.open(result.gif_path) as image:
        assert getattr(image, "n_frames", 1) > 1


@pytest.mark.skipif(
    importlib.util.find_spec("pybullet") is None, reason="pybullet is not installed"
)
@pytest.mark.parametrize("dice_type", SUPPORTED_DICE_TYPES)
def test_roll_gif_six_dice_share_physics_world(tmp_path, dice_type: str) -> None:
    result = roll_gif(
        dice_type,
        count=6,
        output_dir=tmp_path,
        seed=123,
        width=240,
        height=240,
        fps=4,
        duration_ms=5000,
    )
    assert len(result.results) == 6
    assert result.metadata["settled"] is True
    assert result.metadata["inter_body_contact_count"] > 0
    assert result.metadata["inter_body_contact_steps"] > 0
    expected_contact_vertices = 4 if dice_type == "D6" else 3
    assert result.metadata["final_contact_vertices"] == [expected_contact_vertices] * 6
