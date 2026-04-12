from __future__ import annotations

import json
import os
import secrets
import socketserver
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from functools import partial
from http.server import SimpleHTTPRequestHandler
from io import BytesIO
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops

RUNTIME_DIR = Path(__file__).resolve().parent
PROJECT_DIR = RUNTIME_DIR.parent
DEFAULT_TIMEOUT_MS = 60000
DEFAULT_RESULT_TIMEOUT_MS = 8000
PLAYWRIGHT_INSTALL_TIMEOUT_SECONDS = 600

# A single persistent browser/page is reused between render requests.
_session_lock = threading.Lock()
_persisted_session: PersistedBrowserSession | None = None


class PersistedBrowserSession:
    """Persistent browser session reused between dice renders."""

    def __init__(
        self,
        browser_path: str,
        site_dir: Path,
        width: int,
        height: int,
        timeout_ms: int,
    ) -> None:
        self.browser_path = browser_path
        self.site_dir = site_dir
        self.width = width
        self.height = height
        self.timeout_ms = timeout_ms

        self._playwright_ctx: Any = None
        self._browser: Any = None
        self._page: Any = None
        self._server: StaticServer | None = None
        self._clip: dict[str, int] | None = None
        self._ready = False
        self.render_lock = threading.Lock()

    def start(self) -> None:
        sync_playwright = get_sync_playwright()
        self._playwright_ctx = sync_playwright().__enter__()
        self._server = StaticServer(self.site_dir)
        self._server.__enter__()
        base_url = f"http://127.0.0.1:{self._server.port}/index.html"

        self._browser = self._playwright_ctx.chromium.launch(
            executable_path=self.browser_path,
            headless=True,
            timeout=self.timeout_ms,
            args=[
                "--allow-file-access-from-files",
                "--autoplay-policy=no-user-gesture-required",
                "--disable-background-timer-throttling",
                "--disable-dev-shm-usage",
                "--disable-renderer-backgrounding",
                "--mute-audio",
            ],
        )
        context = self._browser.new_context(
            viewport={"width": self.width, "height": self.height},
            device_scale_factor=1,
        )
        self._page = context.new_page()
        self._page.set_default_timeout(self.timeout_ms)
        self._page.set_default_navigation_timeout(self.timeout_ms)
        self._page.goto(
            base_url, wait_until="domcontentloaded", timeout=self.timeout_ms
        )
        wait_for_dice_app(self._page)
        self._clip = get_capture_clip(self._page)
        self._ready = True

    def is_alive(self) -> bool:
        """Return whether the persisted page still accepts commands."""
        if not self._ready or self._page is None:
            return False
        try:
            self._page.evaluate("() => true")
            return True
        except Exception:
            return False

    def matches(
        self,
        browser_path: str,
        site_dir: Path,
        width: int,
        height: int,
        timeout_ms: int,
    ) -> bool:
        """Return whether this session was created with the requested settings."""
        return (
            self.browser_path == browser_path
            and self.site_dir == site_dir
            and self.width == width
            and self.height == height
            and self.timeout_ms == timeout_ms
        )

    def get_page_and_clip(self) -> tuple[Any, dict[str, int]]:
        return self._page, self._clip  # type: ignore[return-value]

    def close(self) -> None:
        self._ready = False
        try:
            if self._browser:
                self._browser.close()
        except Exception:
            pass
        try:
            if self._playwright_ctx:
                self._playwright_ctx.__exit__(None, None, None)
        except Exception:
            pass
        try:
            if self._server:
                self._server.__exit__(None, None, None)
        except Exception:
            pass
        self._browser = None
        self._page = None
        self._playwright_ctx = None
        self._server = None


