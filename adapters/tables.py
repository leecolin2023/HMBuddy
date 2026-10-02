"""统一表格契约（移植自 fce/contracts/table.py）与 ArtifactBlock 元数据转换。

所有 Adapter 的表格最终都落成 ArtifactBlock(block_type="table")，metadata 同时携带：
- cells: 合并展开后的 rows×columns 文本网格（渲染/兼容用）
- cells_merged: 存在跨行/跨列时的锚点单元格记录（row/column/rowspan/colspan/text）
- extraction_method / confidence: 提取来源与置信度（provenance 精神）
- 表头与跨页续表信息（repeated_header_row / continuation_id / ...）
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Tuple

TableBoundingBox = Tuple[float, float, float, float]


@dataclass
class TableCell:
    row: int
    column: int
    text: str = ""
    rowspan: int = 1
    colspan: int = 1
    bbox: TableBoundingBox = (0.0, 0.0, 0.0, 0.0)


@dataclass
class TableRow:
    index: int
    cells: List[TableCell] = field(default_factory=list)
    is_header: bool = False


@dataclass
class ExtractedTable:
    """与具体格式无关的表格表达；page 字段沿用 fce 命名（非 PDF 表格填 0）。"""

    page: int
    table: int
    rows: List[TableRow] = field(default_factory=list)
    column_count: int = 0
    bbox: TableBoundingBox = (0.0, 0.0, 0.0, 0.0)
    extraction_method: str = ""
    confidence: float = 0.0
    continuation_id: str = ""
    continues_from_previous: bool = False
    continued_on_next: bool = False
    repeated_header_row: int = 0

    def to_grid(self) -> List[List[str]]:
        """把 span 单元格展开成 rows×columns 文本网格；非锚点位置为空串。"""
        row_count = len(self.rows)
        column_count = self.column_count or (
            max((cell.column + cell.colspan - 1 for row in self.rows for cell in row.cells), default=0)
        )
        grid = [["" for _ in range(column_count)] for _ in range(row_count)]
        for row in self.rows:
            for cell in row.cells:
                row_index = cell.row - 1
                column_index = cell.column - 1
                if 0 <= row_index < row_count and 0 <= column_index < column_count:
                    grid[row_index][column_index] = cell.text
        return grid

    def has_merged_cells(self) -> bool:
        return any(
            cell.rowspan > 1 or cell.colspan > 1
            for row in self.rows
            for cell in row.cells
        )


def table_to_block_metadata(table: ExtractedTable) -> dict[str, Any]:
    """ExtractedTable → ArtifactBlock.metadata（见模块 docstring）。"""
    metadata: dict[str, Any] = {
        "rows": len(table.rows),
        "columns": table.column_count,
        "cells": table.to_grid(),
    }
    if table.has_merged_cells():
        metadata["cells_merged"] = [
            {
                "row": cell.row,
                "column": cell.column,
                "rowspan": cell.rowspan,
                "colspan": cell.colspan,
                "text": cell.text,
            }
            for row in table.rows
            for cell in row.cells
            if cell.rowspan > 1 or cell.colspan > 1
        ]
    if table.extraction_method:
        metadata["extraction_method"] = table.extraction_method
    if table.confidence:
        metadata["confidence"] = round(table.confidence, 3)
    if table.repeated_header_row:
        metadata["repeated_header_row"] = table.repeated_header_row
    if table.continuation_id:
        metadata["continuation_id"] = table.continuation_id
    if table.continues_from_previous:
        metadata["continues_from_previous"] = True
    if table.continued_on_next:
        metadata["continued_on_next"] = True
    return metadata


def grid_to_table_metadata(
    cells: List[List[str]],
    *,
    merged_cells: List[str] | None = None,
    extraction_method: str = "",
) -> dict[str, Any]:
    """简单网格（docx/xlsx/pptx 现有路径）→ 表格 block metadata。"""
    metadata: dict[str, Any] = {
        "rows": len(cells),
        "columns": len(cells[0]) if cells else 0,
        "cells": cells,
    }
    if merged_cells:
        metadata["merged_cells"] = merged_cells
    if extraction_method:
        metadata["extraction_method"] = extraction_method
    return metadata
