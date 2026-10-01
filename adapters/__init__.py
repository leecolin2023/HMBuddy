"""adapters 包：格式适配层（规格 P2 —— 文件格式差异必须被 Adapter 隔离）。"""
from .base import ArtifactAdapter, assign_block_ids, ensure_not_ole
from .docx import DocxAdapter
from .pdf import PdfAdapter
from .pptx import PptxAdapter
from .xlsx import XlsxAdapter

ADAPTER_CLASSES = (DocxAdapter, PdfAdapter, XlsxAdapter, PptxAdapter)


def default_adapters() -> list[ArtifactAdapter]:
    return [cls() for cls in ADAPTER_CLASSES]


__all__ = [
    "ArtifactAdapter",
    "assign_block_ids",
    "ensure_not_ole",
    "DocxAdapter",
    "PdfAdapter",
    "XlsxAdapter",
    "PptxAdapter",
    "default_adapters",
]
