"""表格结构识别（移植自 fce/extractors.py 的表格 OCR 部分）。

依赖 paddlex + SLANet_plus 模型目录，全部懒加载；仅在 enable_table_ocr=True
且 OCR 文本框呈表格形态时才会被调用。HTML 表格解析为纯标准库实现。
"""
from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Any, Dict, List, Optional

from ..tables import ExtractedTable, TableCell, TableRow
from .engine import DEFAULT_OCR_MODEL_PROFILE, resolve_model_root
from .geometry import OcrTextBox, group_ocr_text_boxes_into_rows

_TABLE_OCR_INSTANCE = None
_TABLE_OCR_MODEL_ROOT = None

PDF_TABLE_MIN_ROWS = 2
PDF_TABLE_MIN_COLUMNS = 2
TABLE_STRUCTURE_MODEL_SUBDIR = "SLANet_plus_infer"


# ---------------------------------------------------------------------------
# HTML 表格解析（表格结构识别输出的 pred_html → 结构化表格）
# ---------------------------------------------------------------------------

@dataclass
class _HtmlTableCell:
    text: str
    colspan: int = 1
    rowspan: int = 1


class TableHtmlParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._rows: List[List[_HtmlTableCell]] = []
        self._current_row: Optional[List[_HtmlTableCell]] = None
        self._current_cell: Optional[_HtmlTableCell] = None
        self._cell_parts: List[str] = []
        self._table_depth = 0

    @property
    def rows(self) -> List[List[_HtmlTableCell]]:
        return self._rows

    def handle_starttag(self, tag: str, attrs: List[tuple[str, Optional[str]]]) -> None:
        normalized_tag = tag.lower()
        if normalized_tag == "table":
            self._table_depth += 1
            return
        if self._table_depth <= 0:
            return

        attrs_dict = {key.lower(): (value or "") for key, value in attrs}
        if normalized_tag == "tr":
            self._current_row = []
            return
        if normalized_tag in ("td", "th"):
            self._current_cell = _HtmlTableCell(
                text="",
                colspan=_safe_positive_int(attrs_dict.get("colspan")),
                rowspan=_safe_positive_int(attrs_dict.get("rowspan")),
            )
            self._cell_parts = []
            return
        if normalized_tag == "br" and self._current_cell is not None:
            self._cell_parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        normalized_tag = tag.lower()
        if normalized_tag == "table":
            if self._table_depth > 0:
                self._table_depth -= 1
            return
        if self._table_depth <= 0:
            return

        if normalized_tag in ("td", "th") and self._current_cell is not None:
            self._current_cell.text = " ".join("".join(self._cell_parts).split())
            if self._current_row is not None:
                self._current_row.append(self._current_cell)
            self._current_cell = None
            self._cell_parts = []
            return
        if normalized_tag == "tr" and self._current_row is not None:
            if self._current_row:
                self._rows.append(self._current_row)
            self._current_row = None

    def handle_data(self, data: str) -> None:
        if self._current_cell is not None:
            self._cell_parts.append(data)


def _safe_positive_int(value: object, default: int = 1) -> int:
    try:
        parsed = int(str(value or "").strip())
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def normalize_html_table_rows(rows: List[List[_HtmlTableCell]]) -> List[List[str]]:
    """按 rowspan/colspan 展开成规则网格。"""
    occupied: Dict[int, Dict[int, str]] = {}
    normalized_rows: List[List[str]] = []

    for row_index, cells in enumerate(rows):
        occupied.setdefault(row_index, {})
        column_index = 0
        for cell in cells:
            while column_index in occupied[row_index]:
                column_index += 1

            for row_offset in range(cell.rowspan):
                target_row = row_index + row_offset
                occupied.setdefault(target_row, {})
                for column_offset in range(cell.colspan):
                    target_column = column_index + column_offset
                    occupied[target_row][target_column] = (
                        cell.text if row_offset == 0 and column_offset == 0 else ""
                    )
            column_index += cell.colspan

        row_map = occupied.get(row_index, {})
        if not row_map:
            continue
        row_values = [
            row_map.get(column_position, "")
            for column_position in range(0, max(row_map) + 1)
        ]
        while row_values and not row_values[-1]:
            row_values.pop()
        if row_values and any(value for value in row_values):
            normalized_rows.append(row_values)

    return normalized_rows


