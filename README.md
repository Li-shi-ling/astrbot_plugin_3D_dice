# AstrBot 3D Dice

Roll animated 3D dice in AstrBot and return the final GIF plus parsed result.

## Commands

- `/3d_dice`
- `/3d_dice D20 2`
- `/3d_dice 2D6`
- `/投骰子 D8 3`
- `/3d_dice_help`

Supported dice: `D4`, `D6`, `D8`, `D20`.

## Runtime

The renderer uses the bundled `rollmydice_app` static site, Playwright, and a local Chromium/Chrome/Edge executable. Set `browser` in the plugin config if auto-detection cannot find a browser.

## Tests

Run plugin tests with:

```powershell
'F:\anaconda\condabin\conda.bat' run -n AstrBot pytest data\plugins\astrbot_plugin_3D_dice\test
```
