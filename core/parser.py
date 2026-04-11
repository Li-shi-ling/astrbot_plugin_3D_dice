from __future__ import annotations

import re
from dataclasses import dataclass

from .models import DEFAULT_THEME, DiceSpec, SUPPORTED_SIDES


_TERM_RE = re.compile(r"(?i)^(?:(\d+)?d)(\d+)$")


@dataclass(slots=True)
class ParsedCommand:
    notation: str
    options: dict[str, str]


def parse_command_text(text: str) -> ParsedCommand:
    cleaned = text.strip()
    if cleaned.startswith("/dice"):
        cleaned = cleaned[5:].strip()
    elif cleaned.startswith("dice "):
        cleaned = cleaned[5:].strip()
    if not cleaned:
        raise ValueError(
            "Usage: /dice <notation> [theme=<name>] [seed=<int>] [transparent=true|false]",
        )

    notation_parts: list[str] = []
    options: dict[str, str] = {}
    for token in cleaned.split():
        if "=" in token:
            key, value = token.split("=", 1)
            if not key or not value:
                raise ValueError(f"Invalid option: {token}")
            options[key.strip().lower()] = value.strip()
        else:
            notation_parts.append(token)

    if not notation_parts:
        raise ValueError("Dice notation is required. Example: /dice 2d6")

    return ParsedCommand(notation="".join(notation_parts), options=options)


def parse_dice_notation(notation: str, max_dice_count: int) -> list[DiceSpec]:
    terms = [term for term in re.split(r"[\s,+]+", notation.strip()) if term]
    if not terms:
        raise ValueError("Dice notation is empty.")

    specs: list[DiceSpec] = []
    total_count = 0
    for term in terms:
        match = _TERM_RE.match(term)
        if not match:
            raise ValueError(f"Unsupported dice term: {term}")
        count = int(match.group(1) or "1")
        sides = int(match.group(2))
        if count <= 0:
            raise ValueError("Dice count must be greater than zero.")
        if sides not in SUPPORTED_SIDES:
            supported = ", ".join(f"d{value}" for value in SUPPORTED_SIDES)
            raise ValueError(f"Unsupported dice shape d{sides}. Supported: {supported}")
        total_count += count
        if total_count > max_dice_count:
            raise ValueError(
                f"Dice count exceeds the configured limit of {max_dice_count}."
            )
        specs.append(DiceSpec(count=count, sides=sides))
    return specs


def parse_bool_option(value: str, default: bool = False) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    return default


def normalize_theme(value: str | None) -> str:
    if not value:
        return DEFAULT_THEME
    return value.strip().lower()