def parse_html_table_rows(html: str) -> List[List[str]]:
    parser = TableHtmlParser()
    parser.feed(html or "")
    parser.close()
    return normalize_html_table_rows(parser.rows)


def build_extracted_table_from_html(
    html: str,
    *,
    page: int,
    table_index: int,
) -> ExtractedTable:
    parser = TableHtmlParser()
    parser.feed(str(html or ""))
    occupied_until: Dict[int, int] = {}
    rows: List[TableRow] = []
    max_column = 0
    for row_index, source_cells in enumerate(parser.rows, start=1):
        column = 1
        cells: List[TableCell] = []
        for source_cell in source_cells:
            while occupied_until.get(column, 0) >= row_index:
                column += 1
            colspan = max(int(source_cell.colspan), 1)
            rowspan = max(int(source_cell.rowspan), 1)
            cell = TableCell(
                row=row_index,
                column=column,
                text=" ".join(source_cell.text.split()),
                rowspan=rowspan,
                colspan=colspan,
            )
            cells.append(cell)
            if rowspan > 1:
                for occupied_column in range(column, column + colspan):
                    occupied_until[occupied_column] = row_index + rowspan - 1
            max_column = max(max_column, column + colspan - 1)
            column += colspan
        rows.append(TableRow(index=row_index, cells=cells, is_header=row_index == 1))
    return ExtractedTable(
        page=page,
        table=table_index,
        rows=rows,
        column_count=max_column,
        extraction_method="paddle-table-structure",
        confidence=0.85,
        repeated_header_row=1 if rows else 0,
    )


def extract_tables_from_result(
    result: Any,
    *,
    page: int,
    first_table_index: int = 1,
) -> List[ExtractedTable]:
    if not isinstance(result, dict):
        return []
    tables: List[ExtractedTable] = []
    for offset, table_result in enumerate(result.get("table_res_list", [])):
        if not isinstance(table_result, dict):
            continue
        table_html = str(table_result.get("pred_html") or "").strip()
        if not table_html:
            continue
        table = build_extracted_table_from_html(
            table_html,
            page=page,
            table_index=first_table_index + offset,
        )
        if table.rows:
            tables.append(table)
    return tables


# ---------------------------------------------------------------------------
# OCR 行形态判断 + paddlex 表格结构识别管线（懒加载）
# ---------------------------------------------------------------------------

def ocr_rows_look_like_table(rows: List[List[OcrTextBox]]) -> bool:
    if len(rows) < PDF_TABLE_MIN_ROWS:
        return False

    max_column_count = max(len(row) for row in rows)
    if max_column_count < PDF_TABLE_MIN_COLUMNS:
        return False

    stable_columns = 0
    for column_index in range(min(max_column_count, 4)):
        positions = [row[column_index].box[0] for row in rows if len(row) > column_index]
        if len(positions) >= PDF_TABLE_MIN_ROWS and max(positions) - min(positions) <= 48.0:
            stable_columns += 1
    return stable_columns >= PDF_TABLE_MIN_COLUMNS


def build_table_pipeline_config(model_root) -> Dict[str, object]:
    table_model_path = model_root / TABLE_STRUCTURE_MODEL_SUBDIR
    return {
        "pipeline_name": "table_recognition",
        "use_doc_preprocessor": False,
        "use_layout_detection": False,
        "use_ocr_model": False,
        "SubModules": {
            "TableStructureRecognition": {
                "module_name": "table_structure_recognition",
                "model_name": "SLANet_plus",
                "model_dir": str(table_model_path),
            },
        },
    }


