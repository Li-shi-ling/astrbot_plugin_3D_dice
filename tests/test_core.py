from __future__ import annotations

import pytest

from core import (
    format_request_error,
    normalize_config,
    parse_roll_request,
    usage_text,
)


def test_parse_supported_dice_and_seed() -> None:
    request = parse_roll_request("/roll3d 2d10 seed=123", {"max_count": 3})
    assert request.dice_type == "D10"
    assert request.count == 2
    assert request.seed == 123


def test_parse_defaults_from_config() -> None:
    request = parse_roll_request("/roll3d", {"default_dice_type": "D20", "default_count": 1})
    assert request.dice_type == "D20"
    assert request.count == 1


def test_unsupported_dice_is_friendly() -> None:
    with pytest.raises(ValueError) as excinfo:
        parse_roll_request("/roll3d d12")
    message = format_request_error(excinfo.value, 3)
    assert "D4/D6/D8/D10/D20" in message
    assert "Usage:" in message


def test_count_bounds() -> None:
    with pytest.raises(ValueError):
        parse_roll_request("/roll3d 7d6", {"max_count": 6})


def test_normalize_config_clamps_values() -> None:
    config = normalize_config(
        {
            "default_dice_type": "d10",
            "max_count": 99,
            "width": 10,
            "height": 9999,
            "fps": 99,
            "duration_ms": 99,
        }
    )
    assert config["default_dice_type"] == "D10"
    assert config["max_count"] == 6
    assert config["width"] == 240
    assert config["height"] == 1024
    assert config["fps"] == 30
    assert config["duration_ms"] == 800


def test_invalid_config_seed_falls_back_to_random_seed() -> None:
    config = normalize_config({"seed": "not-a-number"})
    assert config["seed"] is None


def test_usage_mentions_all_supported_dice() -> None:
    text = usage_text(3)
    for dice_type in ("D4", "D6", "D8", "D10", "D20"):
        assert dice_type in text
