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

# 将插件根目录加入 sys.path，使本地 pybatchrender 包可直接导入
_project_str = str(PROJECT_DIR)
if _project_str not in sys.path:
    sys.path.insert(0, _project_str)

from pybatchrender import PBRRenderer  # noqa: E402  # type: ignore

TILE_RESOLUTION = (512, 512)

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
    1: (0.0,  0.0,          0.0),
    2: (0.0,  0.0,         -np.pi / 2),
    3: (0.0,  np.pi / 2,    0.0),
    4: (0.0, -np.pi / 2,    0.0),
    5: (0.0,  0.0,          np.pi / 2),
    6: (0.0,  np.pi,        0.0),
}


def _build_rotation_matrix(hpr_rad: np.ndarray) -> np.ndarray: