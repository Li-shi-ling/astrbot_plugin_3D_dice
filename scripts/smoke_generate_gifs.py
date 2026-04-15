from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dice_sim import SUPPORTED_DICE_TYPES, roll_gif


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate sample physical dice GIFs.")
    parser.add_argument("--output-dir", default="outputs/smoke", help="Directory for generated GIFs.")
    parser.add_argument("--seed", type=int, default=1000, help="Base deterministic seed.")
    parser.add_argument("--width", type=int, default=360)
    parser.add_argument("--height", type=int, default=300)
    parser.add_argument("--fps", type=int, default=10)
    parser.add_argument("--duration-ms", type=int, default=1600)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    for offset, dice_type in enumerate(SUPPORTED_DICE_TYPES):
        result = roll_gif(
            dice_type,
            output_dir=output_dir,
            seed=args.seed + offset,
            width=args.width,
            height=args.height,
            fps=args.fps,
            duration_ms=args.duration_ms,
        )
        print(f"{dice_type}: {result.results} total={result.total} path={result.gif_path}")


if __name__ == "__main__":
    main()
