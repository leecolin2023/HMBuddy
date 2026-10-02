from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class OcrTextBox:
    text: str
    score: float
    box: List[float]
    polygon: List[List[float]]


@dataclass(frozen=True)
class OcrImageTile:
    path: Path
    left: int
    top: int
    right: int
    bottom: int
    owner_left: float
    owner_top: float
    owner_right: float
    owner_bottom: float
