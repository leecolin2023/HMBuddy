"""Phase 1.1.1 修订：ArtifactLocator 是核心契约（规格 BUG-009），
定义在本模块供插件与 plugin_runtime 共同使用；ArtifactBlock 增加 locator 字段。"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


def make_artifact_id(path: str | Path) -> str:
    """由文件绝对路径生成稳定的 Artifact ID。

    同一位置的文件无论扫描多少次，ID 保持一致（G1 稳定性要求）。
    文件移动或重命名后 ID 会变化，这是 Phase 1 的明确取舍。
    """
    digest = hashlib.sha256(str(Path(path).resolve()).encode("utf-8")).hexdigest()
    return f"a_{digest[:16]}"


def make_workspace_id(root_path: str | Path) -> str:
    """由 Workspace 根目录生成稳定 ID，用于 ArtifactRef 信任域标记（BUG-007）。"""
    digest = hashlib.sha256(str(Path(root_path).resolve()).encode("utf-8")).hexdigest()
    return f"ws_{digest[:12]}"


@dataclass
class ArtifactLocator:
    """格式特有的稳定定位描述（规格第 13 节 / BUG-009）。

    Core 只保存和传递 Locator，解释权归对应格式插件所有；
    block_id 只是解析顺序 ID，不承担跨版本定位职责。
    """

    scheme: str
    data: dict = field(default_factory=dict)


@dataclass
class ArtifactRef:
    """表达"存在一个文件"，尚未读取正文（规格 8.2）。

    workspace_id 标记信任域（BUG-007）：由 Workspace 生成的 Ref 必须在
    原 Workspace（或同信任域 Workspace）内才能读取。
    """

    artifact_id: str
    name: str
    path: str
    extension: str
    size: int
    modified_at: datetime
    artifact_type: str
    workspace_id: str | None = None
    relative_path: str | None = None


@dataclass
class ArtifactBlock:
    """所有文件内部内容的统一表达单元（规格 8.4 + BUG-009）。

    block_type 例如：heading / paragraph / list_item / table / image_reference /
    text_block / textbox / slide。
    text 面向文本型内容；表格等结构化内容放在 metadata（如 cells 网格）。
    locator 是格式插件生成的稳定定位（可跨版本解释）；location 仅为
    兼容/展示保留的解析期信息。
    """

    block_id: str
    block_type: str
    text: str | None = None
    location: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
    locator: ArtifactLocator | None = None


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
