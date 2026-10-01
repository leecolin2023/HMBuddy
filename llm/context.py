"""Artifact → LLM Context（规格第 17 节）。

Artifact 内部模型面向程序，Context Representation 面向 LLM，两者不混为一个对象。
本模块只按 block_type / location 渲染，不出现任何文件格式判断（P2）：
格式差异已在 Adapter 层被吸收为统一的 Block 流。
"""
from __future__ import annotations

from workspace.artifact import Artifact, ArtifactBlock

# 单个表格最多渲染的行数，超出截断并显式标注（避免长表格挤爆上下文）
MAX_TABLE_ROWS = 200


def artifact_to_context(artifact: Artifact, max_table_rows: int = MAX_TABLE_ROWS) -> str:
    lines: list[str] = [
        "[Document]",
        f"Name: {artifact.name}",
        f"Type: {artifact.artifact_type.upper()}",
        f"Path: {artifact.path}",
    ]
    title = artifact.metadata.get("title")
    if title:
        lines.append(f"Title: {title}")
    if artifact.metadata.get("requires_ocr"):
        lines.append("[Note] 该 PDF 无文本层（requires_ocr=true），文本内容可能缺失。")

    current_page = None
    for block in artifact.blocks:
        page = block.location.get("page")
        if page is not None and page != current_page:
            lines.append(f"[Page {page}]")
            current_page = page
        rendered = _render_block(block, max_table_rows)
        if rendered:
            lines.append(rendered)
    return "\n".join(lines)


def _render_block(block: ArtifactBlock, max_table_rows: int) -> str | None:
    block_type = block.block_type
    if block_type == "heading":
        return f"[Heading {block.metadata.get('level', '?')}] {block.text}"
    if block_type == "paragraph":
        return f"[Paragraph] {block.text}"
    if block_type == "list_item":
        return f"[List Item] {block.text}"
    if block_type == "slide":
        header = f"[Slide {block.location.get('slide')}] {block.text or ''}"
        return header.rstrip()
    if block_type == "textbox":
        return f"[Textbox] {block.text}"
    if block_type == "text_block":
        return f"[Text] {block.text}"
    if block_type == "image_reference":
        count = block.metadata.get("count", 1)
        return f"[Image Reference] x{count}" if count and count > 1 else "[Image Reference]"
    if block_type == "table":
        return _render_table(block, max_table_rows)
    if block.text:
        return f"[{block_type}] {block.text}"
    return f"[{block_type}]"


def _render_table(block: ArtifactBlock, max_table_rows: int) -> str:
    location = block.location
    where: list[str] = []
    if "sheet" in location:
        where.append(f"sheet={location['sheet']}")
    if "range" in location:
        where.append(f"range={location['range']}")
    if "page" in location:
        where.append(f"page={location['page']}")
    if "slide" in location:
        where.append(f"slide={location['slide']}")

    rows = block.metadata.get("cells") or []
    rows_count = block.metadata.get("rows", len(rows))
    columns_count = block.metadata.get("columns", 0)
    header = f"[Table {rows_count}x{columns_count}"
    if where:
        header += " | " + " ".join(where)
    header += "]"

    lines = [header]
    for row in rows[:max_table_rows]:
        lines.append("| " + " | ".join(_cell_str(cell) for cell in row) + " |")
    if len(rows) > max_table_rows:
        lines.append(f"...（表格共 {len(rows)} 行，已截断显示前 {max_table_rows} 行）")
    return "\n".join(lines)


def _cell_str(value) -> str:
    if value is None:
        return ""
    return str(value).replace("\n", " ").replace("|", "\\|")
