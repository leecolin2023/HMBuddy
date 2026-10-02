"""Presentation helpers for the desktop shell.

Kept free of Tkinter so formatting can be unit-tested in headless environments.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime


BLOCK_TYPE_LABELS = {
    "heading": "Heading",
    "paragraph": "Paragraph",
    "list_item": "ListItem",
    "table": "Table",
    "image_reference": "Image",
    "text_block": "TextBlock",
    "textbox": "Textbox",
    "slide": "Slide",
}


def format_file_size(size: int) -> str:
    value = float(size)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} GB"


def format_datetime(value: datetime) -> str:
    return value.astimezone().strftime("%Y-%m-%d %H:%M")


def artifact_summary_text(artifact) -> str:
    lines = [
        f"文件：{artifact.name}",
        f"类型：{artifact.artifact_type.upper()}",
        f"路径：{artifact.path}",
    ]

    title = artifact.metadata.get("title")
    if title:
        lines.append(f"标题：{title}")

    counts = Counter(block.block_type for block in artifact.blocks)
    if counts:
        lines.append("")
        lines.append("结构：")
        for block_type, count in sorted(counts.items()):
            label = BLOCK_TYPE_LABELS.get(block_type, block_type)
            lines.append(f"  - {label}: {count}")

    sheets = artifact.metadata.get("sheets")
    if sheets:
        lines.append("")
        lines.append("Sheets：")
        for sheet in sheets:
            name = sheet.get("name", "(unnamed)") if isinstance(sheet, dict) else str(sheet)
            lines.append(f"  - {name}")

    page_count = artifact.metadata.get("page_count")
    if page_count is not None:
        lines.append(f"Pages：{page_count}")

    provenance = artifact.provenance or {}
    lines.extend(
        [
            "",
            "解析信息：",
            f"  - Adapter: {provenance.get('adapter', '?')}",
            f"  - 耗时: {provenance.get('parse_duration_ms', '?')} ms",
            f"  - Artifact ID: {artifact.artifact_id}",
        ]
    )

    preview = (artifact.content or "").strip()
    if preview:
        lines.extend(["", "内容预览：", preview[:3000]])
        if len(preview) > 3000:
            lines.append("…（预览已截断）")

    return "\n".join(lines)
