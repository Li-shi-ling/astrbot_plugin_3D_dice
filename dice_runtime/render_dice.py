from __future__ import annotations

import asyncio
import base64
import json
import math
import os
import queue
import secrets
import shutil
import socketserver
import subprocess
import sys
import threading
import time
import traceback
from collections.abc import Mapping
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
CONFIGURE_TIMEOUT_MS = 5000
PLAYWRIGHT_INSTALL_TIMEOUT_SECONDS = 600
DEFAULT_CAPTURE_MAX_SIDE = 560
DEFAULT_CAPTURE_VERTICAL_INSET = 32
SESSION_RECYCLE_RENDER_COUNT = 25
XVFB_ENV = "ASTRBOT_3D_DICE_USE_XVFB"
XVFB_ACTIVE_ENV = "ASTRBOT_3D_DICE_XVFB"

# A single persistent browser/page is reused between render requests.
_session_lock = threading.Lock()
_persisted_session: PersistedBrowserSession | None = None
_render_worker_lock = threading.Lock()
_render_worker_process: RenderWorkerProcess | None = None


def run_sync_renderer(function: Any, *args: Any, **kwargs: Any) -> Any:
    try:
        running_loop = asyncio.get_running_loop()
    except RuntimeError:
        running_loop = None

    if running_loop is None or not running_loop.is_running():
        return function(*args, **kwargs)

    result_queue: queue.Queue[tuple[bool, Any]] = queue.Queue(maxsize=1)

    def target() -> None:
        try:
            result_queue.put((True, function(*args, **kwargs)))
        except BaseException as exc:
            result_queue.put((False, exc))

    thread = threading.Thread(target=target, name="astrbot-3d-dice-sync-render")
    thread.start()
    ok, value = result_queue.get()
    thread.join()
    if ok:
        return value
    raise value


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
        self._context: Any = None
        self._page: Any = None
        self._server: StaticServer | None = None
        self._clip: dict[str, int] | None = None
        self._ready = False
        self._render_count = 0
        self.render_lock = threading.Lock()

    def start(self) -> None:
        try:
            sync_playwright = get_sync_playwright()
            self._playwright_ctx = sync_playwright().__enter__()
            self._server = StaticServer(self.site_dir)
            self._server.__enter__()
            base_url = f"http://127.0.0.1:{self._server.port}/index.html"

            self._browser = self._playwright_ctx.chromium.launch(
                executable_path=self.browser_path,
                headless=not is_display_available(),
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
            self._context = self._browser.new_context(
                viewport={"width": self.width, "height": self.height},
                device_scale_factor=1,
            )
            self._page = self._context.new_page()
            self._page.set_default_timeout(self.timeout_ms)
            self._page.set_default_navigation_timeout(self.timeout_ms)
            self._page.goto(
                base_url, wait_until="domcontentloaded", timeout=self.timeout_ms
            )
            wait_for_dice_app(self._page)
            self._clip = get_capture_clip(self._page)
            self._ready = True
        except BaseException:
            self.close()
            raise

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

    def should_recycle_after_render(self) -> bool:
        self._render_count += 1
        return self._render_count >= SESSION_RECYCLE_RENDER_COUNT

    def close(self) -> None:
        self._ready = False
        try:
            if self._page:
                self._page.close()
        except Exception:
            pass
        try:
            if self._context:
                self._context.close()
        except Exception:
            pass
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
        self._context = None
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


def _close_persisted_session_impl() -> None:
    global _persisted_session
    with _session_lock:
        if _persisted_session is not None:
            _persisted_session.close()
            _persisted_session = None


def close_persisted_session() -> None:
    """Close and clear the global persistent browser session."""
    _close_persisted_session_impl()
    close_render_worker()


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
    gif_backend: str = "screenshot",
    ffmpeg_path: str | None = None,
    screencast_quality: int = 80,
    better_render_quality: bool = True,
    parallel_result: bool = False,
    result_timeout_ms: int = DEFAULT_RESULT_TIMEOUT_MS,
    result_mode: str = "physical",
) -> dict[str, Any]:
    return _render_dice_gif_worker(
        dice_type=dice_type,
        count=count,
        duration=duration,
        fps=fps,
        output_name=output_name,
        browser=browser,
        output_dir=output_dir,
        site_dir=site_dir,
        width=width,
        height=height,
        gif_backend=gif_backend,
        ffmpeg_path=ffmpeg_path,
        screencast_quality=screencast_quality,
        better_render_quality=better_render_quality,
        parallel_result=parallel_result,
        result_timeout_ms=result_timeout_ms,
        result_mode=result_mode,
    )


def prewarm_render_worker(
    browser: str | None = None,
    site_dir: Path | None = None,
    width: int = 900,
    height: int = 1400,
) -> None:
    """Start the persistent worker and load the dice page before the first roll."""
    worker = get_render_worker()
    try:
        worker.prewarm(browser=browser, site_dir=site_dir, width=width, height=height)
    except RenderWorkerRequestError:
        raise
    except Exception:
        close_render_worker()
        get_render_worker().prewarm(
            browser=browser, site_dir=site_dir, width=width, height=height
        )


