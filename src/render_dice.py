import json
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional


RUNTIME_DIR = Path(__file__).resolve().parent
NODE_SCRIPT = RUNTIME_DIR / "render_dice_gif.mjs"


def render_dice_gif(
    dice_type: str = "D6",
    count: int = 1,
    duration: int = 2400,
    fps: int = 16,
    output_name: Optional[str] = None,
    browser: Optional[str] = None,
) -> Dict[str, Any]:
    cmd = [
        "node",
        str(NODE_SCRIPT),
        f"--diceType={dice_type}",
        f"--count={count}",
        f"--duration={duration}",
        f"--fps={fps}",
    ]

    if output_name:
        cmd.append(f"--outputName={output_name}")
    if browser:
        cmd.append(f"--browser={browser}")

    completed = subprocess.run(
        cmd,
        cwd=RUNTIME_DIR,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    stdout = completed.stdout.strip().splitlines()
    if not stdout:
        raise RuntimeError("Renderer returned no output")

    return json.loads(stdout[-1])


if __name__ == "__main__":
    result = render_dice_gif()
    print(json.dumps(result, ensure_ascii=False))