def get_persisted_session(
    browser_path: str,
    site_dir: Path,
    width: int,
    height: int,
    timeout_ms: int,
) -> PersistedBrowserSession:
    """Return or recreate the global persistent browser session."""
    global _persisted_session
    with _session_lock:
        if _persisted_session is not None and (
            not _persisted_session.is_alive()
            or not _persisted_session.matches(
                browser_path=browser_path,
                site_dir=site_dir,
                width=width,
                height=height,
                timeout_ms=timeout_ms,
            )
        ):
            _persisted_session.close()
            _persisted_session = None

        if _persisted_session is None:
            session = PersistedBrowserSession(
                browser_path=browser_path,
                site_dir=site_dir,
                width=width,
                height=height,
                timeout_ms=timeout_ms,
            )
            session.start()
            _persisted_session = session

        return _persisted_session


def close_persisted_session() -> None:
    """Close and clear the global persistent browser session."""
    global _persisted_session
    with _session_lock:
        if _persisted_session is not None:
            _persisted_session.close()
            _persisted_session = None


# 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€


@dataclass(frozen=True)
class BrowserSetupResult:
    browser_path: str
    installed: bool


def playwright_install_reminder() -> str:
    return (
        "3D dice requires Playwright. Install it in the AstrBot Python environment, "
        "then install Chromium: python -m pip install playwright && "
        "python -m playwright install chromium"
    )


def is_playwright_available() -> bool:
    try:
        get_sync_playwright()
    except ModuleNotFoundError:
        return False
    return True


def get_sync_playwright() -> Any:
    try:
        from playwright.sync_api import sync_playwright
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(playwright_install_reminder()) from exc
    return sync_playwright