class RenderWorkerProcess:
    """Persistent render subprocess that owns Playwright and Chromium."""

    def __init__(self) -> None:
        self.process: subprocess.Popen[str] | None = None
        self.lock = threading.Lock()

    def render(self, **kwargs: Any) -> dict[str, Any]:
        with self.lock:
            self.start()
            try:
                return self._send_request("render", kwargs)
            except RenderWorkerRequestError:
                raise
            except Exception:
                self.close()
                raise

    def prewarm(self, **kwargs: Any) -> None:
        with self.lock:
            self.start()
            try:
                self._send_request("prewarm", kwargs)
            except RenderWorkerRequestError:
                raise
            except Exception:
                self.close()
                raise

    def start(self) -> None:
        if self.process is not None and self.process.poll() is None:
            return
        self.close()
        command, env = build_render_worker_command()
        self.process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            env=env,
            text=True,
            bufsize=1,
        )

    def close(self) -> None:
        process = self.process
        self.process = None
        if process is None:
            return
        try:
            if process.stdin:
                process.stdin.close()
        except Exception:
            pass
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)

    def _send_request(self, action: str, kwargs: dict[str, Any]) -> dict[str, Any]:
        if (
            self.process is None
            or self.process.stdin is None
            or self.process.stdout is None
        ):
            raise RuntimeError("3D dice render worker is not running")

        payload = {
            "action": action,
            "options": {
                key: str(value) if isinstance(value, Path) else value
                for key, value in kwargs.items()
            },
        }
        self.process.stdin.write(json.dumps(payload, ensure_ascii=False) + "\n")
        self.process.stdin.flush()

        response = read_worker_json_response(self.process.stdout)
        if response.get("ok"):
            return response["result"]
        error = str(response.get("error") or "3D dice render worker failed")
        details = str(response.get("traceback") or "").strip()
        raise RenderWorkerRequestError(f"{error}\n{details}".strip())


class RenderWorkerRequestError(RuntimeError):
    """Render failed inside a healthy worker process."""


def build_render_worker_command() -> tuple[list[str], dict[str, str]]:
    command = [sys.executable, str(Path(__file__).resolve()), "--worker-json"]
    env = os.environ.copy()
    xvfb_mode = env.get(XVFB_ENV, "auto").strip().lower()

    if xvfb_mode in {"0", "false", "no", "off", "never"}:
        return command, env
    if env.get(XVFB_ACTIVE_ENV) or not is_xvfb_supported_platform():
        return command, env
    if is_display_available(env) and xvfb_mode != "true":
        return command, env

    xvfb_run = shutil.which("xvfb-run")
    if not xvfb_run:
        if xvfb_mode == "true":
            raise FileNotFoundError("xvfb-run was requested but was not found in PATH")
        return command, env

    env[XVFB_ACTIVE_ENV] = "1"
    return [xvfb_run, "-a", *command], env


def is_xvfb_supported_platform() -> bool:
    return os.name != "nt" and sys.platform != "darwin"


def _parse_display_number(display: str) -> int | None:
    display = display.strip()
    if not display:
        return None
    if ":" in display:
        display = display.split(":")[-1]
    if "." in display:
        display = display.split(".")[0]
    try:
        return int(display)
    except ValueError:
        return None


def _is_display_available(env: Mapping[str, str], x11_dir: Path) -> bool:
    display = env.get("DISPLAY", "").strip()
    if not display:
        return False
    if os.name == "nt":
        return True
    if not x11_dir.exists():
        return False
    display_number = _parse_display_number(display)
    if display_number is not None:
        return (x11_dir / f"X{display_number}").exists()
    return any(child.name.startswith("X") for child in x11_dir.iterdir())


def is_display_available(env: Mapping[str, str] | None = None) -> bool:
    return _is_display_available(env or os.environ, Path("/tmp/.X11-unix"))


def read_worker_json_response(stdout: Any) -> dict[str, Any]:
    while True:
        line = stdout.readline()
        if not line:
            raise RuntimeError(
                "3D dice render worker stopped before returning a result"
            )
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            continue


def _render_dice_gif_worker(**kwargs: Any) -> dict[str, Any]:
    worker = get_render_worker()
    try:
        return worker.render(**kwargs)
    except RenderWorkerRequestError:
        raise
    except Exception:
        # Retry once with a fresh worker in case the persistent subprocess died.
        close_render_worker()
        return get_render_worker().render(**kwargs)


def get_render_worker() -> RenderWorkerProcess:
    global _render_worker_process
    with _render_worker_lock:
        if _render_worker_process is None:
            _render_worker_process = RenderWorkerProcess()
        return _render_worker_process


def close_render_worker() -> None:
    global _render_worker_process
    with _render_worker_lock:
        if _render_worker_process is not None:
            _render_worker_process.close()
            _render_worker_process = None


