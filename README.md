# astrbot_plugin_3D_dice

An AstrBot plugin that rolls animated 3D dice and returns the result as a GIF.

## Commands

- `/dice`
- `/dice d20`
- `/dice 3d6`
- `/投骰子 2d8`

Supported dice types: `d4`, `d6`, `d8`, `d20`

## Requirements

- The plugin Python dependencies in `requirements.txt` must be installed
- Playwright for Python must be available
- A local Chromium or Chrome browser must be available, or configure `browser_path`
- The dice web app must exist in `rollmydice_app/`, or configure `site_dir`

## Python runtime

This plugin now renders dice through Playwright for Python and no longer depends on Node.js.

- Install the plugin dependency: `pip install -r requirements.txt`
- If you use Playwright-managed browsers, run `playwright install chromium`
- If you use a system browser such as `/usr/bin/chromium-browser`, set `browser_path`

## Runtime path

The active runtime path is:

- AstrBot command handler -> `main.py`
- Python renderer -> `src/render_dice.py`
- Browser automation -> Playwright for Python

If the repository still contains files such as `render_dice_gif.mjs` or
`node_modules/`, they are leftover artifacts from an earlier prototype and are
not used by the plugin runtime anymore.

## Headless Linux

The renderer supports Linux servers without a desktop environment.

- Recommended: keep `linux_render_mode` set to `auto`; the renderer will try true headless first and fall back to `xvfb` on Linux when WebGL initialization fails
- If your server is known to require a virtual display, install `xvfb` and set `linux_render_mode` to `xvfb`
- The renderer enables software WebGL automatically on Linux (`llvmpipe` + SwiftShader/EGL)

## Optional config

```json
{
  "browser_path": "",
  "site_dir": "",
  "default_duration_ms": 2400,
  "default_fps": 16,
  "linux_render_mode": "auto"
}
```

## Output

The plugin returns a plain-text summary and the rendered GIF in the same reply.

## Third-party assets

The `rollmydice_app` directory contains third-party web assets used only as the local rendering runtime for this plugin.
Keep original attribution and license information when redistributing or modifying those assets.
