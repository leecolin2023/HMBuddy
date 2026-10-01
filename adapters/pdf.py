"""PDF Adapter（规格第 12 节）。

第一阶段只处理有文本层的 PDF：保留 page / text block（行级，含页码归属）/
table（能力允许时）/ 图片引用。无文本层时标记 requires_ocr=true，不自动 OCR。
"""
from __future__ import annotations

from pathlib import Path

import pdfplumber

from workspace.artifact import Artifact, ArtifactBlock
from workspace.errors import EncryptedArtifactError

from .base import ArtifactAdapter, assign_block_ids


def _is_encryption_error(exc: Exception) -> bool:
    name = type(exc).__name__.lower()
    return "encrypt" in name or "password" in name


def _round_bbox(bbox) -> list[float]:
    try:
        return [round(float(v), 2) for v in bbox]
    except Exception:
        return []


class PdfAdapter(ArtifactAdapter):
    artifact_type = "pdf"
    supported_extensions = (".pdf",)
    parser_library = "pdfplumber"

    def read(self, path: Path, artifact_id: str) -> Artifact:
        try:
            pdf = pdfplumber.open(str(path))
        except Exception as exc:
            if _is_encryption_error(exc):
                raise EncryptedArtifactError(
                    path, adapter=type(self).__name__, reason=str(exc)
                ) from exc
            raise

        blocks: list[ArtifactBlock] = []
        pages_meta: list[dict] = []
        table_count = 0
        image_reference_count = 0
        try:
            doc_meta = dict(pdf.metadata or {})
            for page_number, page in enumerate(pdf.pages, start=1):
                # 同一页内的块按纵向位置排序后输出，文本块保持自上而下的阅读顺序
                page_blocks: list[tuple[float, ArtifactBlock]] = []

                try:
                    lines = page.extract_text_lines() or []
                except Exception:
                    lines = []
                lines.sort(key=lambda d: (d.get("top", 0.0), d.get("x0", 0.0)))
                line_index = 0
                for line in lines:
                    text = (line.get("text") or "").strip()
                    if not text:
                        continue
                    page_blocks.append(
                        (
                            float(line.get("top", 0.0)),
                            ArtifactBlock(
                                "",
                                "text_block",
                                text,
                                {"page": page_number, "line_index": line_index},
                                {
                                    "x0": round(float(line.get("x0", 0.0)), 2),
                                    "top": round(float(line.get("top", 0.0)), 2),
                                },
                            ),
                        )
                    )
                    line_index += 1

                try:
                    found_tables = page.find_tables()
                except Exception:
                    found_tables = []
                for table_index_on_page, table in enumerate(found_tables):
                    try:
                        data = table.extract() or []
                    except Exception:
                        data = []
                    cells = [
                        [("" if c is None else str(c).strip()) for c in row]
                        for row in data
                    ]
                    top = float(table.bbox[1]) if table.bbox else 0.0
                    page_blocks.append(
                        (
                            top,
                            ArtifactBlock(
                                "",
                                "table",
                                None,
                                {"page": page_number, "table_index": table_index_on_page},
                                {
                                    "rows": len(cells),
                                    "columns": len(cells[0]) if cells else 0,
                                    "cells": cells,
                                    "bbox": _round_bbox(table.bbox),
                                },
                            ),
                        )
                    )
                    table_count += 1

                images = page.images or []
                if images:
                    page_blocks.append(
                        (
                            0.0,
                            ArtifactBlock(
                                "",
                                "image_reference",
                                None,
                                {"page": page_number},
                                {
                                    "count": len(images),
                                    "bboxes": [
                                        _round_bbox(
                                            (
                                                img.get("x0", 0),
                                                img.get("top", 0),
                                                img.get("x1", 0),
                                                img.get("bottom", 0),
                                            )
                                        )
                                        for img in images
                                    ],
                                },
                            ),
                        )
                    )
                    image_reference_count += 1

                page_blocks.sort(key=lambda pair: pair[0])
                blocks.extend(block for _, block in page_blocks)

                page_text = page.extract_text() or ""
                pages_meta.append(
                    {
                        "page": page_number,
                        "text_chars": len(page_text.strip()),
                        "text_block_count": line_index,
                        "has_images": bool(images),
                    }
                )
        finally:
            pdf.close()

        total_text_chars = sum(m["text_chars"] for m in pages_meta)
        metadata = {
            "title": doc_meta.get("Title") or None,
            "page_count": len(pages_meta),
            "requires_ocr": bool(pages_meta) and total_text_chars == 0,
            "pages": pages_meta,
            "table_count": table_count,
            "image_reference_count": image_reference_count,
        }
        content = "\n".join(block.text for block in blocks if block.text)
        assign_block_ids(blocks)
        return self.build_artifact(
            path,
            artifact_id,
            blocks=blocks,
            metadata=metadata,
            content=content,
            file_stat=path.stat(),
        )
