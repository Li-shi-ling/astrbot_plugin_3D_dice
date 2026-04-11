import json
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

PLUGIN_DIR = Path(__file__).resolve().parent.parent
NODE_SCRIPT = PLUGIN_DIR / "render_dice_gif.mjs"


def render_dice_gif(
    dice_type: str = "D6",
    count: int = 1,
    duration: int = 2400,
    fps: int = 16,
    output_name: Optional[str] = None,
    browser: Optional[str] = None,
    output_dir: Optional[Path] = None,
    site_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    if not NODE_SCRIPT.exists():
        raise FileNotFoundError(f"Node script not found: {NODE_SCRIPT}")

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
    if output_dir:
        cmd.append(f"--outputDir={Path(output_dir).resolve()}")
    if site_dir:
        cmd.append(f"--siteDir={Path(site_dir).resolve()}")

    try:
        completed = subprocess.run(
            cmd,
            cwd=PLUGIN_DIR,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        stdout = (exc.stdout or "").strip()
        details = stderr or stdout or str(exc)
        raise RuntimeError(f"Node renderer failed: {details}")

    stdout = completed.stdout.strip().splitlines()
    if not stdout:
        raise RuntimeError("Renderer returned no output")

    return json.loads(stdout[-1])


if __name__ == "__main__":
    result = render_dice_gif()
    print(json.dumps(result, ensure_ascii=False))
