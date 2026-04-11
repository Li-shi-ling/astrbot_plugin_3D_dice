# astrbot_plugin_3D_dice

Generate `cs.html` style animated 3D `d6` GIFs inside AstrBot.

## Features

- Reproduces the ivory rounded dice and red pip visual style from `cs.html`
- Uses true 3D cube projection for both browser preview and GIF generation
- Supports one or more `d6` dice in one request, for example `d6`, `2d6`, or `3d6`
- Generates an HTML preview page and a final GIF from the same 3D animation data
- Uses Playwright for browser capture when available
- Falls back to Pillow rendering with the same 3D cube projection when Playwright is unavailable
- Supports deterministic seeds for reproducible rolls
- Supports visual themes: `classic`, `ember`, `emerald`, `midnight`
- Reuses cached GIF outputs for identical requests
- Keeps the plugin runtime fully in Python aside from optional Playwright CLI capture

## Commands

```text
/dice <notation> [theme=<name>] [seed=<int>] [width=<int>] [height=<int>] [fps=<int>] [frames=<int>] [transparent=true|false]
/dice_help
```

Examples:

```text
/dice d6
/dice 2d6 theme=ember
/dice 3d6 seed=42
/dice 2d6 theme=midnight width=640 height=640
```

## Requirements

- AstrBot
- Playwright CLI available as `playwright` for HTML-based frame capture
- Python dependencies from the AstrBot environment, including Pillow

## Configuration

The plugin provides `_conf_schema.json` with these main options:

- `default_width`
- `default_height`
- `default_fps`
- `default_frames`
- `default_theme`
- `max_dice_count`
- `timeout_ms`
- `debug`
- `playwright_path`

## Renderer Architecture

- Python side:
  - Parse dice notation and command options
- Build cs-style `d6` 3D animation data
- Generate a browser preview page from `renderer/preview_template.html`
- Prefer browser-based frame capture through the generated HTML preview
- Fall back to direct Pillow 3D projection drawing if Playwright capture is unavailable
- Cache generated GIF outputs in plugin data storage
- Generate a reference-style HTML preview page beside the cached GIF

## Limitations

- Only `d6` is supported in the current renderer
- The motion is stylized to match `cs.html`, not a full rigid-body physics engine
- Output format is currently GIF only
- Browser-based frame capture depends on local Playwright CLI availability

## Testing

- All tests are written under `tests/`
- Use `pytest` for test execution
- Every new feature must update this `README.md`
- Every new feature must add or update tests and run the affected suite

## Development Rules

- Every new feature must update `README.md`
- Every new feature must add or update pytest tests under `tests/`
- Every new feature must run the related test suite before the work is considered complete
- Project constraints are defined in `CONSTRAINTS.md`
