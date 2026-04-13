from __future__ import annotations

import secrets
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch
from PIL import Image

RUNTIME_DIR = Path(__file__).resolve().parent
PROJECT_DIR = RUNTIME_DIR.parent

FRAME_DURATION_MS = 62  # ~16fps
TILE_RESOLUTION = (512, 512)

# 每种骰子类型的颜色 (R,G,B,A)
_DICE_COLORS: dict[str, tuple[float, float, float, float]] = {
    "D4":  (0.90, 0.30, 0.30, 1.0),
    "D6":  (0.96, 0.96, 0.93, 1.0),
    "D8":  (0.30, 0.55, 0.90, 1.0),
    "D20": (0.30, 0.80, 0.40, 1.0),
}
_PIP_COLOR = (0.08, 0.08, 0.08, 1.0)

# D6 各点数对应的最终 HPR（使对应面朝上 +Z）
# H=绕Z, P=绕X, R=绕Y
_D6_RESULT_HPR: dict[int, tuple[float, float, float]] = {
    1: (0.0,          0.0,          0.0),
    2: (0.0,          0.0,         -np.pi / 2),
    3: (0.0,          np.pi / 2,    0.0),
    4: (0.0,         -np.pi / 2,    0.0),
    5: (0.0,          0.0,          np.pi / 2),
    6: (0.0,          np.pi,        0.0),
}


def _ensure_pbr() -> None:
    """确保 pybatchrender 可导入，优先使用插件目录内的本地副本。"""
    try:
        import pybatchrender  # noqa: F401
        return
    except ImportError:
        pass
    # 将插件根目录加入 sys.path，使 PROJECT_DIR/pybatchrender 可被导入
    project_str = str(PROJECT_DIR)
    if project_str not in sys.path:
        sys.path.insert(0, project_str)


def _build_rotation_matrix(hpr_rad: np.ndarray) -> np.ndarray:
    h, p, r = hpr_rad.astype(np.float32)
    ch, sh = np.cos(h), np.sin(h)
    cp, sp = np.cos(p), np.sin(p)
    cr, sr = np.cos(r), np.sin(r)
    rz = np.array([[ch, -sh, 0], [sh, ch, 0], [0, 0, 1]], dtype=np.float32)
    rx = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]], dtype=np.float32)
    ry = np.array([[cr, 0, sr], [0, 1, 0], [-sr, 0, cr]], dtype=np.float32)
    return rz @ rx @ ry


def _d6_pip_layout() -> np.ndarray:
    """返回 D6 所有 21 个点的本地坐标 (21, 3)。"""
    half = 1.0
    inset = 1.02
    offset = 0.38
    layouts: dict[int, list[tuple[float, float]]] = {
        1: [(0.0, 0.0)],
        2: [(-offset, -offset), (offset, offset)],
        3: [(-offset, -offset), (0.0, 0.0), (offset, offset)],
        4: [(-offset, -offset), (-offset, offset), (offset, -offset), (offset, offset)],
        5: [(-offset, -offset), (-offset, offset), (0.0, 0.0), (offset, -offset), (offset, offset)],
        6: [(-offset, -offset), (-offset, 0.0), (-offset, offset),
            (offset, -offset), (offset, 0.0), (offset, offset)],
    }
    points: list[list[float]] = []
    for u, v in layouts[1]:
        points.append([u, v, half * inset])
    for u, v in layouts[6]:
        points.append([-u, v, -half * inset])
    for u, v in layouts[2]:
        points.append([half * inset, v, -u])
    for u, v in layouts[5]:
        points.append([-half * inset, v, u])
    for u, v in layouts[3]:
        points.append([u, half * inset, -v])
    for u, v in layouts[4]:
        points.append([u, -half * inset, v])
    return np.asarray(points, dtype=np.float32)


def _slerp_hpr(
    start: np.ndarray, end: np.ndarray, t: float
) -> np.ndarray:
    """线性插值 HPR（简单 lerp，足够用于骰子动画）。"""
    return start + (end - start) * t


def _dice_spacing(count: int) -> list[float]:
    """返回 count 个骰子的 X 轴偏移列表，使其居中排列。"""
    step = 2.8
    total = (count - 1) * step
    return [-total / 2 + i * step for i in range(count)]


# ---------------------------------------------------------------------------
# D6 渲染器
# ---------------------------------------------------------------------------

