"""PDF Adapter（规格第 12 节 + fce 能力融入版）。

- 文本层：行级 text_block，保留页码归属与阅读顺序（不变）；
- 表格：优先使用矢量线表格引擎（adapters/pdf_tables.py，含合并单元格、
  表头识别、跨页续表链接），无矢量线时回退 pdfplumber 表格检测；
- OCR（可选，默认关闭）：无文本层的扫描件按需渲染页面并执行 PaddleOCR，
  表格结构识别（SLANet）可选启用；模型只从本地目录解析。
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pdfplumber

from workspace.artifact import Artifact, ArtifactBlock

from .base import ArtifactAdapter, OcrOptions, assign_block_ids
from .pdf_tables import (
    extract_pdf_vector_tables,
    link_pdf_table_continuations,
    normalize_pdf_table_pages,
)
from .tables import ExtractedTable, TableCell, TableRow, grid_to_table_metadata, table_to_block_metadata


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

    def __init__(self, ocr_options: OcrOptions | None = None):
        super().__init__(ocr_options)

    # ------------------------------------------------------------------
    # 主入口
    # ------------------------------------------------------------------

    def read(self, path: Path, artifact_id: str) -> Artifact:
        try:
            pdf = pdfplumber.open(str(path))
        except Exception as exc:
            if _is_encryption_error(exc):
                from workspace.errors import EncryptedArtifactError

                raise EncryptedArtifactError(
                    path, adapter=type(self).__name__, reason=str(exc)
                ) from exc
            raise

        blocks: list[ArtifactBlock] = []
        pages_meta: list[dict] = []
        all_tables: list[ExtractedTable] = []
        metadata_extra: dict = {}
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

                # 表格：矢量线引擎优先（含跨页续表），本页无矢量表格时回退 pdfplumber
                page_tables = extract_pdf_vector_tables(page, page_number)
                if not page_tables:
                    page_tables = self._tables_via_pdfplumber(page, page_number)
                all_tables.extend(page_tables)
                for table in page_tables:
                    top = float(table.bbox[1]) if table.bbox else 0.0
                    page_blocks.append(
                        (
                            top,
                            ArtifactBlock(
                                "",
                                "table",
                                None,
                                {
                                    "page": page_number,
                                    "table_index": table.table,
                                    **(
                                        {"bbox": _round_bbox(table.bbox)}
                                        if table.bbox
                                        else {}
                                    ),
                                },
                                table_to_block_metadata(table),
                            ),
                        )
                    )

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

            # 跨页续表：整份文档的表格统一规范化后再链接
            all_tables = normalize_pdf_table_pages(all_tables)
            link_pdf_table_continuations(all_tables)
            self._sync_table_blocks(blocks, all_tables)

            total_text_chars = sum(m["text_chars"] for m in pages_meta)
            requires_ocr = bool(pages_meta) and total_text_chars == 0
            if requires_ocr and self.ocr_options.enable_ocr:
                blocks, ocr_meta = self._run_ocr(path)
                metadata_extra = ocr_meta
                requires_ocr = False
        finally:
            pdf.close()

        metadata = {
            "title": doc_meta.get("Title") or None,
            "page_count": len(pages_meta),
            "requires_ocr": requires_ocr,
            "pages": pages_meta,
            "table_count": sum(
                1 for block in blocks if block.block_type == "table"
            ),
            "image_reference_count": sum(
                1 for block in blocks if block.block_type == "image_reference"
            ),
            **metadata_extra,
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

    # ------------------------------------------------------------------
    # 表格
    # ------------------------------------------------------------------

    @staticmethod
    def _tables_via_pdfplumber(page, page_number: int) -> list[ExtractedTable]:
        """矢量线引擎无结果时的回退：pdfplumber 内置表格检测（纯网格）。"""
        tables: list[ExtractedTable] = []
        try:
            found = page.find_tables()
        except Exception:
            found = []
        for table_index_on_page, found_table in enumerate(found, start=1):
            try:
                data = found_table.extract() or []
            except Exception:
                data = []
            cells = [
                [("" if c is None else str(c).strip()) for c in row] for row in data
            ]
            if not cells:
                continue
            rows = [
                TableRow(
                    index=row_index,
                    cells=[
                        TableCell(
                            row=row_index,
                            column=column_index,
                            text=cell_text,
                        )
                        for column_index, cell_text in enumerate(row_cells, start=1)
                    ],
                )
                for row_index, row_cells in enumerate(cells, start=1)
            ]
            tables.append(
                ExtractedTable(
                    page=page_number,
                    table=table_index_on_page,
                    rows=rows,
                    column_count=len(cells[0]) if cells else 0,
                    bbox=tuple(
                        round(float(v), 3) for v in (found_table.bbox or ())
                    ),  # type: ignore[arg-type]
                    extraction_method="pdfplumber-find-tables",
                    confidence=0.7,
                )
            )
        return tables

    @staticmethod
    def _sync_table_blocks(blocks: list[ArtifactBlock], tables: list[ExtractedTable]) -> None:
        """把 normalize/link 之后的表格元数据（续表标记等）回写到对应 block。"""
        tables_by_key = {(table.page, table.table): table for table in tables}
        for block in blocks:
            if block.block_type != "table":
                continue
            table = tables_by_key.get(
                (block.location.get("page", 0), block.location.get("table_index", 0))
            )
            if table is not None:
                block.metadata.update(table_to_block_metadata(table))

    # ------------------------------------------------------------------
    # OCR（可选路径）
    # ------------------------------------------------------------------

    def _run_ocr(self, path: Path) -> tuple[list[ArtifactBlock], dict]:
        """渲染页面 → PaddleOCR 文本框 → 行级 text_block（+ 可选表格结构识别）。"""
        from .ocr import (
            get_ocr_instance,
            group_ocr_text_boxes_into_rows,
            postprocess_ocr_text_boxes_with_report,
            resolve_model_root,
            run_ocr_on_path,
        )
        from .ocr.tables_ocr import extract_page_table_blocks
        from .textnorm import merge_transformations

        blocks: list[ArtifactBlock] = []
        meta: dict = {}

        model_root = self.ocr_options.model_root or resolve_model_root()
        try:
            with tempfile.TemporaryDirectory(prefix="hmbuddy-pdf-ocr-") as temp_dir:
                page_images = self._render_pdf_to_images(path, Path(temp_dir))
                ocr = get_ocr_instance(model_root, self.ocr_options.model_profile)
                path_ocr_results = [
                    run_ocr_on_path(image, ocr, progress_label=path.name)
                    for image in page_images
                ]

                page_index = 0
                transformations: list = []
                ocr_tables: list = []
                for page_number, page_text_boxes_list in enumerate(
                    path_ocr_results, start=1
                ):
                    line_index = 0
                    for page_text_boxes in page_text_boxes_list:
                        processed_boxes, page_transformations = (
                            postprocess_ocr_text_boxes_with_report(page_text_boxes)
                        )
                        transformations.extend(page_transformations)
                        # 按"行"分组输出（与文本层 PDF 的 text_block 粒度对齐）
                        for row_boxes in group_ocr_text_boxes_into_rows(
                            processed_boxes
                        ):
                            text = " ".join(box.text for box in row_boxes).strip()
                            if not text:
                                continue
                            row_top = min(box.box[1] for box in row_boxes)
                            blocks.append(
                                ArtifactBlock(
                                    "",
                                    "text_block",
                                    text,
                                    {"page": page_number, "line_index": line_index},
                                    {
                                        "origin": "ocr",
                                        "top": round(row_top, 2),
                                        "x0": round(
                                            min(box.box[0] for box in row_boxes), 2
                                        ),
                                    },
                                )
                            )
                            line_index += 1
                    page_index = page_number

                    if self.ocr_options.enable_table_ocr:
                        try:
                            ocr_tables.extend(
                                extract_page_table_blocks(
                                    page_text_boxes_list,
                                    page_images=page_images,
                                    model_root=model_root,
                                    resolved_page=page_number,
                                    first_table_index=1
                                    + sum(
                                        1
                                        for block in blocks
                                        if block.block_type == "table"
                                    ),
                                )
                            )
                        except Exception:
                            meta.setdefault("table_ocr_error", "本页表格结构识别失败")

                if ocr_tables:
                    link_pdf_table_continuations(ocr_tables)
                    for table in ocr_tables:
                        blocks.append(
                            ArtifactBlock(
                                "",
                                "table",
                                None,
                                {"page": table.page, "table_index": table.table},
                                table_to_block_metadata(table),
                            )
                        )

                # 按（页码, 纵向位置）稳定排序
                blocks.sort(
                    key=lambda block: (
                        block.location.get("page", 0),
                        block.metadata.get("top", 0.0),
                    )
                )
                meta = {
                    "ocr": {
                        "enabled": True,
                        "profile": self.ocr_options.model_profile,
                        "pages": page_index,
                        "table_ocr": self.ocr_options.enable_table_ocr,
                        "transformations": [
                            {
                                "rule_id": t.rule_id,
                                "version": t.version,
                                "count": t.count,
                            }
                            for t in merge_transformations(transformations)
                        ],
                    }
                }
        except Exception as exc:
            # OCR 失败不吞掉原有结果：保留 requires_ocr 标记并记录错误信息
            meta = {
                "ocr": {"enabled": True, "status": "error", "error": str(exc)[:300]}
            }
            meta["requires_ocr"] = True
            return blocks, meta
        return blocks, meta

    @staticmethod
    def _render_pdf_to_images(path: Path, output_dir: Path) -> list[Path]:
        try:
            import pypdfium2 as pdfium  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "缺少 pypdfium2，无法把 PDF 页面渲染为 OCR 图片。"
                "可安装 hmbuddy[ocr] 依赖组。"
            ) from exc

        rendered_paths: list[Path] = []
        pdf_document = pdfium.PdfDocument(str(path))
        try:
            for page_index in range(len(pdf_document)):
                page = pdf_document.get_page(page_index)
                try:
                    bitmap = page.render(scale=2.0)
                    image = bitmap.to_pil()
                finally:
                    page.close()
                rendered_path = output_dir / "pdf-page-{0:03d}.png".format(
                    page_index + 1
                )
                image.save(rendered_path)
                rendered_paths.append(rendered_path)
        finally:
            pdf_document.close()
        return rendered_paths
