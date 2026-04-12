# 3D Dice

AstrBot 插件：使用本地浏览器渲染 3D 投骰动画，并返回 GIF 和点数结果。

插件内置了压缩后的 Roll My Dice 静态页面，核心效果仍由原页面的 Three.js + Cannon 物理实现。当前支持 `D4`、`D6`、`D8`、`D20`，可一次投 1 到 6 个骰子。

## 命令

| 命令 | 说明 | 示例 |
|---|---|---|
| `/3d_dice` | 使用默认配置投骰 | `/3d_dice` |
| `/3d_dice [骰子]` | 指定骰子类型 | `/3d_dice D20` |
| `/3d_dice [骰子] [数量]` | 指定骰子类型和数量 | `/3d_dice D20 2` |
| `/3d_dice [数量]D[面数]` | 紧凑写法 | `/3d_dice 2D6` |
| `/3d_dice_help` | 查看用法 | `/3d_dice_help` |

别名：

- `/3ddice`
- `/dice3d`
- `/roll3d`
- `/投骰子`
- `/骰子`

## 功能

- 返回真实 3D 物理投骰 GIF
- 返回骰子明细和总点数
- 支持 D4、D6、D8、D20
- 支持 1 到 6 个骰子
- 支持自动检测 Chrome、Edge、Chromium
- 支持缺少 Playwright Chromium 时自动安装
- 支持更高质量的 GIF 录制模式

## 依赖

插件目录包含 `requirements.txt`，AstrBot 会自动安装 Python 依赖：

```text
pillow
playwright
```

注意：`playwright` Python 包安装后，还需要 Chromium 浏览器二进制。插件默认会在找不到浏览器时自动执行：

```bash
python -m playwright install chromium
```

如果 Playwright Python 包本身没有安装，插件不会直接崩溃；用户输入本插件指令时会返回安装提醒：

```bash
python -m pip install playwright
python -m playwright install chromium
```

也可以在配置里手动填写 `browser`，直接指定 Chrome、Edge 或 Chromium 可执行文件路径。

## 渲染机制

1. 插件启动本地静态文件服务，加载 `dice_roller_app/index.html`。
2. 使用 Playwright 打开本地页面。
3. 根据命令选择骰子类型和数量。
4. 默认等待 3D canvas 稳定渲染完成。
5. 点击原页面的 Roll 按钮。
6. 录制动画帧并写出 GIF。
7. 读取页面显示的投骰结果。
8. 向 AstrBot 消息链返回文字结果和 GIF 图片。

D4、D8、D20 使用原页面的 convex polyhedron 物理体。为了避免部分环境中多面骰偶发不下落，当前静态包保留原始速度/角速度范围，同时在 Roll 时显式唤醒物理体并重置到初始投掷位置。

## 配置（`_conf_schema.json`）

- `default_dice_type`: 默认骰子类型，支持 `D4`、`D6`、`D8`、`D20`
- `default_count`: 默认骰子数量
- `max_count`: 最大骰子数量，最多 6
- `duration`: GIF 录制时长，单位毫秒
- `fps`: GIF 帧率
- `browser`: 可选浏览器路径；留空时自动检测 Chrome、Edge、Chromium
- `auto_install_chromium`: 找不到浏览器时是否自动执行 `python -m playwright install chromium`
- `better_render_quality`: 是否等待 3D 场景完整渲染后再点击 Roll 并录制
- `width`: 浏览器渲染视口宽度
- `height`: 浏览器渲染视口高度

## 许可

AGPL-3.0

## 开发者

- 作者：Lishining
- QQ群: 1083090761

## 致谢

感谢[rollmydices](https://www.rollmydice.app/)的3d代码支持

[![Moe Counter](https://count.getloli.com/get/@li-shi-ling?theme=minecraft)](https://github.com/Li-shi-ling/astrbot_plugin_mrfzccl)
