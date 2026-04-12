import argparse
import json
import os
import re
import shutil
import socketserver
import subprocess
import sys
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler
from io import BytesIO
from pathlib import Path
from typing import Any

from PIL import Image
from playwright.sync_api import TimeoutError, sync_playwright

from astrbot.api import logger

PLUGIN_DIR = Path(__file__).resolve().parent.parent
DEFAULT_TIMEOUT_MS = 60000
HEADLESS_GL_ERROR_PATTERNS = (
    "Requested GL implementation",
    "Exiting GPU process due to errors during initialization",
    "Failed to send GpuControl.CreateCommandBuffer",
    "Dice app did not become ready",
    "Timed out after waiting",
    "WebGL",
    "Target page, context or browser has been closed",
)


def append_debug(diagnostics: list[str], message: str) -> None:
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[3D_dice][render] {timestamp} {message}"
    diagnostics.append(line)
    logger.debug(line)


def render_dice_gif(
    dice_type: str = "D6",
    count: int = 1,
    duration: int = 2400,
    fps: int = 16,
    output_name: str | None = None,
    browser: str | None = None,
    output_dir: Path | None = None,
    site_dir: Path | None = None,
    linux_render_mode: str | None = None,
) -> dict[str, Any]:
    diagnostics: list[str] = []
    resolved_linux_render_mode = normalize_linux_render_mode(linux_render_mode)
    resolved_browser = browser or detect_browser_path()
    append_debug(
        diagnostics,
        "build request "
        f"dice_type={dice_type} count={count} duration={duration} fps={fps} "
        f"browser={resolved_browser or '<auto-miss>'} linux_mode={resolved_linux_render_mode or '<none>'}",
    )
    request = build_render_request(
        dice_type=dice_type,
        count=count,
        duration=duration,
        fps=fps,
        output_name=output_name,
        browser=resolved_browser,
        output_dir=output_dir,
        site_dir=site_dir,
        linux_render_mode=resolved_linux_render_mode,
    )

    try:
        return render_dice_gif_once(request, diagnostics=diagnostics)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            "Playwright renderer timed out while waiting for the browser process. "
            f"diagnostics: {' | '.join(diagnostics[-20:])}"
        ) from exc
    except Exception as exc:
        if should_retry_with_xvfb(exc, resolved_linux_render_mode):
            fallback_request = dict(request)
            fallback_request["linux_render_mode"] = "xvfb"
            append_debug(
                diagnostics,
                f"headless render failed, retrying with xvfb: {exc}",
            )
            try:
                return render_dice_gif_via_subprocess(
                    fallback_request, diagnostics=diagnostics
                )
            except subprocess.TimeoutExpired as retry_exc:
                raise RuntimeError(
                    "Playwright renderer timed out in xvfb fallback mode. "
                    f"diagnostics: {' | '.join(diagnostics[-20:])}"
                ) from retry_exc
            except subprocess.CalledProcessError as retry_exc:
                retry_details = (retry_exc.stderr or "").strip()
                if not retry_details:
                    retry_details = (retry_exc.stdout or "").strip() or str(retry_exc)
                raise RuntimeError(
                    "Playwright renderer failed in headless mode and xvfb fallback "
                    f"also failed: {retry_details} | diagnostics: {' | '.join(diagnostics[-20:])}"
                ) from retry_exc
        raise RuntimeError(
            f"Playwright renderer failed: {exc} | diagnostics: {' | '.join(diagnostics[-20:])}"
        ) from exc


def build_render_request(
    *,
    dice_type: str,
    count: int,
    duration: int,
    fps: int,
    output_name: str | None,
    browser: str | None,
    output_dir: Path | None,
    site_dir: Path | None,
    linux_render_mode: str | None,
) -> dict[str, Any]:
    return {
        "dice_type": dice_type,
        "count": count,
        "duration": duration,
        "fps": fps,
        "output_name": output_name,
        "browser": browser,
        "output_dir": str(Path(output_dir).resolve()) if output_dir else None,
        "site_dir": str(Path(site_dir).resolve()) if site_dir else None,
        "linux_render_mode": linux_render_mode,
        "timeout": DEFAULT_TIMEOUT_MS,
    }


