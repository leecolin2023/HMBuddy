"""adapters 包：格式适配层（规格 P2 —— 文件格式差异必须被 Adapter 隔离）。

Phase 1 核心四格式 + fce 能力融入的扩展：
- 文本格式（txt/md/csv...，多编码回退）
- 遗留 Office（.xls 经 xlrd/COM，.doc 经 Word/WPS COM；依赖懒加载）
- OCR（PaddleOCR/SLANet，默认关闭、懒加载，模型只从本地目录解析）
"""
from .base import ArtifactAdapter, OcrOptions, assign_block_ids, ensure_not_ole
from .doc_legacy import DocLegacyAdapter
from .docx import DocxAdapter
from .pdf import PdfAdapter
from .pptx import PptxAdapter
from .text import TextAdapter
from .xls import XlsAdapter
from .xlsx import XlsxAdapter

ADAPTER_CLASSES = (
    DocxAdapter,
    DocLegacyAdapter,
    PdfAdapter,
    XlsxAdapter,
    XlsAdapter,
    PptxAdapter,
    TextAdapter,
)


def default_adapters(ocr_options: OcrOptions | None = None) -> list[ArtifactAdapter]:
    """构造默认适配器集；OCR 选项只影响支持 OCR 的适配器（PDF/DOCX）。"""
    return [cls(ocr_options) if ocr_options is not None else cls() for cls in ADAPTER_CLASSES]


__all__ = [
    "ArtifactAdapter",
    "OcrOptions",
    "assign_block_ids",
    "ensure_not_ole",
    "DocxAdapter",
    "DocLegacyAdapter",
    "PdfAdapter",
    "XlsxAdapter",
    "XlsAdapter",
    "PptxAdapter",
    "TextAdapter",
    "default_adapters",
]
