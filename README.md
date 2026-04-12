# astrbot_plugin_3D_dice

An AstrBot plugin that rolls animated 3D dice and returns the result as a GIF.

## Commands

- `/dice`
- `/dice d20`
- `/dice 3d6`
- `/投骰子 2d8`

Supported dice types: `d4`, `d6`, `d8`, `d20`

## Requirements

- `node` must be available in `PATH`
- The npm dependencies in `package.json` must be installed
- A local Edge or Chrome browser must be available, or configure `browser_path`
- The dice web app must exist in `rollmydice_app/`, or configure `site_dir`

## Headless Linux

The renderer supports Linux servers without a desktop environment.

- Recommended: install `chromium` or `google-chrome` and keep `linux_render_mode` set to `headless`
- Fallback: use `linux_render_mode: "xvfb"` only if your Chromium build cannot render WebGL in true headless mode
- The renderer enables software WebGL automatically on Linux (`llvmpipe` + SwiftShader/EGL)

## Optional config

```json
{
  "browser_path": "",
  "site_dir": "",
  "default_duration_ms": 2400,
  "default_fps": 16,
  "linux_render_mode": "headless"
}
```

## Output

The plugin returns a plain-text summary and the rendered GIF in the same reply.

## Third-party assets

The `rollmydice_app` directory contains third-party web assets used only as the local rendering runtime for this plugin.
Keep original attribution and license information when redistributing or modifying those assets.