def render_dice_gif(
    dice_type: str = "D6",
    count: int = 1,
    duration: int = 2400,
    fps: int = 16,
    output_name: str | None = None,
    browser: str | None = None,
    output_dir: Path | None = None,
    site_dir: Path | None = None,
    width: int = 900,
    height: int = 1400,
    better_render_quality: bool = True,
    parallel_result: bool = False,
) -> dict[str, Any]:
    """Render a dice GIF and return the parsed roll result.

    Playwright sync pages are single-threaded. ``parallel_result`` keeps the
    faster behavior by reading the result immediately after GIF capture, but it
    does not access the reused page from a second thread.
    """
    site_dir = Path(site_dir or (PROJECT_DIR / "dice_roller_app")).resolve()
    output_dir = Path(output_dir or (RUNTIME_DIR / "outputs")).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / (output_name or default_output_name(dice_type, count))
    browser_path = browser or detect_browser_path()
    timeout_ms = DEFAULT_TIMEOUT_MS

    if not site_dir.exists():
        raise FileNotFoundError(f"Site directory not found: {site_dir}")
    if not browser_path:
        raise FileNotFoundError(
            "Could not find a local Chromium/Chrome/Edge executable. Pass browser=..."
        )

    frame_delay = max(20, round(1000 / max(1, fps)))
    total_frames = max(1, -(-duration // frame_delay))

    session = get_persisted_session(
        browser_path=browser_path,
        site_dir=site_dir,
        width=width,
        height=height,
        timeout_ms=timeout_ms,
    )

    with session.render_lock:
        page, clip = session.get_page_and_clip()

        try:
            configure_dice(page, dice_type=dice_type, dice_count=count)
            if better_render_quality:
                wait_for_stable_render(page, clip)
            baseline_frame = capture_clip_png(page, clip)
            trigger_roll(page)
            if better_render_quality:
                wait_for_roll_start(page, clip, baseline_frame)
            else:
                wait_for_animation_start(page, clip, baseline_frame, 2000)
            frames = capture_frames(page, clip, total_frames, frame_delay)
            write_gif(frames, output_path, frame_delay)

            if parallel_result:
                result = read_roll_results(page, count, dice_type)
            else:
                page.wait_for_timeout(max(2500, duration))
                result = read_roll_results(page, count, dice_type)

        except Exception:
            # Rebuild the persistent page on the next request after any page error.
            close_persisted_session()
            raise

    return {
        "gif_path": str(output_path),
        "results": result["results"],
        "total": result["total"],
        "dice_type": dice_type,
        "dice_count": count,
        "fallback": bool(result.get("fallback", False)),
        "partial": bool(result.get("partial", False)),
    }


def default_output_name(dice_type: str, count: int) -> str:
    return f"{dice_type.lower()}-{count}-{int(time.time() * 1000)}.gif"


def detect_browser_path() -> str | None:
    program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
    program_files_x86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    candidates = [
        os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH"),
        os.environ.get("PUPPETEER_EXECUTABLE_PATH"),
        os.environ.get("BROWSER"),
        os.environ.get("CHROME_BIN"),
        str(Path(program_files) / "Google/Chrome/Application/chrome.exe"),
        str(Path(program_files_x86) / "Google/Chrome/Application/chrome.exe"),
        str(Path(program_files) / "Microsoft/Edge/Application/msedge.exe"),
        str(Path(program_files_x86) / "Microsoft/Edge/Application/msedge.exe"),
        str(Path(local_app_data) / "Google/Chrome/Application/chrome.exe")
        if local_app_data
        else None,
        str(Path(local_app_data) / "Microsoft/Edge/Application/msedge.exe")
        if local_app_data
        else None,
        "/usr/bin/chromium-browser",
        "/usr/bin/chromium",
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/snap/bin/chromium",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    return detect_playwright_chromium_path()


def detect_playwright_chromium_path() -> str | None:
    try:
        with get_sync_playwright()() as playwright:
            candidate = playwright.chromium.executable_path
    except Exception:
        return None
    if candidate and Path(candidate).exists():
        return str(candidate)
    return None


def ensure_chromium_browser(auto_install: bool = True) -> BrowserSetupResult:
    browser_path = detect_browser_path()
    if browser_path:
        return BrowserSetupResult(browser_path=browser_path, installed=False)

    if not auto_install:
        raise FileNotFoundError(
            "Could not find a local Chromium/Chrome/Edge executable. "
            "Install Chromium with: python -m playwright install chromium"
        )

    install_playwright_chromium()
    browser_path = detect_browser_path()
    if browser_path:
        return BrowserSetupResult(browser_path=browser_path, installed=True)

    raise FileNotFoundError(
        "Playwright Chromium installation finished, but no browser executable was found."
    )


def install_playwright_chromium() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "playwright", "install", "chromium"],
        capture_output=True,
        check=False,
        text=True,
        timeout=PLAYWRIGHT_INSTALL_TIMEOUT_SECONDS,
    )
    if completed.returncode == 0:
        return

    output = "\n".join(
        part.strip()
        for part in (completed.stdout, completed.stderr)
        if part and part.strip()
    )
    raise RuntimeError(
        "Failed to install Playwright Chromium "
        f"(exit code {completed.returncode}). {output}"
    )


def wait_for_dice_app(page: Any) -> None:
    """Wait until the dice app has mounted and WebGL is ready."""
    page.wait_for_function(
        """
        () => {
          const canvas = document.querySelector('canvas');
          const buttons = [...document.querySelectorAll('button')];
          return Boolean(canvas && buttons.some((button) => /roll/i.test(button.textContent || '')));
        }
        """
    )
    page.wait_for_selector("canvas")
    page.wait_for_function(
        """
        () => {
          const canvas = document.querySelector('canvas');
          if (!canvas) return false;
          const rect = canvas.getBoundingClientRect();
          return rect.width > 100 && rect.height > 100;
        }
        """
    )
    page.wait_for_function(
        """
        () => new Promise((resolve) => {
          const canvas = document.querySelector('canvas');
          if (!canvas) return resolve(false);
          const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
          if (!gl || gl.drawingBufferWidth <= 0 || gl.drawingBufferHeight <= 0) {
            return resolve(false);
          }
          requestAnimationFrame(() => requestAnimationFrame(() => resolve(true)));
        })
        """,
        timeout=10000,
    )
    page.evaluate("window.scrollTo(0, 0)")


def wait_for_roll_start(
    page: Any,
    clip: dict[str, int],
    baseline_frame: Image.Image,
    max_wait_ms: int = 1500,
) -> None:
    """绛夊緟楠板瓙寮€濮嬭繍鍔ㄥ悗鍐嶅綍鍒跺抚锛堝缓璁洓鏇夸唬鏂规锛夈€?

    鍘熸潵 better_render_quality=True 鏃剁洿鎺?wait_for_timeout(140)锛?
    杩欓噷鏀逛负涓诲姩妫€娴嬬敾闈㈠彉鍖栵紝楠板瓙涓€鍔ㄥ氨绔嬪嵆寮€濮嬪綍鍒讹紝
    鏃笉浼氬洜鍥哄畾寤惰繜婕忔帀璧峰甯э紝涔熶笉浼氬湪鎱㈤€熸満鍣ㄤ笂杩囨棭鎴浘銆?
    """
    deadline = time.time() + (max_wait_ms / 1000.0)
    while time.time() < deadline:
        current_frame = capture_clip_png(page, clip)
        if count_changed_pixels(baseline_frame, current_frame) > 10:
            return
        page.wait_for_timeout(30)
    # 瓒呮椂涔熺户缁紝涓嶆姏寮傚父锛堥瀛愬彲鑳藉凡缁忓湪杩愬姩浜嗭級


def configure_dice(page: Any, dice_type: str, dice_count: int) -> None:
    page.evaluate(
        """
        (label) => {
          const buttons = [...document.querySelectorAll('button')];
          const dieButton = buttons.find((button) => /^D\\d+$/i.test((button.textContent || '').trim()));
          const directTarget = buttons.find((button) => (button.textContent || '').trim() === label);
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
          const buttons = [...document.querySelectorAll('button')];
          return buttons.some((button) => (button.textContent || '').trim() === label);
        }
        """,
        arg=dice_type,
    )
    page.evaluate(
        """
        (label) => {
          const buttons = [...document.querySelectorAll('button')];
          const target = buttons.find((button) => (button.textContent || '').trim() === label);
          if (target) {
            target.click();
          }
        }
        """,
        dice_type,
    )
    page.wait_for_function(
        """
        (label) => {
          const buttons = [...document.querySelectorAll('button')];
          const dieButton = buttons.find((button) => /^D\\d+$/i.test((button.textContent || '').trim()));
          return (dieButton?.textContent || '').trim() === label;
        }
        """,
        arg=dice_type,
    )

    if dice_count < 1:
        return

    current_count = page.evaluate(
        """
        () => {
          const heading = [...document.querySelectorAll('h1')].find((node) => /^\\d+\\s+(Die|Dice)$/i.test((node.textContent || '').trim()));
          if (!heading) return 1;
          const match = (heading.textContent || '').match(/^\\s*(\\d+)/);
          return match ? Number(match[1]) : 1;
        }
        """
    )
    diff = int(dice_count) - int(current_count or 1)
    if diff == 0:
        return

    page.evaluate(
        """
        ({ direction, steps }) => {
          const heading = [...document.querySelectorAll('h1')].find((node) => /^\\d+\\s+(Die|Dice)$/i.test((node.textContent || '').trim()));
          if (!heading) return;
          const parent = heading.parentElement;
          if (!parent) return;
          const buttons = [...parent.querySelectorAll('button')];
          const target = direction > 0 ? buttons[buttons.length - 1] : buttons[0];
          if (!target) return;
          for (let i = 0; i < steps; i += 1) {
            target.click();
          }
        }
        """,
        {"direction": 1 if diff > 0 else -1, "steps": abs(diff)},
    )
    page.wait_for_function(
        """
        (expectedCount) => {
          const heading = [...document.querySelectorAll('h1')].find((node) => /^\\d+\\s+(Die|Dice)$/i.test((node.textContent || '').trim()));
          if (!heading) return false;
          const match = (heading.textContent || '').match(/^\\s*(\\d+)/);
          return match ? Number(match[1]) === expectedCount : false;
        }
        """,
        arg=dice_count,
    )
    page.wait_for_timeout(300)


def get_capture_clip(page: Any) -> dict[str, int]:
    clip = page.evaluate(
        """
        () => {
          const canvases = [...document.querySelectorAll('canvas')];
          const target = canvases.find((canvas) => {
            const rect = canvas.getBoundingClientRect();
            return rect.width > 200 && rect.height > 200;
          }) || canvases[0];
          if (!target) return null;
          const rect = target.getBoundingClientRect();
          return {
            x: Math.max(0, Math.floor(rect.left - 24)),
            y: Math.max(0, Math.floor(rect.top - 40)),
            width: Math.min(window.innerWidth, Math.ceil(rect.width + 48)),
            height: Math.min(window.innerHeight, Math.ceil(rect.height + 80)),
          };
        }
        """
    )
    if not clip:
        raise RuntimeError("Could not locate dice canvas")
    return {
        "x": int(clip["x"]),
        "y": int(clip["y"]),
        "width": int(clip["width"]),
        "height": int(clip["height"]),
    }


def capture_clip_png(page: Any, clip: dict[str, int]) -> Image.Image:
    png_bytes = page.screenshot(type="png", clip=clip)
    return Image.open(BytesIO(png_bytes)).convert("RGBA")


def count_changed_pixels(before: Image.Image, after: Image.Image) -> int:
    diff = ImageChops.difference(before.convert("RGBA"), after.convert("RGBA"))
    alpha = diff.convert("L")
    return sum(1 for pixel in alpha.getdata() if pixel)


def wait_for_stable_render(
    page: Any,
    clip: dict[str, int],
    stable_samples: int = 3,
    interval_ms: int = 160,
    max_wait_ms: int = 3000,
    changed_pixel_tolerance: int = 40,
) -> None:
    previous_frame = capture_clip_png(page, clip)
    stable_count = 0
    deadline = time.time() + (max_wait_ms / 1000.0)

    while time.time() < deadline:
        page.wait_for_timeout(interval_ms)
        current_frame = capture_clip_png(page, clip)
        changed_pixels = count_changed_pixels(previous_frame, current_frame)
        if changed_pixels <= changed_pixel_tolerance:
            stable_count += 1
            if stable_count >= stable_samples:
                return
        else:
            stable_count = 0
        previous_frame = current_frame


def trigger_roll(page: Any) -> None:
    page.evaluate(
        """
        () => {
          const buttons = [...document.querySelectorAll('button')];
          const target = buttons.find((button) => /roll/i.test(button.textContent || ''));
          if (!target) {
            throw new Error('Roll button not found');
          }
          target.click();
        }
        """
    )


def wait_for_animation_start(
    page: Any,
    clip: dict[str, int],
    baseline_frame: Image.Image,
    max_wait_ms: int,
) -> None:
    deadline = time.time() + (max_wait_ms / 1000.0)
    while time.time() < deadline:
        current_frame = capture_clip_png(page, clip)
        if count_changed_pixels(baseline_frame, current_frame) > 0:
            return
        page.wait_for_timeout(100)
    raise RuntimeError("Timed out waiting for animation to start")


def capture_frames(
    page: Any, clip: dict[str, int], total_frames: int, frame_delay_ms: int
) -> list[Image.Image]:
    frames = []
    started_at = time.time()
    for index in range(total_frames):
        target_time = started_at + (index * frame_delay_ms / 1000.0)
        sleep_seconds = target_time - time.time()
        if sleep_seconds > 0:
            time.sleep(sleep_seconds)
        frames.append(capture_clip_png(page, clip))
    return frames


def write_gif(
    frames: list[Image.Image], output_path: Path, frame_delay_ms: int
) -> None:
    if not frames:
        raise RuntimeError("No frames captured")
    first, rest = frames[0], frames[1:]
    first.save(
        output_path,
        save_all=True,
        append_images=rest,
        format="GIF",
        duration=frame_delay_ms,
        loop=0,
        disposal=2,
    )


def read_roll_results(
    page: Any,
    dice_count: int,
    dice_type: str,
    timeout_ms: int = DEFAULT_RESULT_TIMEOUT_MS,
    fallback_random: bool = True,
) -> dict[str, Any]:
    deadline = time.time() + (max(1000, timeout_ms) / 1000.0)
    best_total_result: dict[str, Any] | None = None

    while time.time() < deadline:
        page.wait_for_timeout(100)
        result = parse_roll_result_snapshot(
            read_roll_result_snapshot(page), dice_count, dice_type
        )
        if result and result.get("results"):
            return result
        if result:
            best_total_result = result

    if best_total_result:
        return best_total_result

    if fallback_random:
        return make_fallback_roll_result(dice_count, dice_type)

    snapshot = read_roll_result_snapshot(page)
    raise RuntimeError(
        "Could not parse dice results from page. "
        f"numeric={snapshot.get('numericCandidates', [])[:5]!r}, "
        f"breakdown={snapshot.get('breakdownCandidates', [])[:5]!r}"
    )


def read_roll_result_snapshot(page: Any) -> dict[str, Any]:
    return page.evaluate(
        """
        () => {
          const nodes = [...document.querySelectorAll('div, span, p, h1, h2')];
          const appResults = Array.isArray(globalThis.__astrbotDiceResults)
            ? globalThis.__astrbotDiceResults
                .map((value) => Number(value))
                .filter((value) => Number.isFinite(value))
            : [];
          const visible = nodes
            .map((node) => {
              const text = (node.textContent || '').trim();
              const style = getComputedStyle(node);
              const rect = node.getBoundingClientRect();
              return {
                text,
                display: style.display,
                visibility: style.visibility,
                opacity: Number(style.opacity || '1'),
                fontSize: Number.parseFloat(style.fontSize || '0'),
                fontWeight: Number.parseInt(style.fontWeight || '400', 10) || 400,
                top: Math.round(rect.top),
                left: Math.round(rect.left),
                width: Math.round(rect.width),
                height: Math.round(rect.height),
              };
            })
            .filter((item) =>
              item.text &&
              item.display !== 'none' &&
              item.visibility !== 'hidden' &&
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
                .split('+')
                .map((part) => Number(part.trim()))
                .filter((value) => Number.isFinite(value)),
            }));

          return { appResults, numericCandidates, breakdownCandidates };
        }
        """
    )


def parse_roll_result_snapshot(
    data: dict[str, Any], dice_count: int, dice_type: str
) -> dict[str, Any] | None:
    max_face = get_dice_face_count(dice_type)
    min_total = dice_count
    max_total = dice_count * max_face

    app_results = data.get("appResults", [])
    if (
        isinstance(app_results, list)
        and len(app_results) >= dice_count
        and all(isinstance(value, int | float) for value in app_results[:dice_count])
    ):
        results = [int(value) for value in app_results[:dice_count]]
        if all(1 <= value <= max_face for value in results):
            return {"results": results, "total": sum(results)}

    for candidate in data.get("breakdownCandidates", []):
        parts = candidate.get("parts", [])
        if len(parts) != dice_count:
            continue
        if not all(1 <= int(value) <= max_face for value in parts):
            continue
        total = sum(int(value) for value in parts)
        if min_total <= total <= max_total:
            return {"results": [int(value) for value in parts], "total": total}

    for candidate in data.get("numericCandidates", []):
        value = candidate.get("value")
        if (
            isinstance(value, int)
            and min_total <= value <= max_total
            and is_likely_total_candidate(candidate)
        ):
            if dice_count == 1:
                return {"results": [value], "total": value}
            return {"results": [], "total": value, "partial": True}

    return None


def is_likely_total_candidate(candidate: dict[str, Any]) -> bool:
    return float(candidate.get("fontSize") or 0) >= 40


def make_fallback_roll_result(dice_count: int, dice_type: str) -> dict[str, Any]:
    max_face = get_dice_face_count(dice_type)
    results = [secrets.randbelow(max_face) + 1 for _ in range(dice_count)]
    return {
        "results": results,
        "total": sum(results),
        "fallback": True,
    }


def get_dice_face_count(dice_type: str) -> int:
    normalized = str(dice_type or "").strip().upper()
    if not normalized.startswith("D"):
        raise ValueError(f"Unsupported dice type: {dice_type}")
    return int(normalized[1:])


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
        self.httpd = None
        self.thread = None
        self.port = 0

    def __enter__(self) -> StaticServer:
        import threading

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


if __name__ == "__main__":
    result = render_dice_gif()
    print(json.dumps(result, ensure_ascii=False))
