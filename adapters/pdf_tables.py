"""PDF 矢量表格引擎（移植自 fce/pdf_tables.py）。

与 fce 版的差异仅在几何采集层：fce 通过 pypdf 的 visitor 回调捕获 `re`
矩形与文本矩阵；本版改用 pdfplumber 的 lines/rects/words 原语（语义等价、
实现更直接、且能穿透描边矩形边框）。表格拼装算法——连通分量识别、
union-find 合并缺失边界的单元格（rowspan/colspan）、文本框归属、
表头识别、重复表头面板拆分、跨页续表链接——保持逐行保真移植。

坐标统一为"top 基准"（距页顶距离），与 pdfplumber 一致。
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .tables import ExtractedTable, TableCell, TableRow


PDF_VECTOR_LINE_MIN_LENGTH = 8.0
PDF_VECTOR_COORDINATE_TOLERANCE = 2.0
PDF_VECTOR_MAX_COLUMNS = 40
PDF_VECTOR_MAX_ROWS = 1000
PDF_HEADER_KEYWORDS = (
    "序号",
    "部门",
    "机构",
    "姓名",
    "职务",
    "职责",
    "电话",
    "手机",
    "地址",
    "楼层",
    "管理部门",
)


@dataclass(frozen=True)
class PdfHorizontalLine:
    x0: float
    x1: float
    y: float


@dataclass(frozen=True)
class PdfVerticalLine:
    x: float
    y0: float
    y1: float


@dataclass(frozen=True)
class PdfTableTextFragment:
    text: str
    x: float
    y: float
    font_size: float


# ---------------------------------------------------------------------------
# 几何采集（pdfplumber 原语）
# ---------------------------------------------------------------------------

def _rect_is_background(rect) -> bool:
    """纯背景色块（有填充无描边且不是细线条）不参与表格边界。"""
    fill = bool(rect.get("fill"))
    stroke = bool(rect.get("stroke"))
    width = abs(float(rect.get("x1", 0)) - float(rect.get("x0", 0)))
    height = abs(float(rect.get("bottom", 0)) - float(rect.get("top", 0)))
    return fill and not stroke and min(width, height) > 2.0


def _rect_border_lines(rect) -> Iterable[object]:
    x0 = float(rect.get("x0", 0))
    x1 = float(rect.get("x1", 0))
    top = float(rect.get("top", 0))
    bottom = float(rect.get("bottom", 0))
    return [
        PdfHorizontalLine(x0, x1, top),
        PdfHorizontalLine(x0, x1, bottom),
        PdfVerticalLine(x0, top, bottom),
        PdfVerticalLine(x1, top, bottom),
    ]


def _collect_page_lines(page) -> Tuple[List[PdfHorizontalLine], List[PdfVerticalLine]]:
    horizontal: List[PdfHorizontalLine] = []
    vertical: List[PdfVerticalLine] = []

    for line in page.lines or []:
        x0, x1 = float(line.get("x0", 0)), float(line.get("x1", 0))
        top, bottom = float(line.get("top", 0)), float(line.get("bottom", 0))
        if abs(bottom - top) <= 1.0 and abs(x1 - x0) >= PDF_VECTOR_LINE_MIN_LENGTH:
            horizontal.append(PdfHorizontalLine(x0, x1, (top + bottom) / 2.0))
        elif abs(x1 - x0) <= 1.0 and abs(bottom - top) >= PDF_VECTOR_LINE_MIN_LENGTH:
            vertical.append(PdfVerticalLine((x0 + x1) / 2.0, top, bottom))

    for rect in page.rects or []:
        if _rect_is_background(rect):
            continue
        for border in _rect_border_lines(rect):
            if isinstance(border, PdfHorizontalLine):
                if border.x1 - border.x0 >= PDF_VECTOR_LINE_MIN_LENGTH:
                    horizontal.append(border)
            else:
                if border.y1 - border.y0 >= PDF_VECTOR_LINE_MIN_LENGTH:
                    vertical.append(border)

    return horizontal, vertical


def _collect_page_fragments(page) -> List[PdfTableTextFragment]:
    fragments: List[PdfTableTextFragment] = []
    try:
        words = page.extract_words(extra_attrs=["size"]) or []
    except Exception:
        return []
    for word in words:
        text = str(word.get("text") or "").strip()
        if not text:
            continue
        try:
            font_size = float(word.get("size", 0.0))
        except (TypeError, ValueError):
            font_size = 0.0
        fragments.append(
            PdfTableTextFragment(
                text=text,
                x=float(word.get("x0", 0.0)),
                y=float(word.get("top", 0.0)),
                font_size=font_size if font_size > 0 else 10.0,
            )
        )
    return fragments


# ---------------------------------------------------------------------------
# 表格拼装（fce 算法保真移植）
# ---------------------------------------------------------------------------

def _cluster_values(values: Iterable[float], tolerance: float = 1.5) -> List[float]:
    clusters: List[List[float]] = []
    for value in sorted(values):
        if clusters and abs(value - (sum(clusters[-1]) / len(clusters[-1]))) <= tolerance:
            clusters[-1].append(value)
        else:
            clusters.append([value])
    return [sum(cluster) / len(cluster) for cluster in clusters]


def _dedupe_horizontal(lines: Sequence[PdfHorizontalLine]) -> List[PdfHorizontalLine]:
    grouped: List[List[PdfHorizontalLine]] = []
    for line in sorted(lines, key=lambda item: (item.y, item.x0, item.x1)):
        target: Optional[List[PdfHorizontalLine]] = None
        for group in reversed(grouped):
            if abs(group[0].y - line.y) <= 1.5:
                target = group
                break
            if line.y - group[0].y > 1.5:
                break
        if target is None:
            grouped.append([line])
        else:
            target.append(line)

    resolved: List[PdfHorizontalLine] = []
    for group in grouped:
        y = sum(item.y for item in group) / len(group)
        merged: List[List[float]] = []
        for item in sorted(group, key=lambda line: line.x0):
            if merged and item.x0 <= merged[-1][1] + 1.5:
                merged[-1][1] = max(merged[-1][1], item.x1)
            else:
                merged.append([item.x0, item.x1])
        resolved.extend(PdfHorizontalLine(x0, x1, y) for x0, x1 in merged)
    return resolved


def _dedupe_vertical(lines: Sequence[PdfVerticalLine]) -> List[PdfVerticalLine]:
    grouped: List[List[PdfVerticalLine]] = []
    for line in sorted(lines, key=lambda item: (item.x, item.y0, item.y1)):
        target: Optional[List[PdfVerticalLine]] = None
        for group in reversed(grouped):
            if abs(group[0].x - line.x) <= 1.5:
                target = group
                break
            if line.x - group[0].x > 1.5:
                break
        if target is None:
            grouped.append([line])
        else:
            target.append(line)

    resolved: List[PdfVerticalLine] = []
    for group in grouped:
        x = sum(item.x for item in group) / len(group)
        merged: List[List[float]] = []
        for item in sorted(group, key=lambda line: line.y0):
            if merged and item.y0 <= merged[-1][1] + 1.5:
                merged[-1][1] = max(merged[-1][1], item.y1)
            else:
                merged.append([item.y0, item.y1])
        resolved.extend(PdfVerticalLine(x, y0, y1) for y0, y1 in merged)
    return resolved


def _line_components(
    horizontal: Sequence[PdfHorizontalLine],
    vertical: Sequence[PdfVerticalLine],
) -> List[Tuple[List[PdfHorizontalLine], List[PdfVerticalLine]]]:
    h_to_v: Dict[int, List[int]] = {index: [] for index in range(len(horizontal))}
    v_to_h: Dict[int, List[int]] = {index: [] for index in range(len(vertical))}
    tolerance = PDF_VECTOR_COORDINATE_TOLERANCE
    for h_index, h_line in enumerate(horizontal):
        for v_index, v_line in enumerate(vertical):
            if (
                h_line.x0 - tolerance <= v_line.x <= h_line.x1 + tolerance
                and v_line.y0 - tolerance <= h_line.y <= v_line.y1 + tolerance
            ):
                h_to_v[h_index].append(v_index)
                v_to_h[v_index].append(h_index)

    components: List[Tuple[List[PdfHorizontalLine], List[PdfVerticalLine]]] = []
    visited_h: set[int] = set()
    visited_v: set[int] = set()
    for start_h in range(len(horizontal)):
        if start_h in visited_h or not h_to_v[start_h]:
            continue
        pending_h = [start_h]
        component_h: set[int] = set()
        component_v: set[int] = set()
        while pending_h:
            h_index = pending_h.pop()
            if h_index in component_h:
                continue
            component_h.add(h_index)
            visited_h.add(h_index)
            for v_index in h_to_v[h_index]:
                if v_index in component_v:
                    continue
                component_v.add(v_index)
                visited_v.add(v_index)
                for linked_h in v_to_h[v_index]:
                    if linked_h not in component_h:
                        pending_h.append(linked_h)
        if len(component_h) >= 3 and len(component_v) >= 3:
            components.append(
                (
                    [horizontal[index] for index in sorted(component_h)],
                    [vertical[index] for index in sorted(component_v)],
                )
            )
    return components


class _UnionFind:
    def __init__(self, size: int) -> None:
        self.parents = list(range(size))

    def find(self, value: int) -> int:
        while self.parents[value] != value:
            self.parents[value] = self.parents[self.parents[value]]
            value = self.parents[value]
        return value

    def union(self, left: int, right: int) -> None:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root != right_root:
            self.parents[right_root] = left_root


def _has_vertical_boundary(
    lines: Sequence[PdfVerticalLine],
    x: float,
    y: float,
) -> bool:
    tolerance = PDF_VECTOR_COORDINATE_TOLERANCE
    return any(
        abs(line.x - x) <= tolerance and line.y0 - tolerance <= y <= line.y1 + tolerance
        for line in lines
    )


def _has_horizontal_boundary(
    lines: Sequence[PdfHorizontalLine],
    y: float,
    x: float,
) -> bool:
    tolerance = PDF_VECTOR_COORDINATE_TOLERANCE
    return any(
        abs(line.y - y) <= tolerance and line.x0 - tolerance <= x <= line.x1 + tolerance
        for line in lines
    )


def _estimated_text_width(fragment: PdfTableTextFragment) -> float:
    width = 0.0
    for character in fragment.text:
        width += fragment.font_size * (0.55 if ord(character) < 128 else 1.0)
    return width


def _join_fragment_line(fragments: Sequence[PdfTableTextFragment]) -> str:
    parts: List[str] = []
    previous: Optional[PdfTableTextFragment] = None
    for fragment in sorted(fragments, key=lambda item: item.x):
        text = fragment.text.strip()
        if not text:
            continue
        if previous is not None and parts:
            gap = fragment.x - (previous.x + _estimated_text_width(previous))
            if (
                gap > max(previous.font_size, fragment.font_size) * 0.45
                and parts[-1][-1:].isascii()
                and text[:1].isascii()
                and parts[-1][-1:].isalnum()
                and text[:1].isalnum()
            ):
                parts.append(" ")
        parts.append(text)
        previous = fragment
    return "".join(parts).strip()


def _build_cell_text(fragments: Sequence[PdfTableTextFragment]) -> str:
    if not fragments:
        return ""
    font_sizes = [fragment.font_size for fragment in fragments if fragment.font_size > 0]
    average_font_size = sum(font_sizes) / len(font_sizes) if font_sizes else 8.0
    tolerance = max(1.5, min(average_font_size * 0.55, 4.0))
    grouped: List[List[PdfTableTextFragment]] = []
    for fragment in sorted(fragments, key=lambda item: (item.y, item.x)):
        if grouped and abs(fragment.y - (sum(item.y for item in grouped[-1]) / len(grouped[-1]))) <= tolerance:
            grouped[-1].append(fragment)
        else:
            grouped.append([fragment])
    return "\n".join(
        line
        for line in (_join_fragment_line(group) for group in grouped)
        if line
    ).strip()


def _header_score(row: TableRow, column_count: int) -> float:
    if len(row.cells) < 2:
        return -10.0
    texts = [cell.text.strip() for cell in row.cells if cell.text.strip()]
    if not texts:
        return -10.0
    coverage = sum(max(cell.colspan, 1) for cell in row.cells) / max(column_count, 1)
    keyword_count = sum(1 for keyword in PDF_HEADER_KEYWORDS if any(keyword in text for text in texts))
    short_ratio = sum(1 for text in texts if len(text) <= 20) / len(texts)
    return coverage + (keyword_count * 1.5) + short_ratio + (len(row.cells) * 0.1)


def _mark_header_row(table: ExtractedTable) -> None:
    candidates = table.rows[: min(len(table.rows), 8)]
    if not candidates:
        return
    best = max(candidates, key=lambda row: _header_score(row, table.column_count))
    if _header_score(best, table.column_count) < 2.0:
        return
    best.is_header = True
    table.repeated_header_row = best.index


def _table_from_component(
    page_number: int,
    table_index: int,
    horizontal: Sequence[PdfHorizontalLine],
    vertical: Sequence[PdfVerticalLine],
    fragments: Sequence[PdfTableTextFragment],
) -> Optional[ExtractedTable]:
    x_values = _cluster_values(line.x for line in vertical)
    y_values = _cluster_values(line.y for line in horizontal)
    if len(x_values) < 3 or len(y_values) < 3:
        return None
    column_count = len(x_values) - 1
    row_count = len(y_values) - 1
    if column_count > PDF_VECTOR_MAX_COLUMNS or row_count > PDF_VECTOR_MAX_ROWS:
        return None

    unit_count = row_count * column_count
    union_find = _UnionFind(unit_count)

    def unit_index(row: int, column: int) -> int:
        return (row * column_count) + column

    for row_index in range(row_count):
        y_mid = (y_values[row_index] + y_values[row_index + 1]) / 2.0
        for column_index in range(column_count):
            x_mid = (x_values[column_index] + x_values[column_index + 1]) / 2.0
            if column_index + 1 < column_count and not _has_vertical_boundary(
                vertical,
                x_values[column_index + 1],
                y_mid,
            ):
                union_find.union(
                    unit_index(row_index, column_index),
                    unit_index(row_index, column_index + 1),
                )
            if row_index + 1 < row_count and not _has_horizontal_boundary(
                horizontal,
                y_values[row_index + 1],
                x_mid,
            ):
                union_find.union(
                    unit_index(row_index, column_index),
                    unit_index(row_index + 1, column_index),
                )

    units_by_root: Dict[int, List[Tuple[int, int]]] = {}
    for row_index in range(row_count):
        for column_index in range(column_count):
            root = union_find.find(unit_index(row_index, column_index))
            units_by_root.setdefault(root, []).append((row_index, column_index))

    cells: List[TableCell] = []
    for units in units_by_root.values():
        min_row = min(item[0] for item in units)
        max_row = max(item[0] for item in units)
        min_column = min(item[1] for item in units)
        max_column = max(item[1] for item in units)
        bbox = (
            x_values[min_column],
            y_values[min_row],
            x_values[max_column + 1],
            y_values[max_row + 1],
        )
        cells.append(
            TableCell(
                row=min_row + 1,
                column=min_column + 1,
                text="",
                rowspan=(max_row - min_row) + 1,
                colspan=(max_column - min_column) + 1,
                bbox=tuple(round(value, 3) for value in bbox),  # type: ignore[arg-type]
            )
        )

    assigned_fragments: Dict[int, List[PdfTableTextFragment]] = {
        index: [] for index in range(len(cells))
    }
    for fragment in fragments:
        candidates = [
            index
            for index, cell in enumerate(cells)
            if cell.bbox[0] <= fragment.x < cell.bbox[2]
            and cell.bbox[1] <= fragment.y < cell.bbox[3]
        ]
        if not candidates:
            candidates = [
                index
                for index, cell in enumerate(cells)
                if cell.bbox[0] - 1.0 <= fragment.x <= cell.bbox[2] + 1.0
                and cell.bbox[1] - 2.0 <= fragment.y <= cell.bbox[3] + 2.0
            ]
        if not candidates:
            continue
        selected = min(
            candidates,
            key=lambda index: (
                abs(fragment.x - ((cells[index].bbox[0] + cells[index].bbox[2]) / 2.0))
                / max(cells[index].bbox[2] - cells[index].bbox[0], 1.0)
            )
            + (
                abs(fragment.y - ((cells[index].bbox[1] + cells[index].bbox[3]) / 2.0))
                / max(cells[index].bbox[3] - cells[index].bbox[1], 1.0)
            ),
        )
        assigned_fragments[selected].append(fragment)
    for index, cell in enumerate(cells):
        cell.text = _build_cell_text(assigned_fragments[index])

    rows = [
        TableRow(
            index=row_index,
            cells=sorted(
                [cell for cell in cells if cell.row == row_index],
                key=lambda cell: cell.column,
            ),
        )
        for row_index in range(1, row_count + 1)
    ]
    table = ExtractedTable(
        page=page_number,
        table=table_index,
        rows=rows,
        column_count=column_count,
        bbox=(
            round(x_values[0], 3),
            round(y_values[0], 3),
            round(x_values[-1], 3),
            round(y_values[-1], 3),
        ),
        extraction_method="pdf-vector-grid",
        confidence=0.98,
    )
    _mark_header_row(table)
    return table


def _normalize_header_text(text: str) -> str:
    return re.sub(r"[\s：:（）()、，,。.]", "", text or "").lower()


def _split_table_at_column(
    table: ExtractedTable,
    split_column: int,
) -> List[ExtractedTable]:
    if split_column <= 1 or split_column > table.column_count:
        return [table]
    results: List[ExtractedTable] = []
    all_cells = [cell for row in table.rows for cell in row.cells]
    for panel_index, (first_column, last_column) in enumerate(
        ((1, split_column - 1), (split_column, table.column_count)),
        start=1,
    ):
        panel_cells = [
            cell
            for cell in all_cells
            if cell.column >= first_column
            and cell.column + cell.colspan - 1 <= last_column
        ]
        if not panel_cells:
            continue
        x_boundaries = _cluster_values(
            value
            for cell in panel_cells
            for value in (cell.bbox[0], cell.bbox[2])
        )
        y_boundaries = _cluster_values(
            value
            for cell in panel_cells
            for value in (cell.bbox[1], cell.bbox[3])
        )
        normalized_cells: List[TableCell] = []
        for cell in panel_cells:
            x0 = min(range(len(x_boundaries)), key=lambda index: abs(x_boundaries[index] - cell.bbox[0]))
            x1 = min(range(len(x_boundaries)), key=lambda index: abs(x_boundaries[index] - cell.bbox[2]))
            y0 = min(range(len(y_boundaries)), key=lambda index: abs(y_boundaries[index] - cell.bbox[1]))
            y1 = min(range(len(y_boundaries)), key=lambda index: abs(y_boundaries[index] - cell.bbox[3]))
            normalized_cells.append(
                TableCell(
                    row=y0 + 1,
                    column=x0 + 1,
                    text=cell.text,
                    rowspan=max(y1 - y0, 1),
                    colspan=max(x1 - x0, 1),
                    bbox=cell.bbox,
                )
            )
        rows = [
            TableRow(
                index=row_index,
                cells=sorted(
                    [cell for cell in normalized_cells if cell.row == row_index],
                    key=lambda cell: cell.column,
                ),
            )
            for row_index in range(1, len(y_boundaries))
        ]
        panel = ExtractedTable(
            page=table.page,
            table=panel_index,
            rows=rows,
            column_count=max(len(x_boundaries) - 1, 0),
            bbox=(x_boundaries[0], y_boundaries[0], x_boundaries[-1], y_boundaries[-1]),
            extraction_method=table.extraction_method,
            confidence=table.confidence,
        )
        _mark_header_row(panel)
        results.append(panel)
    return results or [table]


def _split_repeated_header_panels(table: ExtractedTable) -> List[ExtractedTable]:
    header = next((row for row in table.rows if row.is_header), None)
    if header is None or table.column_count < 6:
        return [table]
    ordered = sorted(header.cells, key=lambda cell: cell.column)
    normalized = [_normalize_header_text(cell.text) for cell in ordered]
    split_column = 0
    for first_index, first_value in enumerate(normalized):
        if not first_value or not any(keyword in first_value for keyword in ("部门", "部室", "机构")):
            continue
        for second_index in range(first_index + 3, len(normalized)):
            if normalized[second_index] != first_value:
                continue
            left_values = [value for value in normalized[first_index:second_index] if value]
            right_values = [value for value in normalized[second_index:] if value]
            comparable_count = min(len(left_values), len(right_values))
            if comparable_count < 3:
                continue
            similarity = sum(
                1
                for index in range(comparable_count)
                if left_values[index] == right_values[index]
            ) / comparable_count
            if similarity >= 0.6:
                split_column = ordered[second_index].column
                break
        if split_column:
            break
    if not split_column:
        return [table]
    return _split_table_at_column(table, split_column)


def extract_pdf_vector_tables(page, page_number: int) -> List[ExtractedTable]:
    """从一页 PDF 中提取矢量线表格（含合并单元格与表头识别）。"""
    horizontal, vertical = _collect_page_lines(page)
    fragments = _collect_page_fragments(page)
    horizontal = _dedupe_horizontal(horizontal)
    vertical = _dedupe_vertical(vertical)
    components = _line_components(horizontal, vertical)
    tables: List[ExtractedTable] = []
    for component_index, (component_h, component_v) in enumerate(components, start=1):
        table = _table_from_component(
            page_number,
            component_index,
            component_h,
            component_v,
            fragments,
        )
        if table is not None:
            tables.extend(_split_repeated_header_panels(table))
    for table_index, table in enumerate(sorted(tables, key=lambda item: (item.bbox[1], item.bbox[0])), start=1):
        table.table = table_index
    return tables


def normalize_pdf_table_pages(tables: Sequence[ExtractedTable]) -> List[ExtractedTable]:
    normalized: List[ExtractedTable] = []
    previous_page_tables: List[ExtractedTable] = []
    for page_number in sorted({table.page for table in tables}):
        page_tables = sorted(
            [table for table in tables if table.page == page_number],
            key=lambda item: (item.bbox[1], item.bbox[0]),
        )
        if len(page_tables) == 1 and len(previous_page_tables) == 2:
            table = page_tables[0]
            previous_column_count = sum(item.column_count for item in previous_page_tables)
            if table.column_count == previous_column_count:
                page_tables = _split_table_at_column(
                    table,
                    previous_page_tables[0].column_count + 1,
                )
        for table_index, table in enumerate(page_tables, start=1):
            table.table = table_index
        normalized.extend(page_tables)
        previous_page_tables = page_tables
    return normalized


def _header_signature(table: ExtractedTable) -> Tuple[str, ...]:
    header = next((row for row in table.rows if row.is_header), None)
    if header is None:
        return ()
    return tuple(
        _normalize_header_text(cell.text)
        for cell in sorted(header.cells, key=lambda item: item.column)
        if cell.text.strip()
    )


def _column_width_profile(table: ExtractedTable) -> Tuple[float, ...]:
    width = max(table.bbox[2] - table.bbox[0], 1.0)
    header = next((row for row in table.rows if row.is_header), None)
    cells = header.cells if header is not None else (table.rows[0].cells if table.rows else [])
    return tuple(round((cell.bbox[2] - cell.bbox[0]) / width, 2) for cell in cells)


def link_pdf_table_continuations(tables: Sequence[ExtractedTable]) -> None:
    """跨页续表链接：相邻页同列数且表头签名或列宽剖面一致的表格串成一条链。"""
    previous_page_tables: List[ExtractedTable] = []
    previous_page = 0
    chain_index = 0
    for table in sorted(tables, key=lambda item: (item.page, item.table)):
        if table.page != previous_page:
            previous_page_tables = [
                item for item in tables if item.page == table.page - 1
            ]
            previous_page = table.page
        signature = _header_signature(table)
        profile = _column_width_profile(table)
        match = next(
            (
                previous
                for previous in previous_page_tables
                if previous.table == table.table
                and previous.column_count == table.column_count
                and (
                    (signature and signature == _header_signature(previous))
                    or (profile and profile == _column_width_profile(previous))
                )
            ),
            None,
        )
        if match is not None:
            table.continues_from_previous = True
            table.continuation_id = match.continuation_id
            match.continued_on_next = True
            continue
        chain_index += 1
        table.continuation_id = "table-chain-{0}".format(chain_index)
