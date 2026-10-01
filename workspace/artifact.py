"""Phase 1 核心领域对象（规格第 8 节）：ArtifactRef / Artifact / ArtifactBlock。

Artifact 是统一核心对象（P3）：DOCX/PDF/XLSX/PPTX 进入上层后都表现为 Artifact。
内部模型面向程序；面向 LLM 的表示见 llm/context.py，两者不混为一个对象（P4）。
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# 第一阶段核心支持格式（FR-W02）
ARTIFACT_TYPES = {"docx", "pdf", "xlsx", "pptx"}


def make_artifact_id(path: str | Path) -> str:
    """由文件绝对路径生成稳定的 Artifact ID。

    同一位置的文件无论扫描多少次，ID 保持一致（G1 稳定性要求）。
    文件移动或重命名后 ID 会变化，这是 Phase 1 的明确取舍。
    """
    digest = hashlib.sha256(str(Path(path).resolve()).encode("utf-8")).hexdigest()
    return f"a_{digest[:16]}"


@dataclass
class ArtifactRef:
    """表达"存在一个文件"，尚未读取正文（规格 8.2）。"""

    artifact_id: str
    name: str
    path: str
    extension: str
    size: int
    modified_at: datetime
    artifact_type: str


@dataclass
class ArtifactBlock:
    """所有文件内部内容的统一表达单元（规格 8.4）。

    block_type 例如：heading / paragraph / list_item / table / image_reference /
    text_block / textbox / slide。
    text 面向文本型内容；表格等结构化内容放在 metadata（如 cells 网格）。
    """

    block_id: str
    block_type: str
    text: str | None = None
    location: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)


@dataclass
class Artifact:
    """统一核心对象（规格 8.3）。

    content 是适配器生成的扁平文本预览（面向日志/快速查看）；
    结构化信息以 blocks 为准；面向 LLM 的渲染由 llm.context.artifact_to_context 负责。
    """

    artifact_id: str
    name: str
    path: str
    artifact_type: str
    metadata: dict = field(default_factory=dict)
    content: str = ""
    blocks: list[ArtifactBlock] = field(default_factory=list)
    provenance: dict = field(default_factory=dict)

    def blocks_of_type(self, block_type: str) -> list[ArtifactBlock]:
        return [b for b in self.blocks if b.block_type == block_type]
