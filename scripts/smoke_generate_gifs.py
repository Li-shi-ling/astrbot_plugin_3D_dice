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
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=480)
    parser.add_argument("--fps", type=int, default=12)
    parser.add_argument("--duration-ms", type=int, default=5000)
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
        metadata = result.metadata
        print(
            f"{dice_type}: result={result.results} total={result.total} "
            f"settled={metadata.get('settled')} "
            f"contact_vertices={metadata.get('final_contact_vertices')} "
            f"settle_ms={metadata.get('settle_time_ms')} "
            f"frames={metadata.get('frames')} "
            f"actual_ms={metadata.get('actual_duration_ms')} "
            f"travel={metadata.get('horizontal_travel'):.2f} "
            f"max_h={metadata.get('max_height'):.2f} "
            f"final_v={max(metadata.get('final_linear_speeds') or [0]):.3f} "
            f"final_w={max(metadata.get('final_angular_speeds') or [0]):.3f} "
            f"path={result.gif_path}"
        )


if __name__ == "__main__":
    main()
