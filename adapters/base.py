"""Base Adapter 公共契约（规格 Step 4 / FR-A03）：所有 Adapter 必须返回统一 Artifact。"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import ClassVar, Optional

from workspace.artifact import Artifact, ArtifactBlock
from workspace.errors import EncryptedArtifactError

from .ocr.engine import DEFAULT_OCR_MODEL_PROFILE

# OLE 复合文档魔数：OOXML 扩展名（docx/xlsx/pptx）的文件若呈现该魔数，
# 要么是被加密（加密后变成 OLE 容器），要么是旧二进制格式改了扩展名（ER-03）。
OLE_MAGIC = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"


def ensure_not_ole(path: Path, adapter: "ArtifactAdapter") -> None:
    """ER-03 前置检查：OOXML 扩展名 + OLE 魔数 → 明确报加密/格式错误。"""
    with open(path, "rb") as f:
        head = f.read(len(OLE_MAGIC))
    if head == OLE_MAGIC:
        raise EncryptedArtifactError(
            path,
            adapter=type(adapter).__name__,
            reason=(
                "file is an OLE compound document "
                "(password-protected/encrypted, or a legacy binary Office file)"
            ),
        )


def assign_block_ids(blocks: list[ArtifactBlock]) -> list[ArtifactBlock]:
    """按阅读顺序统一分配 block_id（b0001, b0002, ...）。"""
    for index, block in enumerate(blocks, start=1):
        block.block_id = f"b{index:04d}"
    return blocks


@dataclass(frozen=True)
class OcrOptions:
    """OCR 可选能力（移植自 fce 的 RunOptions 语义）。

    边界约束（沿用 fce/AGENTS.md）：默认关闭，绝不隐式下载模型；
    模型只从本地目录解析（HMBUDDY_MODEL_DIR / FCE_MODEL_DIR / ./models）。
    """

    enable_ocr: bool = False
    enable_table_ocr: bool = True
    model_root: Optional[Path] = None
    model_profile: str = DEFAULT_OCR_MODEL_PROFILE


class ArtifactAdapter(ABC):
    """格式适配器基类：supports() 判断是否支持，read() 输出统一 Artifact。"""

    artifact_type: ClassVar[str] = ""
    supported_extensions: ClassVar[tuple[str, ...]] = ()
    parser_library: ClassVar[str] = ""

    def __init__(self, ocr_options: Optional["OcrOptions"] = None):
        # 所有适配器统一接受 OcrOptions；不需要 OCR 的适配器直接忽略
        self.ocr_options = ocr_options or OcrOptions()

    def supports(self, path: Path) -> bool:
        return path.suffix.lower() in self.supported_extensions

    @abstractmethod
    def read(self, path: Path, artifact_id: str) -> Artifact:
        """读取文件并转换为统一 Artifact。解析异常交由 ArtifactReader 包装。"""

    def build_artifact(
        self,
        path: Path,
        artifact_id: str,
        *,
        blocks: list[ArtifactBlock],
        metadata: dict,
        content: str,
        file_stat,
        artifact_type: Optional[str] = None,
    ) -> Artifact:
        """构造 Artifact 并填充 FR-A04 要求的 provenance（读取时间等由 Reader 补充）。

        artifact_type 允许适配器按具体文件覆写（如 TextAdapter 的 txt/md/csv）。
        """
        resolved_type = artifact_type or self.artifact_type
        provenance = {
            "source_path": str(path),
            "artifact_type": resolved_type,
            "adapter": type(self).__name__,
            "parser_library": self.parser_library,
            "file_size": file_stat.st_size,
            "file_modified_at": datetime.fromtimestamp(
                file_stat.st_mtime, tz=timezone.utc
            ).isoformat(),
        }
        return Artifact(
            artifact_id=artifact_id,
            name=path.name,
            path=str(path),
            artifact_type=resolved_type,
            metadata=metadata,
            content=content,
            blocks=blocks,
            provenance=provenance,
        )
