from __future__ import annotations

import os
import sys
import traceback
from pathlib import Path


def main() -> int:
    plugin_dir = Path(os.environ["DICE_PLUGIN_DIR"]).resolve()
    output_dir = Path(os.environ["DICE_OUTPUT_DIR"]).resolve()
    sys.path.insert(0, str(plugin_dir))

    from dice_sim import StyleOptions, roll_gif

    output_dir.mkdir(parents=True, exist_ok=True)
    jobs = [
        {
            "name": "classic_white_d6",
            "dice_type": "D6",
            "count": 1,
            "seed": 350234,
            "fps": 100,
            "style": StyleOptions(
                die_color="#ffffff",
                ink_color="#000000",
                edge_color="#000000",
                background_color="#f5f7fb",
            ),
        },
        {
            "name": "six_white_d6_collision",
            "dice_type": "D6",
            "count": 6,
            "seed": 350234,
            "fps": 100,
            "style": StyleOptions(
                die_color="#ffffff",
                ink_color="#000000",
                edge_color="#000000",
                background_color="#f5f7fb",
            ),
        },
        {
            "name": "ice_blue_d20",
            "dice_type": "D20",
            "count": 1,
            "seed": 350234,
            "style": StyleOptions(
                die_color="#dff3ff",
                ink_color="#07131f",
                edge_color="#07131f",
                background_color="#eef6f8",
            ),
        },
        {
            "name": "mint_green_3d8",
            "dice_type": "D8",
            "count": 3,
            "seed": 350234,
            "style": StyleOptions(
                die_color="#d7f7df",
                ink_color="#102017",
                edge_color="#102017",
                background_color="#f1f7f2",
            ),
        },
        {
            "name": "rose_2d10",
            "dice_type": "D10",
            "count": 2,
            "seed": 350234,
            "style": StyleOptions(
                die_color="#ffdce5",
                ink_color="#230811",
                edge_color="#230811",
                background_color="#f8f1f3",
            ),
        },
        {
            "name": "charcoal_gold_d4",
            "dice_type": "D4",
            "count": 1,
            "seed": 350234,
            "style": StyleOptions(
                die_color="#2b2f33",
                ink_color="#ffd45a",
                edge_color="#ffd45a",
                background_color="#f3f5f7",
                label_color="#000000",
            ),
        },
    ]

    for job in jobs:
        output_path = output_dir / f"{job['name']}.gif"
        print(f"Generating {job['name']}: {job['count']}x{job['dice_type']}")
        try:
            result = roll_gif(
                job["dice_type"],
                count=job["count"],
                output_path=output_path,
                seed=job["seed"],
                width=840,
                height=600,
                fps=job.get("fps", 100),
                duration_ms=5000,
                final_hold_ms=3000,
                style=job["style"],
                max_cache_files=500,
            )
        except Exception:
            traceback.print_exc()
            return 1

        detail = "+".join(str(value) for value in result.results)
        print(
            f"  -> {result.gif_path} | result={detail} total={result.total} "
            f"settle_ms={result.metadata.get('settle_time_ms')} "
            f"frames={result.metadata.get('frames')}"
        )

    print()
    print(f"Done. GIF files are in: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