def render_dice_gif_once(
    request: dict[str, Any], diagnostics: list[str] | None = None
) -> dict[str, Any]:
    site_dir = Path(request["site_dir"] or (PLUGIN_DIR / "rollmydice_app")).resolve()
    output_dir = Path(request["output_dir"] or (PLUGIN_DIR / "outputs")).resolve()
    output_name = request["output_name"] or default_output_name(request)
    output_path = output_dir / output_name
    timeout_ms = int(request["timeout"] or DEFAULT_TIMEOUT_MS)
    duration_ms = int(request["duration"] or 2400)
    fps = int(request["fps"] or 16)
    frame_delay = max(20, round(1000 / fps))
    total_frames = max(1, -(-duration_ms // frame_delay))
    max_animation_wait_ms = 2000
    browser_path = request["browser"]
    linux_render_mode = normalize_linux_render_mode(request.get("linux_render_mode"))

    if not site_dir.exists():
        raise FileNotFoundError(f"Site directory not found: {site_dir}")
    if not browser_path:
        raise FileNotFoundError(
            "Could not find a local Chromium/Chrome executable. "
            "Configure `browser_path`."
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    diagnostics = diagnostics if diagnostics is not None else []
    append_debug(
        diagnostics,
        f"render start site_dir={site_dir} output_path={output_path} timeout_ms={timeout_ms}",
    )

    with StaticServer(site_dir) as server:
        base_url = f"http://127.0.0.1:{server.port}/index.html"
        append_debug(diagnostics, f"static server listening at {base_url}")
        with sync_playwright() as playwright:
            browser = launch_browser(
                playwright=playwright,
                browser_path=browser_path,
                timeout_ms=timeout_ms,
                linux_render_mode=linux_render_mode,
                diagnostics=diagnostics,
            )
            try:
                context = browser.new_context(
                    viewport={"width": 900, "height": 1400},
                    device_scale_factor=1,
                )
                append_debug(diagnostics, "browser context created")
                page = context.new_page()
                attach_page_diagnostics(page, diagnostics)
                append_debug(diagnostics, "new page created")
                page.set_default_timeout(timeout_ms)
                page.set_default_navigation_timeout(timeout_ms)
                append_debug(diagnostics, f"navigating to {base_url}")
                page.goto(base_url, wait_until="domcontentloaded", timeout=timeout_ms)
                append_debug(diagnostics, f"navigation completed url={page.url}")
                wait_for_dice_app(page, timeout_ms)
                append_debug(diagnostics, "dice app ready")
                configure_dice(
                    page,
                    dice_type=request["dice_type"],
                    dice_count=int(request["count"] or 1),
                )
                append_debug(
                    diagnostics,
                    f"dice configured type={request['dice_type']} count={int(request['count'] or 1)}",
                )
                clip = get_capture_clip(page)
                append_debug(
                    diagnostics, f"capture clip={json.dumps(clip, ensure_ascii=False)}"
                )
                baseline_frame = capture_clip_png(page, clip)
                append_debug(diagnostics, "captured baseline frame")
                trigger_roll(page)
                append_debug(diagnostics, "roll triggered")
                wait_for_animation_start(
                    page,
                    clip,
                    baseline_frame,
                    max_animation_wait_ms,
                )
                append_debug(diagnostics, "animation start detected")
                frames = capture_frames(
                    page, clip, total_frames, frame_delay, diagnostics=diagnostics
                )
                append_debug(
                    diagnostics,
                    f"captured frames count={len(frames)} frame_delay_ms={frame_delay}",
                )
                write_gif(frames, output_path, frame_delay)
                append_debug(diagnostics, f"gif written to {output_path}")
                result = read_roll_results(
                    page,
                    int(request["count"] or 1),
                    str(request["dice_type"] or "D6"),
                    diagnostics,
                )
                append_debug(
                    diagnostics,
                    f"roll results parsed results={result['results']} total={result['total']}",
                )
                return {
                    "gif_path": str(output_path),
                    "results": result["results"],
                    "total": result["total"],
                    "dice_type": request["dice_type"],
                    "dice_count": int(request["count"] or 1),
                }
            except Exception as exc:
                append_debug(diagnostics, f"render failure: {exc}")
                debug_paths = dump_failure_artifacts(page, output_dir, diagnostics)
                details = "; ".join(diagnostics[-10:])
                if debug_paths:
                    details = f"{details}; artifacts: {json.dumps(debug_paths, ensure_ascii=False)}"
                if details:
                    raise RuntimeError(f"{exc} | diagnostics: {details}") from exc
                raise
            finally:
                append_debug(diagnostics, "closing browser")
                browser.close()


def detect_browser_path() -> str | None:
    candidates = [
        os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH"),
        os.environ.get("PUPPETEER_EXECUTABLE_PATH"),
        os.environ.get("BROWSER"),
        os.environ.get("CHROME_BIN"),
        os.environ.get("CHROMIUM_PATH"),
        "/usr/bin/chromium-browser",
        "/usr/bin/chromium",
        "/usr/bin/chrome",
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/snap/bin/chromium",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    return None


def default_output_name(request: dict[str, Any]) -> str:
    dice_type = str(request["dice_type"] or "D6").lower()
    count = int(request["count"] or 1)
    return f"{dice_type}-{count}-{int(time.time() * 1000)}.gif"


def launch_browser(
    *,
    playwright: Any,
    browser_path: str,
    timeout_ms: int,
    linux_render_mode: str | None,
    diagnostics: list[str] | None = None,
):
    has_display = bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
    headless = resolve_linux_headless_mode(linux_render_mode, has_display)
    args = [
        "--allow-file-access-from-files",
        "--autoplay-policy=no-user-gesture-required",
        "--disable-background-timer-throttling",
        "--disable-dev-shm-usage",
        "--disable-renderer-backgrounding",
        "--mute-audio",
    ]
    if sys.platform.startswith("linux"):
        args.extend(
            [
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--enable-webgl",
                "--enable-webgl2-compute-context",
                "--enable-unsafe-swiftshader",
                "--ignore-gpu-blocklist",
                "--use-angle=swiftshader",
                "--use-gl=angle",
                "--disable-gpu-sandbox",
            ]
        )
    if diagnostics is not None:
        append_debug(
            diagnostics,
            "launch browser "
            f"executable={browser_path} headless={headless} has_display={has_display} "
            f"args={json.dumps(args, ensure_ascii=False)}",
        )
    return playwright.chromium.launch(
        executable_path=browser_path,
        headless=headless,
        args=args,
        timeout=timeout_ms,
    )


def resolve_linux_headless_mode(
    linux_render_mode: str | None, has_display: bool
) -> bool:
    if not sys.platform.startswith("linux"):
        return True
    if linux_render_mode == "headless":
        return True
    if linux_render_mode == "xvfb":
        return False
    return not has_display


def attach_page_diagnostics(page: Any, diagnostics: list[str]) -> None:
    page.on(
        "console",
        lambda message: append_debug(
            diagnostics,
            f"[page:{message.type.upper()}] {message.text}",
        ),
    )
    page.on(
        "pageerror",
        lambda error: append_debug(
            diagnostics,
            f"[page:error] {getattr(error, 'message', str(error))}",
        ),
    )
    page.on(
        "requestfailed",
        lambda request: append_debug(
            diagnostics,
            "[page:requestfailed] "
            f"{request.method} {request.url} "
            f"{request.failure.error_text if request.failure else 'unknown'}",
        ),
    )
    page.on(
        "response",
        lambda response: (
            append_debug(
                diagnostics,
                f"[page:response] {response.status} {response.url}",
            )
            if response.status >= 400
            else None
        ),
    )


def wait_for_dice_app(page: Any, timeout_ms: int) -> None:
    try:
        page.wait_for_function(
            """
            () => {
              const canvas = document.querySelector("canvas");
              const buttons = [...document.querySelectorAll("button")];
              return Boolean(
                canvas && buttons.some((button) => /roll/i.test(button.textContent || ""))
              );
            }
            """,
            timeout=timeout_ms,
        )
        page.wait_for_selector("canvas", timeout=timeout_ms)
        page.wait_for_function(
            """
            () => {
              const canvas = document.querySelector("canvas");
              if (!canvas) return false;
              const rect = canvas.getBoundingClientRect();
              return rect.width > 100 && rect.height > 100;
            }
            """,
            timeout=timeout_ms,
        )
    except TimeoutError as error:
        page_state = collect_page_state(page)
        raise RuntimeError(
            f"Dice app did not become ready within {timeout_ms}ms. "
            f"State: {json.dumps(page_state, ensure_ascii=False)}"
        ) from error
    time.sleep(1)


def collect_page_state(page: Any) -> dict[str, Any]:
    return page.evaluate(
        """
        () => {
          const canvas = document.querySelector("canvas");
          const buttons = [...document.querySelectorAll("button")];
          const bodyText = (document.body?.innerText || "")
            .trim()
            .replace(/\\s+/g, " ")
            .slice(0, 300);
          const canvasRect = canvas?.getBoundingClientRect();
          return {
            title: document.title,
            readyState: document.readyState,
            buttonTexts: buttons
              .map((button) => (button.textContent || "").trim())
              .filter(Boolean),
            canvasCount: document.querySelectorAll("canvas").length,
            canvasRect: canvasRect
              ? {
                  width: Math.round(canvasRect.width),
                  height: Math.round(canvasRect.height),
                }
              : null,
            bodyText,
          };
        }
        """
    )


def configure_dice(page: Any, *, dice_type: str, dice_count: int) -> None:
    page.evaluate(
        """
        (label) => {
          const buttons = [...document.querySelectorAll("button")];
          const dieButton = buttons.find((button) => /^D\\d+$/i.test((button.textContent || "").trim()));
          const directTarget = buttons.find((button) => (button.textContent || "").trim() === label);
          if (directTarget) {
            directTarget.click();
            return;
          }
          if (dieButton) {
            dieButton.click();
          }
        }
        """,
        dice_type,
    )
    page.wait_for_function(
        """
        (label) => {
          const buttons = [...document.querySelectorAll("button")];
          return buttons.some((button) => (button.textContent || "").trim() === label);
        }
        """,
        arg=dice_type,
    )
    page.evaluate(
        """
        (label) => {
          const buttons = [...document.querySelectorAll("button")];
          const target = buttons.find((button) => (button.textContent || "").trim() === label);
          target?.click();
        }
        """,
        dice_type,
    )
    page.wait_for_function(
        """
        (label) => {
          const buttons = [...document.querySelectorAll("button")];
          const dieButton = buttons.find((button) => /^D\\d+$/i.test((button.textContent || "").trim()));
          return (dieButton?.textContent || "").trim() === label;
        }
        """,
        arg=dice_type,
    )
    current_count = page.evaluate(
        """
        () => {
          const heading = [...document.querySelectorAll("h1")]
            .find((node) => /^\\d+\\s+(Die|Dice)$/i.test((node.textContent || "").trim()));
          if (!heading) return 1;
          const match = (heading.textContent || "").match(/^\\s*(\\d+)/);
          return match ? Number(match[1]) : 1;
        }
        """
    )
    diff = dice_count - int(current_count or 1)
    if diff != 0:
        page.evaluate(
            """
            ({ direction, steps }) => {
              const heading = [...document.querySelectorAll("h1")]
                .find((node) => /^\\d+\\s+(Die|Dice)$/i.test((node.textContent || "").trim()));
              const parent = heading?.parentElement;
              const buttons = parent ? [...parent.querySelectorAll("button")] : [];
              const target = direction > 0 ? buttons.at(-1) : buttons[0];
              for (let index = 0; index < steps; index += 1) {
                target?.click();
              }
            }
            """,
            {"direction": 1 if diff > 0 else -1, "steps": abs(diff)},
        )
        page.wait_for_function(
            """
            (expectedCount) => {
              const heading = [...document.querySelectorAll("h1")]
                .find((node) => /^\\d+\\s+(Die|Dice)$/i.test((node.textContent || "").trim()));
              if (!heading) return false;
              const match = (heading.textContent || "").match(/^\\s*(\\d+)/);
              return match ? Number(match[1]) === expectedCount : false;
            }
            """,
            arg=dice_count,
        )
    time.sleep(0.3)


def get_capture_clip(page: Any) -> dict[str, int]:
    box = page.evaluate(
        """
        () => {
          const allCanvases = [...document.querySelectorAll("canvas")].map((canvas, index) => {
            const rect = canvas.getBoundingClientRect();
            const style = getComputedStyle(canvas);
            return {
              index,
              width: Math.round(rect.width),
              height: Math.round(rect.height),
              top: Math.round(rect.top),
              left: Math.round(rect.left),
              display: style.display,
              visibility: style.visibility,
              opacity: Number(style.opacity || "1"),
              area: Math.round(rect.width * rect.height),
            };
          });

          const visibleCanvases = allCanvases
            .filter((item) => item.width > 0 && item.height > 0)
            .sort((a, b) => b.area - a.area);

          const canvasInfo = visibleCanvases[0] || allCanvases[0] || null;
          if (!canvasInfo) {
            return { clip: null, canvases: allCanvases };
          }

          const canvas = document.querySelectorAll("canvas")[canvasInfo.index];
          if (!canvas) {
            return { clip: null, canvases: allCanvases };
          }

          const rect = canvas.getBoundingClientRect();
          if (!(rect.width > 0 && rect.height > 0)) {
            return { clip: null, canvases: allCanvases };
          }

          const top = Math.max(0, rect.top - 40);
          const left = Math.max(0, rect.left - 24);
          const right = Math.min(window.innerWidth, rect.right + 24);
          const bottom = Math.min(window.innerHeight, rect.bottom + 80);

          return {
            clip: {
              x: left,
              y: top,
              width: right - left,
              height: bottom - top,
            },
            canvases: allCanvases,
          };
        }
        """
    )
    if not box or not box.get("clip"):
        raise RuntimeError(
            "Could not locate dice canvas clip region; "
            f"canvases={json.dumps((box or {}).get('canvases', []), ensure_ascii=False)}"
        )
    clip = {
        "x": round(box["clip"]["x"]),
        "y": round(box["clip"]["y"]),
        "width": round(box["clip"]["width"]),
        "height": round(box["clip"]["height"]),
    }
    if clip["width"] < 120 or clip["height"] < 120:
        raise RuntimeError(
            "Dice canvas clip region is unexpectedly small: "
            f"{json.dumps(clip, ensure_ascii=False)}; "
            f"canvases={json.dumps(box.get('canvases', []), ensure_ascii=False)}"
        )
    return clip


def trigger_roll(page: Any) -> None:
    page.evaluate(
        """
        () => {
          const buttons = [...document.querySelectorAll("button")];
          const rollButton = buttons.find((button) => /roll/i.test(button.textContent || ""));
          if (!rollButton) {
            throw new Error("Roll button not found");
          }
          rollButton.click();
        }
        """
    )


def capture_frames(
    page: Any,
    clip: dict[str, int],
    total_frames: int,
    delay_ms: int,
    diagnostics: list[str] | None = None,
) -> list[Image.Image]:
    frames: list[Image.Image] = []
    for index in range(total_frames):
        frames.append(capture_clip_png(page, clip))
        if diagnostics is not None and (
            index == 0 or index == total_frames - 1 or (index + 1) % 10 == 0
        ):
            append_debug(
                diagnostics,
                f"captured frame {index + 1}/{total_frames}",
            )
        if index < total_frames - 1:
            time.sleep(delay_ms / 1000)
    return frames


def capture_clip_png(page: Any, clip: dict[str, int]) -> Image.Image:
    png_buffer = page.screenshot(clip=clip, type="png", timeout=15000)
    return Image.open(BytesIO(png_buffer)).convert("RGBA")


def wait_for_animation_start(
    page: Any,
    clip: dict[str, int],
    baseline_frame: Image.Image,
    timeout_ms: int,
) -> None:
    started_at = time.monotonic()
    while (time.monotonic() - started_at) * 1000 < timeout_ms:
        time.sleep(0.08)
        current_frame = capture_clip_png(page, clip)
        if frames_differ_enough(baseline_frame, current_frame):
            return


def frames_differ_enough(first_frame: Image.Image, second_frame: Image.Image) -> bool:
    if first_frame.size != second_frame.size:
        return True
    first_data = first_frame.tobytes()
    second_data = second_frame.tobytes()
    total_pixels = first_frame.width * first_frame.height
    sample_stride = max(1, total_pixels // 2500)
    changed_samples = 0
    total_samples = 0
    for pixel_index in range(0, total_pixels, sample_stride):
        offset = pixel_index * 4
        delta = (
            abs(first_data[offset] - second_data[offset])
            + abs(first_data[offset + 1] - second_data[offset + 1])
            + abs(first_data[offset + 2] - second_data[offset + 2])
            + abs(first_data[offset + 3] - second_data[offset + 3])
        )
        total_samples += 1
        if delta > 24:
            changed_samples += 1
    return changed_samples / max(1, total_samples) > 0.02


def write_gif(frames: list[Image.Image], output_file: Path, delay_ms: int) -> None:
    if not frames:
        raise RuntimeError("No frames captured")
    first_frame = frames[0]
    append_frames = frames[1:]
    first_frame.save(
        output_file,
        save_all=True,
        append_images=append_frames,
        duration=max(20, delay_ms),
        loop=0,
        disposal=2,
    )


def read_roll_results(
    page: Any, dice_count: int, dice_type: str, diagnostics: list[str] | None = None
) -> dict[str, Any]:
    max_face = get_dice_face_count(dice_type)
    min_total = dice_count
    max_total = dice_count * max_face

    for attempt in range(1, 9):
        time.sleep(0.25)
        result = page.evaluate(
            """
            () => {
              const nodes = [...document.querySelectorAll("div, span, p, h1, h2")];
              const visible = nodes
                .map((node) => {
                  const text = (node.textContent || "").trim();
                  const style = getComputedStyle(node);
                  const rect = node.getBoundingClientRect();
                  return {
                    text,
                    display: style.display,
                    visibility: style.visibility,
                    opacity: Number(style.opacity || "1"),
                    fontSize: Number.parseFloat(style.fontSize || "0"),
                    fontWeight: Number.parseInt(style.fontWeight || "400", 10) || 400,
                    top: Math.round(rect.top),
                    left: Math.round(rect.left),
                    width: Math.round(rect.width),
                    height: Math.round(rect.height),
                  };
                })
                .filter((item) =>
                  item.text &&
                  item.display !== "none" &&
                  item.visibility !== "hidden" &&
                  item.opacity > 0 &&
                  item.width > 0 &&
                  item.height > 0
                );
              const numericCandidates = visible
                .filter((item) => /^\\d+$/.test(item.text))
                .sort((a, b) => b.fontSize - a.fontSize || a.top - b.top)
                .map((item) => ({
                  ...item,
                  value: Number(item.text),
                }));
              const breakdownCandidates = visible
                .filter((item) => /^\\d+(?:\\s*\\+\\s*\\d+)+$/.test(item.text))
                .sort((a, b) => b.fontSize - a.fontSize || a.top - b.top)
                .map((item) => ({
                  ...item,
                  parts: item.text
                    .split("+")
                    .map((part) => Number(part.trim()))
                    .filter((value) => Number.isFinite(value)),
                }));
              return {
                numericCandidates,
                breakdownCandidates,
                bodyText: (document.body?.innerText || "").trim().replace(/\\s+/g, " ").slice(0, 500),
              };
            }
            """
        )

        numeric_candidates = result.get("numericCandidates", [])
        breakdown_candidates = result.get("breakdownCandidates", [])

        if diagnostics is not None:
            append_debug(
                diagnostics,
                "roll result candidates "
                f"attempt={attempt} numeric={json.dumps(numeric_candidates[:8], ensure_ascii=False)} "
                f"breakdown={json.dumps(breakdown_candidates[:4], ensure_ascii=False)}",
            )

        for candidate in breakdown_candidates:
            parts = candidate.get("parts", [])
            if len(parts) == dice_count and all(
                1 <= int(value) <= max_face for value in parts
            ):
                total = sum(int(value) for value in parts)
                if min_total <= total <= max_total:
                    return {"results": [int(value) for value in parts], "total": total}

        for candidate in numeric_candidates:
            value = candidate.get("value")
            if not isinstance(value, int):
                continue
            if min_total <= value <= max_total:
                return {"results": [value], "total": value}

    raise RuntimeError(
        f"Could not parse a valid {dice_type} roll result from the page. "
        f"Expected total in range [{min_total}, {max_total}]."
    )


def get_dice_face_count(dice_type: str) -> int:
    match = re.fullmatch(r"D(\\d+)", dice_type.strip().upper())
    if not match:
        raise ValueError(f"Unsupported dice type: {dice_type}")
    return int(match.group(1))


def normalize_linux_render_mode(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip().lower()
    if not normalized:
        return None
    if normalized not in {"auto", "headless", "xvfb"}:
        raise ValueError("linux_render_mode must be one of: auto, headless, xvfb.")
    return normalized


def should_retry_with_xvfb(exc: Exception, linux_render_mode: str | None) -> bool:
    if not sys.platform.startswith("linux"):
        return False
    if linux_render_mode not in {None, "auto", "headless"}:
        return False
    if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
        return False
    if not shutil.which("xvfb-run"):
        return False
    details = str(exc)
    return any(pattern in details for pattern in HEADLESS_GL_ERROR_PATTERNS)


def render_dice_gif_via_subprocess(
    request: dict[str, Any], diagnostics: list[str] | None = None
) -> dict[str, Any]:
    payload = json.dumps(request, ensure_ascii=False)
    command = [
        shutil.which("xvfb-run") or "xvfb-run",
        "-a",
        "-s",
        "-screen 0 1280x1600x24",
        sys.executable,
        str(Path(__file__).resolve()),
        "--payload",
        payload,
    ]
    if diagnostics is not None:
        append_debug(
            diagnostics,
            f"launch xvfb fallback command={json.dumps(command, ensure_ascii=False)}",
        )
    completed = subprocess.run(
        command,
        cwd=PLUGIN_DIR,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=build_render_env(),
        timeout=(int(request.get("timeout") or DEFAULT_TIMEOUT_MS) / 1000) + 15,
    )
    if diagnostics is not None and completed.stderr:
        for line in completed.stderr.strip().splitlines()[-20:]:
            append_debug(diagnostics, f"[xvfb:stderr] {line}")
    stdout = completed.stdout.strip().splitlines()
    if not stdout:
        raise RuntimeError("Renderer subprocess returned no output")
    return json.loads(stdout[-1])


def dump_failure_artifacts(
    page: Any, output_dir: Path, diagnostics: list[str]
) -> dict[str, str]:
    debug_dir = output_dir / "debug"
    debug_dir.mkdir(parents=True, exist_ok=True)
    stamp = str(int(time.time() * 1000))
    artifacts: dict[str, str] = {}
    try:
        screenshot_path = debug_dir / f"failure-{stamp}.png"
        page.screenshot(path=str(screenshot_path), full_page=True)
        artifacts["screenshot"] = str(screenshot_path)
        append_debug(diagnostics, f"saved failure screenshot to {screenshot_path}")
    except Exception as exc:
        append_debug(diagnostics, f"failed to save failure screenshot: {exc}")
    try:
        html_path = debug_dir / f"failure-{stamp}.html"
        html_path.write_text(page.content(), encoding="utf-8")
        artifacts["html"] = str(html_path)
        append_debug(diagnostics, f"saved failure html to {html_path}")
    except Exception as exc:
        append_debug(diagnostics, f"failed to save failure html: {exc}")
    try:
        state_path = debug_dir / f"failure-{stamp}.json"
        state = {
            "url": page.url,
            "title": page.title(),
            "state": collect_page_state(page),
            "diagnostics_tail": diagnostics[-50:],
        }
        state_path.write_text(
            json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        artifacts["state"] = str(state_path)
        append_debug(diagnostics, f"saved failure state to {state_path}")
    except Exception as exc:
        append_debug(diagnostics, f"failed to save failure state: {exc}")
    return artifacts


def build_render_env() -> dict[str, str]:
    env = os.environ.copy()
    if sys.platform.startswith("linux"):
        env.setdefault("LIBGL_ALWAYS_SOFTWARE", "1")
        env.setdefault("MESA_LOADER_DRIVER_OVERRIDE", "llvmpipe")
        env.setdefault("EGL_PLATFORM", "surfaceless")
    return env


class StaticFileHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        return

    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


class ThreadingHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


class StaticServer:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.httpd: ThreadingHTTPServer | None = None
        self.thread: threading.Thread | None = None
        self.port = 0

    def __enter__(self) -> "StaticServer":
        handler = partial(StaticFileHandler, directory=str(self.root_dir))
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self.port = int(self.httpd.server_address[1])
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
        if self.thread:
            self.thread.join(timeout=2)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--payload")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.payload:
        result = render_dice_gif_once(json.loads(args.payload))
    else:
        result = render_dice_gif()
    print(json.dumps(result, ensure_ascii=False))
