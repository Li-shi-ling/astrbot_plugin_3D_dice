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
- 支持自动检测 Chrome、Edge、Chromium 和 Playwright Chromium
- 支持缺少 Playwright Chromium 时自动安装
- 支持常驻渲染 worker 复用浏览器页面
- 支持多种 GIF 生成后端
- 支持在无图形界面的 Linux 环境中自动尝试使用 `xvfb-run`
- 默认裁剪骰子区域，避免把顶部控制按钮和底部 Roll 按钮截入 GIF

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

## 浏览器选择

`browser` 留空时，插件会按通用规则自动选择浏览器：

1. 环境变量中的显式浏览器路径
2. Playwright bundled Chromium
3. 系统 Chrome、Edge、Chromium

插件会跳过常见的不可直接执行浏览器 wrapper，例如 snap Chromium wrapper，避免公共 Linux 环境中误选无法正常启动的浏览器。

这是公共插件，不会在代码里写死某台机器的浏览器路径。如果你的服务器需要固定浏览器，可在插件配置中填写 `browser`。

## Linux 与 Xvfb

部分无桌面 Linux 服务器中，headless Chromium 可能无法正常创建 WebGL 上下文。插件的 render worker 支持通过环境变量控制 `xvfb-run`：

```bash
ASTRBOT_3D_DICE_USE_XVFB=auto
```

可选值：

- `auto`：默认值。Linux 无 `DISPLAY` 且存在 `xvfb-run` 时自动使用
- `true`：强制使用 `xvfb-run`，找不到时直接报错
- `false`：禁用 `xvfb-run`

不需要用 `xvfb-run` 启动 AstrBot 主进程；worker 会按配置自行包装。

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

## GIF 后端

`gif_backend` 支持：

- `screenshot`：逐帧截图，裁剪最精确
- `cdp_screencast_limited`：使用 Chrome DevTools screencast，并按目标帧率限帧
- `cdp_screencast`：使用 Chrome DevTools screencast
- `cdp_screencast_ffmpeg`：screencast 帧流式写入 ffmpeg
- `webm_ffmpeg`：录制 canvas WebM 后用 ffmpeg 转 GIF

默认裁剪会保留骰子区域，并尽量避开页面控制按钮。当前默认裁剪宽度上限为 560 像素，并在上下方向内缩，减少截到底部 Roll 按钮的概率。

`webm_ffmpeg` 是直接录制 canvas 的后端，不走截图裁剪逻辑，因此输出尺寸可能与其它后端不同。

## 配置（`_conf_schema.json`）

- `default_dice_type`: 默认骰子类型，支持 `D4`、`D6`、`D8`、`D20`
- `default_count`: 默认骰子数量
- `max_count`: 最大骰子数量，最多 6
- `duration`: GIF 录制时长，单位毫秒
- `fps`: GIF 帧率
- `browser`: 可选浏览器路径；留空时自动检测浏览器
- `gif_backend`: GIF 生成后端
- `screencast_quality`: CDP screencast 系列后端的 JPEG 质量
- `ffmpeg_path`: 可选 ffmpeg 路径
- `auto_install_chromium`: 找不到浏览器时是否自动执行 `python -m playwright install chromium`
- `better_render_quality`: 是否等待 3D 场景完整渲染后再点击 Roll 并录制
- `prewarm_render_worker`: 插件启动时是否预热 render worker
- `width`: 浏览器渲染视口宽度
- `height`: 浏览器渲染视口高度
- `parallel_result`: GIF 捕获后是否立即读取结果

## 许可

AGPL-3.0

## 开发者

- 作者：Lishining
- QQ群: 1083090761

## 致谢

感谢 [rollmydices](https://www.rollmydice.app/) 的 3D 代码支持。

[![Moe Counter](https://count.getloli.com/get/@li-shi-ling?theme=minecraft)](https://github.com/Li-shi-ling/astrbot_plugin_mrfzccl)