def _render_dice_gif_subprocess(**kwargs: Any) -> dict[str, Any]:
    payload = {
        key: str(value) if isinstance(value, Path) else value
        for key, value in kwargs.items()
    }
    completed = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve()),
            "--render-json",
            json.dumps(payload, ensure_ascii=False),
        ],
        capture_output=True,
        check=False,
        text=True,
        timeout=180,
    )
    if completed.returncode != 0:
        output = "\n".join(
            part.strip()
            for part in (completed.stdout, completed.stderr)
            if part and part.strip()
        )
        raise RuntimeError(output or "3D dice render subprocess failed")

    lines = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    if not lines:
        raise RuntimeError("3D dice render subprocess did not return a result")
    return json.loads(lines[-1])


def _render_dice_gif_impl(
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
    gif_backend: str = "screenshot",
    ffmpeg_path: str | None = None,
    screencast_quality: int = 80,
    better_render_quality: bool = True,
    parallel_result: bool = False,
    result_timeout_ms: int = DEFAULT_RESULT_TIMEOUT_MS,
    result_mode: str = "physical",
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
    gif_backend = str(gif_backend or "screenshot").strip().lower()

    if not site_dir.exists():
        raise FileNotFoundError(f"Site directory not found: {site_dir}")
    if not browser_path:
        raise FileNotFoundError(
            "Could not find a local Chromium/Chrome/Edge executable. Pass browser=..."
        )
    if gif_backend not in {
        "screenshot",
        "webm_ffmpeg",
        "cdp_screencast",
        "cdp_screencast_limited",
        "cdp_screencast_ffmpeg",
    }:
        raise ValueError(f"Unsupported GIF backend: {gif_backend}")

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
        baseline_frame: Image.Image | None = None
        frames: list[Image.Image] = []
        recycle_session = False

        try:
            cleanup_page_render_artifacts(page)
            configure_dice(page, dice_type=dice_type, dice_count=count)
            if better_render_quality:
                wait_for_stable_render(page, clip)
            baseline_frame = capture_clip_png(page, clip)

            if gif_backend == "webm_ffmpeg":
                resolved_ffmpeg = find_ffmpeg_path(ffmpeg_path)
                if not resolved_ffmpeg:
                    raise FileNotFoundError(
                        "ffmpeg was not found. Set ffmpeg_path or add ffmpeg to PATH."
                    )
                recording_duration = max(duration, 1200)
                start_webm_recording(
                    page, clip=clip, fps=fps, duration=recording_duration
                )
                trigger_roll(page)
                if better_render_quality:
                    wait_for_roll_start(page, clip, baseline_frame)
                else:
                    wait_for_animation_start(page, clip, baseline_frame, 2000)
                try:
                    webm_data = finish_webm_recording(page)
                finally:
                    cleanup_page_render_artifacts(page)
                webm_path = output_path.with_suffix(".webm")
                write_webm_file(webm_data, webm_path)
                webm_data.clear()
                try:
                    convert_webm_to_gif(
                        webm_path=webm_path,
                        output_path=output_path,
                        fps=fps,
                        ffmpeg_path=resolved_ffmpeg,
                    )
                finally:
                    webm_path.unlink(missing_ok=True)
            elif gif_backend in {"cdp_screencast", "cdp_screencast_limited"}:
                trigger_roll(page)
                if better_render_quality:
                    wait_for_roll_start(page, clip, baseline_frame)
                else:
                    wait_for_animation_start(page, clip, baseline_frame, 2000)
                frames = capture_screencast_frames(
                    page=page,
                    clip=clip,
                    duration=duration,
                    fps=fps,
                    width=width,
                    height=height,
                    quality=screencast_quality,
                    limit_to_fps=gif_backend == "cdp_screencast_limited",
                )
                write_gif(frames, output_path, frame_delay)
            elif gif_backend == "cdp_screencast_ffmpeg":
                resolved_ffmpeg = find_ffmpeg_path(ffmpeg_path)
                if not resolved_ffmpeg:
                    raise FileNotFoundError(
                        "ffmpeg was not found. Set ffmpeg_path or add ffmpeg to PATH."
                    )
                trigger_roll(page)
                if better_render_quality:
                    wait_for_roll_start(page, clip, baseline_frame)
                else:
                    wait_for_animation_start(page, clip, baseline_frame, 2000)
                capture_screencast_gif_ffmpeg(
                    page=page,
                    clip=clip,
                    output_path=output_path,
                    duration=duration,
                    fps=fps,
                    width=width,
                    height=height,
                    quality=screencast_quality,
                    ffmpeg_path=resolved_ffmpeg,
                )
            else:
                trigger_roll(page)
                if better_render_quality:
                    wait_for_roll_start(page, clip, baseline_frame)
                else:
                    wait_for_animation_start(page, clip, baseline_frame, 2000)
                frames = capture_frames(page, clip, total_frames, frame_delay)
                write_gif(frames, output_path, frame_delay)

            if not parallel_result:
                page.wait_for_timeout(max(2500, duration))
            result = resolve_roll_results(
                page=page,
                dice_count=count,
                dice_type=dice_type,
                result_mode=result_mode,
                result_timeout_ms=result_timeout_ms,
            )

        except Exception:
            # Rebuild the persistent page on the next request after any page error.
            _close_persisted_session_impl()
            raise
        finally:
            if baseline_frame is not None:
                baseline_frame.close()
            close_images(frames)
            cleanup_page_render_artifacts(page)
            recycle_session = session.should_recycle_after_render()

    if recycle_session:
        _close_persisted_session_impl()

    return {
        "gif_path": str(output_path),
        "results": result["results"],
        "total": result["total"],
        "dice_type": dice_type,
        "dice_count": count,
        "gif_backend": gif_backend,
        "fallback": bool(result.get("fallback", False)),
        "partial": bool(result.get("partial", False)),
    }


def default_output_name(dice_type: str, count: int) -> str:
    return f"{dice_type.lower()}-{count}-{int(time.time() * 1000)}.gif"


def detect_browser_path() -> str | None:
    env_candidates = [
        os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH"),
        os.environ.get("PUPPETEER_EXECUTABLE_PATH"),
        os.environ.get("BROWSER"),
        os.environ.get("CHROME_BIN"),
    ]
    for candidate in env_candidates:
        if is_usable_browser_candidate(candidate):
            return candidate

    playwright_browser = detect_playwright_chromium_path()
    if is_usable_browser_candidate(playwright_browser):
        return playwright_browser

    for candidate in system_browser_candidates():
        if is_usable_browser_candidate(candidate):
            return candidate
    return None


def is_usable_browser_candidate(candidate: str | None) -> bool:
    if not candidate:
        return False
    path = Path(candidate)
    return path.exists() and not is_browser_wrapper(candidate)


def is_browser_wrapper(candidate: str | None) -> bool:
    if not candidate:
        return False
    path = Path(candidate)
    try:
        resolved = path.resolve()
    except OSError:
        return False
    return path.name in {"chromium", "chromium-browser"} and resolved.name == "snap"


def system_browser_candidates() -> list[str]:
    program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
    program_files_x86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    return [
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
    """缁涘绶熸鏉跨摍瀵偓婵绻嶉崝銊ユ倵閸愬秴缍嶉崚璺烘姎閿涘牆缂撶拋顔兼磽閺囧じ鍞弬瑙勵攳閿涘鈧?

    閸樼喐娼?better_render_quality=True 閺冨墎娲块幒?wait_for_timeout(140)閿?
    鏉╂瑩鍣烽弨閫涜礋娑撹濮╁Λ鈧ù瀣暰闂堛垹褰夐崠鏍电礉妤犳澘鐡欐稉鈧崝銊ユ皑缁斿宓嗗鈧慨瀣秿閸掕绱?
    閺冾澀绗夋导姘礈閸ュ搫鐣惧鎯扮箿濠曞繑甯€鐠у嘲顫愮敮褝绱濇稊鐔剁瑝娴兼艾婀幈銏も偓鐔告簚閸ｃ劋绗傛潻鍥ㄦ－閹搭亜娴橀妴?
    """
    deadline = time.time() + (max_wait_ms / 1000.0)
    while time.time() < deadline:
        current_frame = capture_clip_png(page, clip)
        if count_changed_pixels(baseline_frame, current_frame) > 10:
            return
        page.wait_for_timeout(30)
    # 鐡掑懏妞傛稊鐔烘埛缂侇叏绱濇稉宥嗗瀵倸鐖堕敍鍫ヮ€忕€涙劕褰查懗钘夊嚒缂佸繐婀潻鎰З娴滃棴绱?


def configure_dice(page: Any, dice_type: str, dice_count: int) -> None:
    current_dice_type = page.evaluate(
        """
        () => {
          const button = [...document.querySelectorAll('button')].find(
            (candidate) => /^D\\d+$/i.test((candidate.textContent || '').trim())
          );
          return (button?.textContent || '').trim();
        }
        """
    )

    if current_dice_type != dice_type:
        page.evaluate(
            """
            () => {
              const buttons = [...document.querySelectorAll('button')];
              const dieButton = buttons.find((button) => /^D\\d+$/i.test((button.textContent || '').trim()));
              if (dieButton) {
                dieButton.click();
              }
            }
            """
        )
        page.wait_for_function(
            """
            (label) => {
              const buttons = [...document.querySelectorAll('button')];
              return buttons.some((button) => (button.textContent || '').trim() === label);
            }
            """,
            arg=dice_type,
            timeout=CONFIGURE_TIMEOUT_MS,
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
            timeout=CONFIGURE_TIMEOUT_MS,
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
        timeout=CONFIGURE_TIMEOUT_MS,
    )
    page.wait_for_timeout(300)


def get_capture_clip(page: Any) -> dict[str, int]:
    clip = page.evaluate(
        """
        ({ captureMaxSide, verticalInset }) => {
          const canvases = [...document.querySelectorAll('canvas')];
          const canvas = canvases.find((candidate) => {
            const rect = candidate.getBoundingClientRect();
            return rect.width > 200 && rect.height > 100;
          }) || canvases[0];
          if (!canvas) return null;

          const rect = canvas.getBoundingClientRect();
          const buttons = [...document.querySelectorAll('button')];
          const rollButton = buttons.find((button) => /roll/i.test(button.textContent || ''));
          const rollTop = rollButton ? rollButton.getBoundingClientRect().top : window.innerHeight;
          const topControlBottom = buttons
            .filter((button) => !/roll/i.test(button.textContent || ''))
            .reduce((bottom, button) => Math.max(bottom, button.getBoundingClientRect().bottom), 0);

          const maxSide = Math.max(1, Math.min(window.innerWidth, window.innerHeight, captureMaxSide));
          const desiredSide = Math.max(rect.width, rect.height, 520);
          const side = Math.floor(Math.min(maxSide, desiredSide));
          const height = Math.max(1, side - (verticalInset * 2));
          const centeredY = rect.top + (rect.height / 2) - (height / 2);
          const minY = Math.max(0, Math.floor(topControlBottom + 8));
          const maxY = Math.max(0, Math.floor(rollTop - height - 8));
          const y = maxY >= minY
            ? Math.min(Math.max(centeredY, minY), maxY)
            : Math.max(0, Math.min(centeredY, window.innerHeight - height));
          const centeredX = rect.left + (rect.width / 2) - (side / 2);
          const x = Math.max(0, Math.min(centeredX, window.innerWidth - side));

          return {
            x: Math.floor(x),
            y: Math.floor(y),
            width: side,
            height,
          };
        }
        """,
        {
            "captureMaxSide": DEFAULT_CAPTURE_MAX_SIDE,
            "verticalInset": DEFAULT_CAPTURE_VERTICAL_INSET,
        },
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
    image = Image.open(BytesIO(png_bytes))
    try:
        return image.convert("RGBA")
    finally:
        image.close()


def close_images(images: list[Image.Image]) -> None:
    while images:
        image = images.pop()
        try:
            image.close()
        except Exception:
            pass


def count_changed_pixels(before: Image.Image, after: Image.Image) -> int:
    before_rgba = before.convert("RGBA")
    after_rgba = after.convert("RGBA")
    diff = ImageChops.difference(before_rgba, after_rgba)
    alpha = diff.convert("L")
    try:
        return sum(1 for pixel in alpha.getdata() if pixel)
    finally:
        alpha.close()
        diff.close()
        after_rgba.close()
        before_rgba.close()


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

    try:
        while time.time() < deadline:
            page.wait_for_timeout(interval_ms)
            current_frame = capture_clip_png(page, clip)
            changed_pixels = count_changed_pixels(previous_frame, current_frame)
            previous_frame.close()
            if changed_pixels <= changed_pixel_tolerance:
                stable_count += 1
                if stable_count >= stable_samples:
                    current_frame.close()
                    return
            else:
                stable_count = 0
            previous_frame = current_frame
    finally:
        previous_frame.close()


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
        try:
            if count_changed_pixels(baseline_frame, current_frame) > 0:
                return
        finally:
            current_frame.close()
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


def capture_screencast_frames(
    page: Any,
    clip: dict[str, int],
    duration: int,
    fps: int,
    width: int,
    height: int,
    quality: int = 80,
    limit_to_fps: bool = False,
) -> list[Image.Image]:
    client = page.context.new_cdp_session(page)
    encoded_frames: list[str] = []
    target_interval = 1 / max(1, int(fps))
    last_kept_timestamp: float | None = None

    def handle_frame(event: dict[str, Any]) -> None:
        session_id = event.get("sessionId")
        if session_id is not None:
            client.send("Page.screencastFrameAck", {"sessionId": session_id})
        data = event.get("data")
        if not data:
            return
        if limit_to_fps:
            nonlocal last_kept_timestamp
            timestamp = get_screencast_timestamp(event)
            if (
                timestamp is not None
                and last_kept_timestamp is not None
                and timestamp - last_kept_timestamp < target_interval
            ):
                return
            last_kept_timestamp = timestamp
        encoded_frames.append(str(data))

    client.on("Page.screencastFrame", handle_frame)
    client.send(
        "Page.startScreencast",
        {
            "format": "jpeg",
            "quality": int(quality),
            "maxWidth": int(width),
            "maxHeight": int(height),
            "everyNthFrame": 1,
        },
    )
    try:
        page.wait_for_timeout(max(100, int(duration)))
    finally:
        try:
            client.send("Page.stopScreencast")
        finally:
            client.detach()

    if not encoded_frames:
        raise RuntimeError("CDP screencast returned no frames")

    target_count = max(1, math.ceil(duration / max(20, round(1000 / max(1, fps)))))
    selected_frames = sample_evenly(encoded_frames, target_count)
    viewport = {"width": int(width), "height": int(height)}
    return [
        decode_and_crop_screencast_frame(encoded_frame, clip=clip, viewport=viewport)
        for encoded_frame in selected_frames
    ]


def get_screencast_timestamp(event: dict[str, Any]) -> float | None:
    metadata = event.get("metadata")
    if not isinstance(metadata, dict):
        return None
    value = metadata.get("timestamp")
    if isinstance(value, int | float):
        return float(value)
    return None


def capture_screencast_gif_ffmpeg(
    page: Any,
    clip: dict[str, int],
    output_path: Path,
    duration: int,
    fps: int,
    width: int,
    height: int,
    quality: int,
    ffmpeg_path: str,
) -> None:
    process = start_screencast_ffmpeg_process(
        output_path=output_path,
        clip=clip,
        fps=fps,
        ffmpeg_path=ffmpeg_path,
    )
    client = page.context.new_cdp_session(page)
    target_interval = 1 / max(1, int(fps))
    last_kept_timestamp: float | None = None
    frames_written = 0

    def handle_frame(event: dict[str, Any]) -> None:
        nonlocal frames_written, last_kept_timestamp
        session_id = event.get("sessionId")
        if session_id is not None:
            client.send("Page.screencastFrameAck", {"sessionId": session_id})
        data = event.get("data")
        if not data or process.stdin is None or process.poll() is not None:
            return
        timestamp = get_screencast_timestamp(event)
        if (
            timestamp is not None
            and last_kept_timestamp is not None
            and timestamp - last_kept_timestamp < target_interval
        ):
            return
        last_kept_timestamp = timestamp
        try:
            process.stdin.write(base64.b64decode(str(data)))
            process.stdin.flush()
            frames_written += 1
        except BrokenPipeError:
            return

    client.on("Page.screencastFrame", handle_frame)
    client.send(
        "Page.startScreencast",
        {
            "format": "jpeg",
            "quality": int(quality),
            "maxWidth": int(width),
            "maxHeight": int(height),
            "everyNthFrame": 1,
        },
    )
    try:
        page.wait_for_timeout(max(100, int(duration)))
    finally:
        try:
            client.send("Page.stopScreencast")
        finally:
            client.detach()
        if process.stdin:
            process.stdin.close()

    try:
        process.wait(timeout=120)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)
    stdout = process.stdout.read().decode(errors="replace") if process.stdout else ""
    stderr = process.stderr.read().decode(errors="replace") if process.stderr else ""
    if frames_written <= 0:
        raise RuntimeError("CDP screencast returned no frames for ffmpeg")
    if process.returncode != 0:
        output = "\n".join(
            part.strip() for part in (stdout, stderr) if part and part.strip()
        )
        raise RuntimeError(f"ffmpeg failed to encode CDP screencast GIF: {output}")
    if not output_path.exists() or output_path.stat().st_size <= 0:
        raise RuntimeError("ffmpeg did not create a CDP screencast GIF output")


def start_screencast_ffmpeg_process(
    output_path: Path,
    clip: dict[str, int],
    fps: int,
    ffmpeg_path: str,
) -> subprocess.Popen[bytes]:
    crop_filter = (
        f"crop={int(clip['width'])}:{int(clip['height'])}:"
        f"{int(clip['x'])}:{int(clip['y'])}"
    )
    return subprocess.Popen(
        [
            ffmpeg_path,
            "-y",
            "-loglevel",
            "error",
            "-f",
            "image2pipe",
            "-framerate",
            str(max(1, int(fps))),
            "-vcodec",
            "mjpeg",
            "-i",
            "pipe:0",
            "-vf",
            crop_filter,
            "-loop",
            "0",
            str(output_path),
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def sample_evenly(items: list[str], target_count: int) -> list[str]:
    if len(items) <= target_count:
        return items
    if target_count <= 1:
        return [items[0]]
    step = (len(items) - 1) / (target_count - 1)
    return [items[round(index * step)] for index in range(target_count)]


def decode_screencast_frame(encoded_frame: str) -> Image.Image:
    frame_bytes = base64.b64decode(encoded_frame)
    image = Image.open(BytesIO(frame_bytes))
    try:
        return image.convert("RGBA")
    finally:
        image.close()


def decode_and_crop_screencast_frame(
    encoded_frame: str, clip: dict[str, int], viewport: dict[str, int]
) -> Image.Image:
    decoded = decode_screencast_frame(encoded_frame)
    cropped: Image.Image | None = None
    try:
        cropped = crop_screencast_frame(decoded, clip=clip, viewport=viewport)
        if cropped is decoded:
            return decoded.copy()
        return cropped.copy()
    finally:
        decoded.close()
        if cropped is not None and cropped is not decoded:
            cropped.close()


def crop_screencast_frame(
    image: Image.Image, clip: dict[str, int], viewport: dict[str, int]
) -> Image.Image:
    scale_x = image.width / max(1, int(viewport["width"]))
    scale_y = image.height / max(1, int(viewport["height"]))
    left = max(0, int(round(clip["x"] * scale_x)))
    top = max(0, int(round(clip["y"] * scale_y)))
    right = min(image.width, int(round((clip["x"] + clip["width"]) * scale_x)))
    bottom = min(image.height, int(round((clip["y"] + clip["height"]) * scale_y)))
    if right <= left or bottom <= top:
        return image
    return image.crop((left, top, right, bottom))


def find_ffmpeg_path(explicit_path: str | None = None) -> str | None:
    if explicit_path:
        candidate = Path(explicit_path)
        if candidate.exists():
            return str(candidate)
        return explicit_path if shutil.which(explicit_path) else None
    return shutil.which(os.environ.get("FFMPEG_BINARY", "ffmpeg"))


def cleanup_page_render_artifacts(page: Any) -> None:
    try:
        page.evaluate(
            """
            () => {
              if (typeof globalThis.__astrbotWebmCleanup === 'function') {
                try {
                  globalThis.__astrbotWebmCleanup();
                } catch (_) {}
              }
              delete globalThis.__astrbotWebmCleanup;
              delete globalThis.__astrbotWebmPromise;
              delete globalThis.__astrbotWebmState;
            }
            """
        )
    except Exception:
        pass


def start_webm_recording(
    page: Any, clip: dict[str, int], fps: int, duration: int
) -> None:
    page.evaluate(
        """
        ({ clip, fps, duration }) => {
          if (typeof globalThis.__astrbotWebmCleanup === 'function') {
            globalThis.__astrbotWebmCleanup();
          }
          delete globalThis.__astrbotWebmPromise;
          delete globalThis.__astrbotWebmState;

          const canvas = [...document.querySelectorAll('canvas')]
            .find((item) => {
              const rect = item.getBoundingClientRect();
              return rect.width > 100 && rect.height > 100;
            });
          if (!canvas) {
            throw new Error('Dice canvas not found');
          }
          if (typeof canvas.captureStream !== 'function') {
            throw new Error('Canvas captureStream is not supported');
          }
          if (typeof MediaRecorder === 'undefined') {
            throw new Error('MediaRecorder is not supported');
          }

          const stream = canvas.captureStream(fps);
          const videoTrack = stream.getVideoTracks()[0];
          const mimeTypes = [
            'video/webm;codecs=vp8',
            'video/webm',
            'video/webm;codecs=vp9',
          ];
          const mimeType = mimeTypes.find((item) => MediaRecorder.isTypeSupported(item));
          const recorder = new MediaRecorder(
            stream,
            mimeType ? { mimeType } : undefined,
          );
          const chunks = [];
          let frameTimer = null;
          globalThis.__astrbotWebmState = { recorder, stream, chunks };
          globalThis.__astrbotWebmCleanup = () => {
            if (frameTimer !== null) {
              clearInterval(frameTimer);
              frameTimer = null;
            }
            stream.getTracks().forEach((track) => {
              try {
                track.stop();
              } catch (_) {}
            });
            chunks.length = 0;
            delete globalThis.__astrbotWebmState;
          };

          globalThis.__astrbotWebmPromise = new Promise((resolve, reject) => {
            recorder.ondataavailable = (event) => {
              if (event.data && event.data.size > 0) {
                chunks.push(event.data);
              }
            };
            recorder.onerror = (event) => {
              reject(new Error(event.error?.message || 'WebM recording failed'));
            };
            recorder.onstop = async () => {
              try {
                if (frameTimer !== null) {
                  clearInterval(frameTimer);
                  frameTimer = null;
                }
                stream.getTracks().forEach((track) => track.stop());
                const blob = new Blob(chunks, { type: recorder.mimeType || 'video/webm' });
                const buffer = await blob.arrayBuffer();
                const bytes = new Uint8Array(buffer);
                chunks.length = 0;
                let binary = '';
                const chunkSize = 0x8000;
                for (let index = 0; index < bytes.length; index += chunkSize) {
                  binary += String.fromCharCode(...bytes.subarray(index, index + chunkSize));
                }
                resolve({
                  base64: btoa(binary),
                  byteLength: bytes.length,
                  mimeType: blob.type,
                  width: canvas.width,
                  height: canvas.height,
                });
                delete globalThis.__astrbotWebmState;
              } catch (error) {
                reject(error);
              }
            };
          });

          recorder.start(100);
          if (videoTrack && typeof videoTrack.requestFrame === 'function') {
            frameTimer = setInterval(
              () => videoTrack.requestFrame(),
              Math.max(20, Math.round(1000 / Math.max(1, fps))),
            );
            videoTrack.requestFrame();
          }
          setTimeout(() => {
            if (recorder.state !== 'inactive') {
              if (typeof recorder.requestData === 'function') {
                recorder.requestData();
              }
              recorder.stop();
            }
          }, Math.max(100, duration));
        }
        """,
        {"clip": clip, "fps": int(fps), "duration": int(duration)},
    )


def finish_webm_recording(page: Any) -> dict[str, Any]:
    data = page.evaluate(
        """
        () => {
          if (!globalThis.__astrbotWebmPromise) {
            throw new Error('WebM recording was not started');
          }
          return globalThis.__astrbotWebmPromise;
        }
        """
    )
    if not data or not data.get("base64"):
        raise RuntimeError("WebM recording returned no data")
    return data


def write_webm_file(webm_data: dict[str, Any], webm_path: Path) -> None:
    content = base64.b64decode(str(webm_data["base64"]))
    if not content:
        raise RuntimeError("WebM recording was empty")
    webm_path.write_bytes(content)


def convert_webm_to_gif(
    webm_path: Path,
    output_path: Path,
    fps: int,
    ffmpeg_path: str,
) -> None:
    palette_filter = (
        f"fps={max(1, int(fps))},"
        "split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse=dither=bayer"
    )
    completed = run_ffmpeg(
        command=[
            ffmpeg_path,
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(webm_path),
            "-filter_complex",
            palette_filter,
            "-loop",
            "0",
            str(output_path),
        ],
    )
    if completed.returncode != 0 and "palettegen" in (
        completed.stdout + completed.stderr
    ):
        completed = run_ffmpeg(
            command=[
                ffmpeg_path,
                "-y",
                "-loglevel",
                "error",
                "-i",
                str(webm_path),
                "-vf",
                f"fps={max(1, int(fps))}",
                "-loop",
                "0",
                str(output_path),
            ],
        )
    if completed.returncode != 0:
        output = "\n".join(
            part.strip()
            for part in (completed.stdout, completed.stderr)
            if part and part.strip()
        )
        raise RuntimeError(f"ffmpeg failed to convert WebM to GIF: {output}")
    if not output_path.exists() or output_path.stat().st_size <= 0:
        raise RuntimeError("ffmpeg did not create a GIF output")


def run_ffmpeg(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        capture_output=True,
        check=False,
        text=True,
        timeout=120,
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


def resolve_roll_results(
    page: Any,
    dice_count: int,
    dice_type: str,
    result_mode: str,
    result_timeout_ms: int,
) -> dict[str, Any]:
    mode = str(result_mode or "physical").strip().lower()
    if mode == "fast":
        snapshot = read_roll_result_snapshot(page)
        parsed = parse_roll_result_snapshot(snapshot, dice_count, dice_type)
        if parsed:
            return parsed
        return make_fallback_roll_result(dice_count, dice_type)
    return read_roll_results(
        page,
        dice_count,
        dice_type,
        timeout_ms=result_timeout_ms,
        fallback_random=True,
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


def _normalize_render_options(options: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(options)
    for path_key in ("output_dir", "site_dir"):
        if normalized.get(path_key):
            normalized[path_key] = Path(normalized[path_key])
    return normalized


def _prewarm_render_impl(
    browser: str | None = None,
    site_dir: Path | None = None,
    width: int = 900,
    height: int = 1400,
) -> dict[str, Any]:
    site_dir = Path(site_dir or (PROJECT_DIR / "dice_roller_app")).resolve()
    browser_path = browser or detect_browser_path()
    if not site_dir.exists():
        raise FileNotFoundError(f"Site directory not found: {site_dir}")
    if not browser_path:
        raise FileNotFoundError(
            "Could not find a local Chromium/Chrome/Edge executable. Pass browser=..."
        )
    session = get_persisted_session(
        browser_path=browser_path,
        site_dir=site_dir,
        width=width,
        height=height,
        timeout_ms=DEFAULT_TIMEOUT_MS,
    )
    return {"ready": session.is_alive()}


def _render_worker_loop() -> None:
    try:
        for line in sys.stdin:
            if not line.strip():
                continue
            try:
                request = json.loads(line)
                action = request.get("action", "render")
                options = _normalize_render_options(request.get("options", request))
                if action == "prewarm":
                    result = run_sync_renderer(_prewarm_render_impl, **options)
                elif action == "render":
                    result = run_sync_renderer(_render_dice_gif_impl, **options)
                else:
                    raise ValueError(f"Unsupported render worker action: {action}")
                response = {"ok": True, "result": result}
            except BaseException as exc:
                response = {
                    "ok": False,
                    "error": str(exc),
                    "traceback": traceback.format_exc(),
                }
            print(json.dumps(response, ensure_ascii=False), flush=True)
    finally:
        _close_persisted_session_impl()


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "--worker-json":
        _render_worker_loop()
    elif len(sys.argv) >= 3 and sys.argv[1] == "--render-json":
        options = _normalize_render_options(json.loads(sys.argv[2]))
        try:
            result = _render_dice_gif_impl(**options)
        finally:
            _close_persisted_session_impl()
        print(json.dumps(result, ensure_ascii=False))
    else:
        result = render_dice_gif()
        print(json.dumps(result, ensure_ascii=False))