class _D6Renderer:
    """在已有 PBRRenderer 实例上管理 D6 骰子的节点。"""

    def __init__(self, renderer: Any, count: int) -> None:
        self.count = count
        self.local_pips = _d6_pip_layout()  # (21, 3)
        n_pips = len(self.local_pips)

        color = _DICE_COLORS["D6"]
        offsets = _dice_spacing(count)

        # 骰子主体：count 个实例
        self.body = renderer.add_node(
            "models/box",
            instances_per_scene=count,
            model_scale=(2.0, 2.0, 2.0),
            model_scale_units="absolute",
            texture=False,
            shared_across_scenes=False,
        )
        init_pos = torch.zeros((1, count, 3), dtype=torch.float32)
        for i, x in enumerate(offsets):
            init_pos[0, i, 0] = x
        self.body.set_positions(init_pos)
        body_colors = torch.tensor(
            [[[*color]] * count], dtype=torch.float32
        )
        self.body.set_colors(body_colors)

        # 点（pip）：count * n_pips 个实例
        self.pips = renderer.add_node(
            "models/smiley",
            instances_per_scene=count * n_pips,
            model_scale=0.18,
            model_scale_units="absolute",
            texture=False,
            shared_across_scenes=False,
        )
        pip_col = np.tile(
            np.array([_PIP_COLOR], dtype=np.float32),
            (count * n_pips, 1),
        ).reshape(1, count * n_pips, 4)
        self.pips.set_colors(torch.tensor(pip_col))

        self._offsets = offsets

    def update(self, hprs: np.ndarray) -> None:
        """hprs: (count, 3) 每个骰子的 HPR。"""
        count = self.count
        n_pips = len(self.local_pips)

        # 更新主体旋转
        hpr_tensor = torch.tensor(
            hprs.reshape(1, count, 3), dtype=torch.float32
        )
        self.body.set_hprs(hpr_tensor)

        # 更新 pip 位置（旋转后的本地坐标 + 骰子偏移）
        all_pip_pos = np.zeros((count * n_pips, 3), dtype=np.float32)
        for i in range(count):
            rot = _build_rotation_matrix(hprs[i])
            rotated = (self.local_pips @ rot.T).astype(np.float32)
            rotated[:, 0] += self._offsets[i]
            all_pip_pos[i * n_pips : (i + 1) * n_pips] = rotated

        self.pips.set_positions(
            torch.tensor(all_pip_pos.reshape(1, count * n_pips, 3))
        )


# ---------------------------------------------------------------------------
# 通用骰子渲染器（D4 / D8 / D20 用球体代替）
# ---------------------------------------------------------------------------

class _GenericDiceRenderer:
    """用球体渲染非 D6 骰子。"""

    def __init__(self, renderer: Any, count: int, dice_type: str) -> None:
        self.count = count
        color = _DICE_COLORS.get(dice_type, (0.7, 0.7, 0.7, 1.0))
        offsets = _dice_spacing(count)
        self._offsets = offsets

        self.body = renderer.add_node(
            "models/smiley",
            instances_per_scene=count,
            model_scale=(2.0, 2.0, 2.0),
            model_scale_units="absolute",
            texture=False,
            shared_across_scenes=False,
        )
        init_pos = torch.zeros((1, count, 3), dtype=torch.float32)
        for i, x in enumerate(offsets):
            init_pos[0, i, 0] = x
        self.body.set_positions(init_pos)
        body_colors = torch.tensor(
            [[[*color]] * count], dtype=torch.float32
        )
        self.body.set_colors(body_colors)

    def update(self, hprs: np.ndarray) -> None:
        hpr_tensor = torch.tensor(
            hprs.reshape(1, self.count, 3), dtype=torch.float32
        )
        self.body.set_hprs(hpr_tensor)


# ---------------------------------------------------------------------------
# 主渲染函数
# ---------------------------------------------------------------------------

def _make_renderer(dice_type: str, count: int) -> Any:
    """创建并返回配置好的 PBRRenderer 实例。"""
    _ensure_pbr()
    from pybatchrender import PBRRenderer  # type: ignore

    # 根据骰子数量调整视野和相机位置
    fov = 36.0 + max(0, count - 1) * 6.0
    eye_x = 0.0
    eye_y = -8.2 - max(0, count - 1) * 2.5
    eye_z = 4.8

    class _DiceScene(PBRRenderer):  # type: ignore
        def __init__(self) -> None:
            super().__init__(
                num_scenes=1,
                tiles=(1, 1),
                tile_resolution=TILE_RESOLUTION,
                offscreen=True,
                report_fps=False,
                panda3d_backend="arm",
                cuda_gl_interop=False,
            )
            self.set_background_color(0.97, 0.97, 0.99, 1.0)

            if dice_type == "D6":
                self._dice = _D6Renderer(self, count)
            else:
                self._dice = _GenericDiceRenderer(self, count, dice_type)

            self.add_camera(fov_y_deg=fov, z_near=0.1, z_far=100.0)
            self._pbr_cam.set_positions_and_lookat(
                eye_k3=torch.tensor([[eye_x, eye_y, eye_z]], dtype=torch.float32),
                target_k3=torch.tensor([[0.0, 0.0, 0.0]], dtype=torch.float32),
            )
            self.add_light(
                ambient=(0.55, 0.55, 0.58),
                dir_dir=(0.7, -0.9, -1.2),
                dir_col=(1.0, 1.0, 1.0),
                strength=1.75,
            )
            self.setup_environment()

        def _step(self, hprs: np.ndarray | None = None) -> None:
            if hprs is None:
                hprs = np.zeros((count, 3), dtype=np.float32)
            self._dice.update(hprs)

    return _DiceScene()


