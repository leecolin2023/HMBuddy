"""文本与单元格规范化（部分移植自 fce/extractors.py）。

TextTransformation 记录"对原始文本做了哪条规则、多少次改写"，为审计与
Diff（第二阶段）保留基础。
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable, List


@dataclass(frozen=True)
class TextTransformation:
    rule_id: str
    version: str = "1"
    count: int = 1


def merge_transformations(
    transformations: Iterable[TextTransformation],
) -> List[TextTransformation]:
    counts: dict[tuple[str, str], int] = {}
    for item in transformations:
        key = (item.rule_id, item.version)
        counts[key] = counts.get(key, 0) + max(int(item.count), 0)
    return [
        TextTransformation(rule_id=rule_id, version=version, count=count)
        for (rule_id, version), count in sorted(counts.items())
        if count > 0
    ]


def collapse_cell_text(text: str) -> str:
    """单元格内多行折叠成" / "连接（fce: collapse_spreadsheet_cell_text）。"""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    parts = [part.strip() for part in normalized.split("\n") if part.strip()]
    if parts:
        return " / ".join(parts)
    return normalized.strip()


def normalize_spreadsheet_value(value: object) -> str:
    """电子表格原始值 → 规范文本（布尔/数字/日期/文本，fce 同名函数移植）。"""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return format(value, "g")
    if isinstance(value, datetime):
        if (
            value.hour == 0
            and value.minute == 0
            and value.second == 0
            and value.microsecond == 0
        ):
            return value.date().isoformat()
        return value.replace(microsecond=0).isoformat(sep=" ")
    if isinstance(value, date):
        return value.isoformat()
    return collapse_cell_text(str(value))
