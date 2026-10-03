"""Preview 渲染器（规格第 20-25 节）。

硬性边界（规格第 21 节 / AC-18）：渲染器只消费 Artifact（content / metadata），
禁止通过 path → open() / Path.read_text() 绕过 Artifact Runtime。
Markdown 使用 Qt 自身 Markdown 渲染；TXT 只读展示；其余格式 Unsupported。
"""
from __future__ import annotations

from dataclasses import dataclass

SUPPORTED_PREVIEW_EXTENSIONS = {".md", ".markdown", ".txt"}


@dataclass
class PreviewModel:
    """Preview 渲染的输入模型（来自 Artifact，不含 path 读取行为）。"""

    name: str
    artifact_type: str
    content: str
    size: int
    supported: bool


def build_preview_model(artifact) -> PreviewModel:
    """由 Artifact 构造渲染模型；扩展名决定 Preview 支持性（规格第 24 节：
    必须区分"可以读取"与"可以 Preview"）。"""
    extension = f".{artifact.artifact_type.lower()}"
    supported = extension in SUPPORTED_PREVIEW_EXTENSIONS
    return PreviewModel(
        name=artifact.name,
        artifact_type=artifact.artifact_type.upper(),
        content=artifact.content or "",
        size=artifact.provenance.get("file_size", 0),
        supported=supported,
    )
