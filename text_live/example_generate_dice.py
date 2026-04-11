import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def main():
    repo_root = REPO_ROOT
    plugin_root = Path(__file__).resolve().parents[1]
    command = "2d6 theme=ember seed=42"

    from data.plugins.astrbot_plugin_3D_dice.core.models import RenderConfig
    from data.plugins.astrbot_plugin_3D_dice.core.service import DiceService

    os.environ["ASTRBOT_ROOT"] = str(repo_root)
    os.chdir(repo_root)

    service = DiceService(
        plugin_root=plugin_root,
        config=RenderConfig(
            playwright_path="playwright",
            width=480,
            height=480,
            fps=20,
            frames=36,
            theme="classic",
            max_dice_count=8,
            timeout_ms=30000,
            debug=False,
        ),
    )

    result = service.render_from_text(command)
    print(f"ASTRBOT_ROOT: {repo_root}")
    print(f"Command: {command}")
    print(f"Summary: {result.summary}")
    print(f"Values: {result.values}")
    print(f"Labels: {result.dice_labels}")
    print(f"Cached: {result.cached}")
    print(f"GIF saved at: {result.image_path}")
    if result.preview_path:
        print(f"HTML preview saved at: {result.preview_path}")


if __name__ == "__main__":
    main()
