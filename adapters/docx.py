"""DOCX Adapter（规格第 11 节）。

保留 heading（含 level）/ paragraph / 基础列表 / table（rows、columns、cells）/
图片位置引用，并保证原始阅读顺序不乱（最低要求）。
"""
from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

from workspace.artifact import Artifact, ArtifactBlock
from workspace.errors import EncryptedArtifactError

from .base import ArtifactAdapter, assign_block_ids, ensure_not_ole

_HEADING_NAME_RE = re.compile(r"^(?:heading|标题|標題)\s*(\d+)$", re.IGNORECASE)
_HEADING_ID_RE = re.compile(r"^(?:heading|标题|標題)(\d+)$", re.IGNORECASE)


def _heading_level(paragraph: Paragraph) -> int | None:
    """识别标题级别：优先样式名（Heading 1 / 标题 1），其次 outlineLvl。"""
    try:
        style = paragraph.style
    except Exception:
        style = None
    if style is not None:
        name = (style.name or "").strip()
        matched = _HEADING_NAME_RE.match(name)
        if matched:
            return int(matched.group(1))
        style_id = getattr(style, "style_id", "") or ""
        matched = _HEADING_ID_RE.match(style_id)
        if matched:
            return int(matched.group(1))
    p_pr = paragraph._p.pPr
    if p_pr is not None:
        outline = p_pr.find(qn("w:outlineLvl"))
        if outline is not None and outline.get(qn("w:val")) is not None:
            try:
                return int(outline.get(qn("w:val"))) + 1
            except ValueError:
                return None
    return None


def _list_level(paragraph: Paragraph) -> int | None:
    """识别基础列表：段落级 numPr，或样式名含 List（List Bullet / List Number）。"""
    try:
        style_name = (paragraph.style.name or "") if paragraph.style is not None else ""
    except Exception:
        style_name = ""
    p_pr = paragraph._p.pPr
    if p_pr is not None:
        num_pr = p_pr.find(qn("w:numPr"))
        if num_pr is not None:
            ilvl = num_pr.find(qn("w:ilvl"))
            if ilvl is not None and ilvl.get(qn("w:val")) is not None:
                try:
                    return int(ilvl.get(qn("w:val")))
                except ValueError:
                    return 0
            return 0
    if "list" in style_name.lower():
        return 0
    return None


def _paragraph_images(doc, paragraph: Paragraph) -> list[str]:
    """返回该段落引用的图片在包内的路径（如 /word/media/image1.png）。"""
    try:
        rids = paragraph._p.xpath(".//a:blip/@r:embed")
    except Exception:
        return []
    names: list[str] = []
    for rid in rids or []:
        part = doc.part.related_parts.get(rid)
        if part is not None:
            names.append(str(part.partname))
    return names


class DocxAdapter(ArtifactAdapter):
    artifact_type = "docx"
    supported_extensions = (".docx",)
    parser_library = "python-docx"

    def read(self, path: Path, artifact_id: str) -> Artifact:
        ensure_not_ole(path, self)
        doc = Document(str(path))

        blocks: list[ArtifactBlock] = []
        counts = {
            "heading": 0,
            "paragraph": 0,
            "list_item": 0,
            "table": 0,
            "image_reference": 0,
        }
        paragraph_index = 0
        table_index = 0
        first_heading: str | None = None

        # 直接按 body XML 子元素顺序遍历，保证 paragraph 与 table 的原始阅读顺序
        for child in doc.element.body.iterchildren():
            if child.tag == qn("w:p"):
                paragraph = Paragraph(child, doc)
                paragraph_index += 1
                text = paragraph.text.strip()
                images = _paragraph_images(doc, paragraph)
                if images:
                    counts["image_reference"] += 1
                    blocks.append(
                        ArtifactBlock(
                            "",
                            "image_reference",
                            None,
                            {"paragraph_index": paragraph_index},
                            {"count": len(images), "images": images},
                        )
                    )
                if not text:
                    continue
                level = _heading_level(paragraph)
                if level is not None:
                    counts["heading"] += 1
                    if first_heading is None:
                        first_heading = text
                    blocks.append(
                        ArtifactBlock(
                            "",
                            "heading",
                            text,
                            {"paragraph_index": paragraph_index},
                            {"level": level},
                        )
                    )
                    continue
                list_level = _list_level(paragraph)
                if list_level is not None:
                    counts["list_item"] += 1
                    blocks.append(
                        ArtifactBlock(
                            "",
                            "list_item",
                            text,
                            {"paragraph_index": paragraph_index},
                            {"list_level": list_level},
                        )
                    )
                    continue
                counts["paragraph"] += 1
                blocks.append(
                    ArtifactBlock(
                        "", "paragraph", text, {"paragraph_index": paragraph_index}, {}
                    )
                )
            elif child.tag == qn("w:tbl"):
                table = Table(child, doc)
                table_index += 1
                cells = [
                    [cell.text.strip() for cell in row.cells] for row in table.rows
                ]
                counts["table"] += 1
                blocks.append(
                    ArtifactBlock(
                        "",
                        "table",
                        None,
                        {"table_index": table_index},
                        {
                            "rows": len(cells),
                            "columns": len(cells[0]) if cells else 0,
                            "cells": cells,
                        },
                    )
                )

        core = doc.core_properties
        core_properties = {
            "title": core.title,
            "author": core.author,
            "subject": core.subject,
            "created": core.created.isoformat() if core.created else None,
            "modified": core.modified.isoformat() if core.modified else None,
        }
        sections = [
            {
                "index": index,
                "orientation": str(section.orientation),
                "page_width": section.page_width,
                "page_height": section.page_height,
            }
            for index, section in enumerate(doc.sections, start=1)
        ]
        metadata = {
            "title": core.title or first_heading,
            "heading_count": counts["heading"],
            "paragraph_count": counts["paragraph"],
            "list_item_count": counts["list_item"],
            "table_count": counts["table"],
            "image_reference_count": counts["image_reference"],
            "section_count": len(sections),
            "sections": sections,
            "core_properties": core_properties,
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
