# astrbot_plugin_3D_dice

Generate animated 3D dice GIFs inside AstrBot.

## Features

- Supports `d4`, `d6`, `d8`, `d10`, `d12`, `d20`, and `d100`
- Supports multiple dice in one request, for example `2d6` or `d20+d4`
- Uses a local Node.js renderer to simulate motion and output frame data
- Uses Pillow on the Python side to assemble the final GIF
- Supports deterministic seeds for reproducible rolls
- Supports visual themes: `classic`, `ember`, `emerald`, `midnight`

## Commands

```text
/dice <notation> [theme=<name>] [seed=<int>] [width=<int>] [height=<int>] [fps=<int>] [frames=<int>] [transparent=true|false]
/dice_help
```

Examples:

```text
/dice d20
/dice 2d6 theme=ember
/dice d20+d4 seed=42
/dice 1d100 theme=midnight width=640 height=640
```

## Requirements

- AstrBot
- Node.js 22+ available as `node`, or configure `node_path` in WebUI
- Python dependencies from the AstrBot environment, including Pillow

## Configuration

The plugin provides `_conf_schema.json` with these main options:

- `node_path`
- `default_width`
- `default_height`
- `default_fps`
- `default_frames`
- `default_theme`
- `max_dice_count`
- `timeout_ms`
- `debug`

## Renderer Architecture

- Python side:
  - Parse dice notation and command options
  - Invoke the local Node.js renderer
  - Draw the returned frame data into a GIF
  - Cache generated GIF outputs in plugin data storage
- Node.js side:
  - Build polyhedron geometry for each supported die type
  - Run a lightweight physics-style simulation
  - Project faces into 2D screen space
  - Return polygon and label data for each frame

## Limitations

- v1 uses a dependency-free Node.js renderer instead of a browser-based Three.js pipeline
- Multi-dice collisions are approximate
- Face text is drawn for readability, not true face texture projection
- Output format is currently GIF only

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