def _generate_results(dice_type: str, count: int) -> list[int]:
    max_face = int(dice_type[1:])
    return [secrets.randbelow(max_face) + 1 for _ in range(count)]


def _build_animation_hprs(
    results: list[int],
    dice_type: str,
    total_frames: int,
) -> list[np.ndarray]:
    """
    返回每帧的 hprs 列表，每个元素 shape=(count, 3)。
    前 70% 帧：快速翻滚；后 30% 帧：减速落定到最终朝向。
    """
    count = len(results)
    rng = np.random.default_rng()

    # 每个骰子的随机初始 HPR 偏移（增加随机感）
    init_offsets = rng.uniform(-np.pi, np.pi, size=(count, 3)).astype(np.float32)

    # D6 最终朝向；其他骰子类型用零旋转（球体无所谓朝向）
    final_hprs = np.zeros((count, 3), dtype=np.float32)
    if dice_type == "D6":
        for i, r in enumerate(results):
            final_hprs[i] = np.array(_D6_RESULT_HPR[r], dtype=np.float32)

    settle_start = int(total_frames * 0.70)
    frames: list[np.ndarray] = []

    for frame_idx in range(total_frames):
        t = frame_idx / max(total_frames - 1, 1)
        hprs = np.zeros((count, 3), dtype=np.float32)

        if frame_idx < settle_start:
            # 翻滚阶段：每个骰子独立旋转
            t_roll = frame_idx / max(settle_start - 1, 1)
            speed_decay = 1.0 - t_roll * 0.5  # 逐渐减速
            for i in range(count):
                phase = init_offsets[i]
                hprs[i] = np.array([
                    phase[0] + t_roll * np.pi * 4.0 * speed_decay,
                    phase[1] + t_roll * np.pi * 3.2 * speed_decay + 0.35,
                    phase[2] + t_roll * np.pi * 2.4 * speed_decay + 0.2,
                ], dtype=np.float32)
        else:
            # 落定阶段：从翻滚末尾插值到最终朝向
            t_settle = (frame_idx - settle_start) / max(total_frames - settle_start - 1, 1)
            ease = t_settle ** 2  # ease-in

            # 翻滚末尾的 HPR
            t_roll_end = 1.0
            speed_decay_end = 0.5
            for i in range(count):
                phase = init_offsets[i]
                roll_end = np.array([
                    phase[0] + t_roll_end * np.pi * 4.0 * speed_decay_end,
                    phase[1] + t_roll_end * np.pi * 3.2 * speed_decay_end + 0.35,
                    phase[2] + t_roll_end * np.pi * 2.4 * speed_decay_end + 0.2,
                ], dtype=np.float32)
                hprs[i] = _slerp_hpr(roll_end, final_hprs[i], ease)

        frames.append(hprs)

    return frames


def render_dice_gif(
    dice_type: str = "D6",
    count: int = 1,
    duration: int = 2400,
    fps: int = 16,
    output_name: str | None = None,
    output_dir: Path | None = None,
    **_kwargs: Any,
) -> dict[str, Any]:
    """
    使用 PyBatchRender 渲染骰子 GIF，返回与 render_dice.py 相同格式的结果字典。
    忽略 Playwright 专用参数（browser, width, height 等）。
    """
    output_dir = Path(output_dir or (RUNTIME_DIR / "outputs")).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    dice_type = dice_type.upper()
    frame_delay = max(20, round(1000 / max(1, fps)))
    total_frames = max(1, -(-duration // frame_delay))

    results = _generate_results(dice_type, count)
    frame_hprs = _build_animation_hprs(results, dice_type, total_frames)

    renderer = _make_renderer(dice_type, count)
    captured: list[Image.Image] = []
    try:
        for hprs in frame_hprs:
            pixels = renderer.step(hprs)          # (1, C, H, W) uint8
            frame_np = pixels[0].permute(1, 2, 0).contiguous().cpu().numpy()
            captured.append(Image.fromarray(frame_np, mode="RGB"))
    finally:
        try:
            renderer.destroy()
        except Exception:
            pass

    ts = int(time.time() * 1000)
    name = output_name or f"pbr-{dice_type.lower()}-{count}-{ts}.gif"
    output_path = output_dir / name

    captured[0].save(
        output_path,
        save_all=True,
        append_images=captured[1:],
        format="GIF",
        duration=frame_delay,
        loop=0,
        disposal=2,
    )

    return {
        "gif_path": str(output_path),
        "results": results,
        "total": sum(results),
        "dice_type": dice_type,
        "dice_count": count,
        "fallback": False,
        "partial": False,
    }


def get_dice_face_count(dice_type: str) -> int:
    return int(str(dice_type).strip().upper()[1:])


# 兼容旧接口：这些函数在 main.py 中被引用
def is_playwright_available() -> bool:
    return False


def playwright_install_reminder() -> str:
    return "此版本使用 PyBatchRender 渲染，无需 Playwright。"


def close_persisted_session() -> None:
    pass


def ensure_chromium_browser(auto_install: bool = True) -> Any:
    raise RuntimeError("PyBatchRender 版本不使用 Chromium。")