def get_table_ocr_instance(model_root):
    global _TABLE_OCR_INSTANCE, _TABLE_OCR_MODEL_ROOT

    if model_root is None:
        model_root = resolve_model_root()
    if model_root is None:
        raise RuntimeError("未找到表格 OCR 模型目录。请设置 HMBUDDY_MODEL_DIR 或放入 ./models。")

    resolved_root = str(model_root.resolve())
    if _TABLE_OCR_INSTANCE is not None and _TABLE_OCR_MODEL_ROOT == resolved_root:
        return _TABLE_OCR_INSTANCE

    table_model_path = model_root / TABLE_STRUCTURE_MODEL_SUBDIR
    if not table_model_path.exists():
        raise RuntimeError("表格 OCR 模型目录不完整：{0}".format(table_model_path))

    try:
        from paddlex import create_pipeline  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "缺少 paddlex，无法执行表格结构识别。请安装 paddlex[ocr] 对应依赖。"
        ) from exc

    try:
        _TABLE_OCR_INSTANCE = create_pipeline(config=build_table_pipeline_config(model_root))
    except Exception as exc:
        raise RuntimeError("表格 OCR 初始化失败：{0}".format(exc)) from exc

    _TABLE_OCR_MODEL_ROOT = resolved_root
    return _TABLE_OCR_INSTANCE


def build_ocr_result_payload(image_array: Any, text_boxes: List[OcrTextBox]) -> Dict[str, object]:
    return {
        "rec_polys": [item.polygon for item in text_boxes],
        "rec_texts": [item.text for item in text_boxes],
        "rec_scores": [item.score for item in text_boxes],
        "rec_boxes": [item.box for item in text_boxes],
        "doc_preprocessor_res": {"output_img": image_array},
    }


def load_image_array(path) -> Any:
    try:
        import numpy as np  # type: ignore
        from PIL import Image  # type: ignore
    except ImportError as exc:
        raise RuntimeError("缺少 pillow/numpy，无法加载表格 OCR 图片。") from exc

    image = Image.open(path).convert("RGB")
    rgb_array = np.array(image)
    return rgb_array[:, :, ::-1].copy()


def extract_page_table_blocks(
    page_text_boxes_list: List[List[OcrTextBox]],
    *,
    page_images: List,
    model_root,
    resolved_page: int,
    first_table_index: int,
    progress_func=None,
) -> List[ExtractedTable]:
    """对一页（可能已分片）的 OCR 文本框执行表格结构识别，返回结构化表格。"""
    pipeline = None
    tables: List[ExtractedTable] = []
    next_table_index = first_table_index
    for page_index, page_text_boxes in enumerate(page_text_boxes_list, start=1):
        rows = group_ocr_text_boxes_into_rows(page_text_boxes)
        if not ocr_rows_look_like_table(rows):
            continue

        if pipeline is None:
            if progress_func:
                progress_func("表格结构识别：第 {0} 页".format(resolved_page))
            pipeline = get_table_ocr_instance(model_root)
        image_array = load_image_array(page_images[page_index - 1])
        overall_ocr_res = build_ocr_result_payload(image_array, page_text_boxes)
        results = list(
            pipeline.predict(
                image_array,
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_layout_detection=False,
                use_ocr_model=False,
                overall_ocr_res=overall_ocr_res,
                use_ocr_results_with_table_cells=False,
                cell_sort_by_y_projection=True,
            )
        )
        for result in results:
            if isinstance(result, dict) and result.get("error"):
                raise RuntimeError(str(result.get("error")))
            page_tables = extract_tables_from_result(
                result,
                page=resolved_page,
                first_table_index=next_table_index,
            )
            next_table_index += len(page_tables)
            tables.extend(page_tables)
    return tables


__all__ = [
    "DEFAULT_OCR_MODEL_PROFILE",
    "TableHtmlParser",
    "build_extracted_table_from_html",
    "build_table_pipeline_config",
    "extract_page_table_blocks",
    "extract_tables_from_result",
    "get_table_ocr_instance",
    "normalize_html_table_rows",
    "ocr_rows_look_like_table",
    "parse_html_table_rows",
]
