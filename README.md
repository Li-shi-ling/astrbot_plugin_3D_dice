# 3D Dice

AstrBot 3D Dice 使用纯 Python 管线生成物理仿真的动态骰子 GIF，支持 D4、D6、D8、D10 和 D20。

## 用法

聊天命令：

```text
/roll3d D20
/roll3d 2D6
/roll3d D10 count=2 seed=42
```

别名包括 `/3d_dice`、`/3ddice`、`/dice3d`、`投骰子` 和 `骰子`。返回内容包含最终点数、总和、随机种子和生成的 GIF。

## 实现

核心库位于 `dice_sim/`：

- `geometry.py` 生成 D4/D6/D8/D10/D20 的凸多面体网格和点数面元数据。
- `physics.py` 使用 PyBullet DIRECT 模式进行无窗口刚体仿真。
- `render.py` 使用 numpy 和 Pillow 做软件投影、深度排序、简单明暗和文字绘制。
- `gif.py` 使用 imageio 写出动画 GIF，并用 Pillow 验证帧数。
- `generator.py` 提供可独立调用的 `roll_gif()` API。

默认渲染不依赖 Node.js、浏览器、Blender 或前端静态资源。

## 依赖

```bash
pip install -r requirements.txt
```

运行时依赖：

- `pybullet`：物理仿真
- `numpy`：几何和矩阵计算
- `Pillow`：软件绘制和 GIF 验证
- `imageio`：GIF 编码

请在 AstrBot 使用的同一个 Python 环境中安装这些依赖。`pybullet` 和 `imageio` 在执行路径中懒加载，缺少时会返回可读错误；`numpy` 和 `Pillow` 是基础渲染依赖，也应随 `requirements.txt` 一起安装。

## 结果规则

- D6、D8、D10、D20：最终姿态中法线最朝上的结果面作为点数。
- D4：使用底面规则，最终姿态中法线最朝下的面作为点数。
- D10：返回 1 到 10，不使用 0 到 9 约定。

## 配置

`_conf_schema.json` 提供这些常用配置：

- `default_dice_type`、`default_count`、`max_count`
- `duration_ms`、`fps`、`width`、`height`
- `seed`
- `die_color`、`background_color`
- `max_cache_files`、`cache_max_age_seconds`

GIF 默认写入 AstrBot 插件数据目录下的 `outputs/`。缓存清理会限制 GIF 数量和保留时间，不会写出临时帧文件。

GIF 帧会在内存中渲染后写出。默认尺寸、帧率和时长适合聊天场景；如果提高 `width`、`height`、`fps` 或 `duration_ms`，峰值内存会随总帧数和画面尺寸增长。

## 维护验证

运行单元测试：

```bash
python -m pytest
```

生成示例 GIF：

```bash
python scripts/smoke_generate_gifs.py --output-dir outputs/smoke
```

如果本机没有安装 PyBullet，GIF smoke 测试会跳过；几何、解析和结果判定测试仍可运行。
