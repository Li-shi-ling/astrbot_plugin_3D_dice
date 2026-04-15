from __future__ import annotations

import time
from pathlib import Path


def build_output_path(
    output_dir: Path | str | None,
    dice_type: str,
    seed: int,
    output_path: Path | str | None = None,
) -> Path:
    if output_path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
    directory = Path(output_dir or "outputs")
    directory.mkdir(parents=True, exist_ok=True)
    stamp = int(time.time() * 1000)
    return directory / f"{dice_type.lower()}_{seed}_{stamp}.gif"


def cleanup_cache(
    output_dir: Path | str | None,
    max_files: int = 80,
    max_age_seconds: int = 604800,
) -> None:
    if not output_dir:
        return
    directory = Path(output_dir)
    if not directory.exists():
        return
    now = time.time()
    files = sorted(
        (path for path in directory.glob("*.gif") if path.is_file()),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if max_age_seconds > 0:
        for path in files:
            try:
                if now - path.stat().st_mtime > max_age_seconds:
                    path.unlink(missing_ok=True)
            except OSError:
                pass
    if max_files > 0:
        refreshed = sorted(
            (path for path in directory.glob("*.gif") if path.is_file()),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        for path in refreshed[max_files:]:
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass
