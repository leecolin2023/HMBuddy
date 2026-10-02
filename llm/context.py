"""Artifact → LLM Context（规格第 17 节 + Phase 1.1 第 25 节 Context Hardening）。

Artifact 内部模型面向程序，Context Representation 面向 LLM，两者不混为一个对象。
本模块只按 block_type / location 渲染，不出现任何文件格式判断（P2）。

Phase 1.1 收口（FR-C01 ~ C04）：
- 全局预算：max_chars / max_blocks / max_table_rows，截断显式可观察；
- XLSX 解析期截断标记（rows/columns/cells_truncated）必须进入 Context；
- PDF 页级 OCR 标记（page-level requires_ocr）；
- 绝对路径默认不进入 LLM Context（仅 name / artifact_id / 可选相对路径）。
"""
from __future__ import annotations

from dataclasses import dataclass, field

from workspace.artifact import Artifact, ArtifactBlock

# 单个表格最多渲染的行数，超出截断并显式标注
MAX_TABLE_ROWS = 200


@dataclass
class ContextBuildResult:
    """build_context 的结构化返回：截断与省略必须可观察（AC-09）。"""

    text: str
    truncated: bool = False
    omitted_blocks: int = 0
    reason: str | None = None
    warnings: list[str] = field(default_factory=list)


def build_context(
    artifact: Artifact,
    max_table_rows: int = MAX_TABLE_ROWS,
    max_chars: int | None = None,
    max_blocks: int | None = None,
    relative_path: str | None = None,
) -> ContextBuildResult:
    warnings: list[str] = []
    lines: list[str] = [
        "[Document]",
        f"Name: {artifact.name}",
        f"Type: {artifact.artifact_type.upper()}",
        f"Artifact ID: {artifact.artifact_id}",
    ]
    if relative_path:
        lines.append(f"Relative Path: {relative_path}")
    title = artifact.metadata.get("title")
    if title:
        lines.append(f"Title: {title}")
    if artifact.metadata.get("requires_ocr"):
        lines.append("[Note] 该 PDF 无文本层（requires_ocr=true），文本内容可能缺失。")

    # FR-C03：页级 OCR 标记（PDF adapter 提供 pages[].requires_ocr）
    pages_meta = {
        page.get("page"): page
        for page in artifact.metadata.get("pages", [])
        if isinstance(page, dict)
    }

    current_page = None
    consumed = 0
    omitted_blocks = 0
    truncated = False
    reason: str | None = None
    char_budget = max_chars

    def char_budget_exceeded(next_text: str) -> bool:
        if char_budget is None:
            return False
        return len("\n".join(lines)) + len(next_text) > char_budget

    for block in artifact.blocks:
        if max_blocks is not None and consumed >= max_blocks:
            # 不在此累加：循环结束后统一以 总块数-已消费 计算省略数
            truncated = True
            reason = f"max_blocks={max_blocks} reached"
            continue
        page = block.location.get("page")
        if page is not None and page != current_page:
            header = f"[Page {page}]"
            if char_budget_exceeded(header):
                truncated = True
                reason = f"max_chars={char_budget} reached"
                break
            lines.append(header)
            current_page = page
            page_info = pages_meta.get(page)
            if page_info and page_info.get("requires_ocr"):
                lines.append(
                    f"[Note] 第 {page} 页无文本层（requires_ocr=true），该页文本可能缺失。"
                )

        rendered = _render_block(block, max_table_rows, warnings)
        if rendered is None:
            consumed += 1
            continue
        if char_budget_exceeded(rendered):
            truncated = True
            reason = f"max_chars={char_budget} reached"
            break
        lines.append(rendered)
        consumed += 1

    if truncated:
        omitted_blocks = max(len(artifact.blocks) - consumed, 0)

    text = "\n".join(lines)
    if truncated:
        marker = (
            f"[Context Truncated] truncated=true omitted_blocks={omitted_blocks} "
            f"reason={reason}"
        )
        text = "\n".join([text, marker])
        warnings.append(f"context truncated: {reason} (omitted_blocks={omitted_blocks})")
    return ContextBuildResult(
        text=text,
        truncated=truncated,
        omitted_blocks=omitted_blocks,
        reason=reason,
        warnings=warnings,
    )


def artifact_to_context(
    artifact: Artifact,
    max_table_rows: int = MAX_TABLE_ROWS,
    max_chars: int | None = None,
    max_blocks: int | None = None,
    relative_path: str | None = None,
) -> str:
    """向后兼容入口：只返回 Context 文本（需要截断详情时用 build_context）。"""
    return build_context(
        artifact,
        max_table_rows=max_table_rows,
        max_chars=max_chars,
        max_blocks=max_blocks,
        relative_path=relative_path,
    ).text


def _render_block(
    block: ArtifactBlock,
    max_table_rows: int,
    warnings: list[str],
) -> str | None:
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
        return _render_table(block, max_table_rows, warnings)
    if block.text:
        return f"[{block_type}] {block.text}"
    return f"[{block_type}]"


def _render_table(block: ArtifactBlock, max_table_rows: int, warnings: list[str]) -> str:
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
    if block.metadata.get("continues_from_previous"):
        header += " | 续上一页表格"
    header += "]"

    lines = [header]
    for row in rows[:max_table_rows]:
        lines.append("| " + " | ".join(_cell_str(cell) for cell in row) + " |")
    if len(rows) > max_table_rows:
        lines.append(f"...（表格共 {len(rows)} 行，已截断显示前 {max_table_rows} 行）")
        warnings.append(
            f"table at {location or 'unknown'}: 渲染行数超过 max_table_rows={max_table_rows}，已截断"
        )

    # FR-C02：解析期截断必须可见，模型不得误以为看到了整表
    truncation_flags = [
        ("rows_truncated", "行"),
        ("columns_truncated", "列"),
        ("cells_truncated", "单元格记录"),
    ]
    for flag_key, label in truncation_flags:
        if block.metadata.get(flag_key):
            note = f"[Note] 本表在解析阶段已被截断（{flag_key}=true，{label}未完整读取）。"
            lines.append(note)
            warnings.append(f"table at {location or 'unknown'}: {flag_key}=true")

    if block.metadata.get("continued_on_next"):
        lines.append("（表格在下一页继续）")
    return "\n".join(lines)


def _cell_str(value) -> str:
    if value is None:
        return ""
    return str(value).replace("\n", " ").replace("|", "\\|")
