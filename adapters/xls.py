"""XLS 适配器（移植自 fce 的 .xls 链路）：xlrd 优先，Windows 上回退 Excel/WPS COM。

两个依赖都是懒加载：未安装 xlrd 且不在 Windows（或没装 pywin32/Office）时，
返回带明确提示的解析错误，不影响其它格式。

Phase 1.1.1（BUG-001）：xlrd 路径只需 filesystem.read；准备 COM fallback
前必须通过 permission gate 申请 office.com（动态权限，规格 4.3）。
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, List

from workspace.artifact import Artifact, ArtifactBlock, ArtifactLocator
from workspace.errors import ArtifactParseError

from .base import ArtifactAdapter, assign_block_ids
from .textnorm import normalize_spreadsheet_value


def _trim_trailing_empty_cells(values: List[str]) -> List[str]:
    trimmed = list(values)
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    return trimmed


def _format_xls_cell(cell: object, datemode: int, xlrd_module: object) -> str:
    ctype = getattr(cell, "ctype", None)
    value = getattr(cell, "value", None)

    if ctype in (
        getattr(xlrd_module, "XL_CELL_EMPTY", object()),
        getattr(xlrd_module, "XL_CELL_BLANK", object()),
    ):
        return ""
    if ctype == getattr(xlrd_module, "XL_CELL_BOOLEAN", object()):
        return "TRUE" if bool(value) else "FALSE"
    if ctype == getattr(xlrd_module, "XL_CELL_ERROR", object()):
        return "#ERROR({0})".format(value)
    if ctype == getattr(xlrd_module, "XL_CELL_DATE", object()):
        try:
            return normalize_spreadsheet_value(
                getattr(xlrd_module, "xldate_as_datetime")(value, datemode)
            )
        except Exception:
            return normalize_spreadsheet_value(value)
    return normalize_spreadsheet_value(value)


class XlsAdapter(ArtifactAdapter):
    artifact_type = "xls"
    supported_extensions = (".xls",)
    parser_library = "xlrd/pywin32"

    def __init__(self, ocr_options=None):
        super().__init__(ocr_options)
        self._permission_gate = None

    def set_permission_gate(self, gate) -> None:
        """由 Provider 在每次 execute 前注入（BUG-001 动态权限受控接口）。"""
        self._permission_gate = gate

    def read(self, path: Path, artifact_id: str) -> Artifact:
        result = self._read_with_xlrd(path)
        if result is None:
            result = self._read_with_com(path)
        if isinstance(result, str):
            # 返回字符串 = 失败原因，交给 Reader 记录 adapter 上下文
            raise ArtifactParseError(path, adapter=type(self).__name__, cause=result)

        blocks, sheets_meta = result
        metadata = {
            "sheet_count": len(sheets_meta),
            "sheets": sheets_meta,
            "title": path.stem,
        }
        content_lines: list[str] = []
        for block in blocks:
            content_lines.append(
                "[Sheet {0}]".format(block.location.get("sheet", ""))
            )
            for row in block.metadata["cells"][:50]:
                line = "\t".join(row).rstrip("\t")
                if line:
                    content_lines.append(line)
        assign_block_ids(blocks)
        return self.build_artifact(
            path,
            artifact_id,
            blocks=blocks,
            metadata=metadata,
            content="\n".join(content_lines),
            file_stat=path.stat(),
        )

    # ------------------------------------------------------------------
    # xlrd 链路
    # ------------------------------------------------------------------

    def _read_with_xlrd(self, path: Path):
        try:
            import xlrd  # type: ignore
        except ImportError:
            return None

        workbook = None
        try:
            # formatting_info=True 才能读到合并单元格；老文件不支持时回退普通打开
            try:
                workbook = xlrd.open_workbook(str(path), formatting_info=True)
            except Exception:
                if workbook is not None:
                    workbook.release_resources()
                workbook = xlrd.open_workbook(str(path), on_demand=True)
            blocks: list[ArtifactBlock] = []
            sheets_meta: list[dict] = []

            for sheet_index, sheet in enumerate(workbook.sheets(), start=1):
                grid: list[list[str]] = []
                for row_index in range(sheet.nrows):
                    values = [
                        _format_xls_cell(cell, getattr(workbook, "datemode", 0), xlrd)
                        for cell in sheet.row(row_index)
                    ]
                    values = _trim_trailing_empty_cells(values)
                    if not values or not any(values):
                        grid.append([""] * 0)
                        continue
                    grid.append(values)

                # 合并单元格信息（xlrd: (起始行, 结束行+1, 起始列, 结束列+1)）
                merged: list[str] = []
                try:
                    for rlo, rhi, clo, chi in sheet.merged_cells or []:
                        merged.append(
                            "{0}{1}:{2}{3}".format(
                                _column_letter(clo),
                                rlo + 1,
                                _column_letter(chi - 1),
                                rhi,
                            )
                        )
                except Exception:
                    merged = []

                non_empty_rows = [row for row in grid if any(row)]
                blocks.append(
                    ArtifactBlock(
                        "",
                        "table",
                        None,
                        {"sheet": sheet.name, "range": _grid_range(non_empty_rows)},
                        {
                            "rows": len(non_empty_rows),
                            "columns": max((len(r) for r in non_empty_rows), default=0),
                            "cells": non_empty_rows,
                            "merged_cells": merged,
                            "extraction_method": "xlrd",
                        },
                    )
                )
                sheets_meta.append(
                    {
                        "name": sheet.name,
                        "max_row": sheet.nrows,
                        "max_column": sheet.ncols,
                        "merged_count": len(merged),
                    }
                )

            if not any(
                block.metadata["rows"] for block in blocks
            ) and not sheets_meta:
                return "XLS 中未识别到有效单元格内容。"
            return blocks, sheets_meta
        except Exception as exc:
            return "XLS 读取失败（xlrd）：{0}".format(exc)
        finally:
            try:
                if workbook is not None:
                    workbook.release_resources()
            except Exception:
                pass

    # ------------------------------------------------------------------
    # COM 兼容链路（Excel / WPS）
    # ------------------------------------------------------------------

    def _read_with_com(self, path: Path):
        # BUG-001 / 规格 4.3：xlrd 失败准备 COM fallback 前申请 office.com
        if self._permission_gate is not None:
            self._permission_gate("office.com")
        if os.name != "nt":
            return "缺少 xlrd，无法读取 .xls（当前平台无 COM 兼容方式）。"
        try:
            import win32com.client as win32  # type: ignore
        except ImportError:
            return "缺少 xlrd/pywin32，无法读取 .xls。"

        prog_ids = ["Excel.Application", "Ket.Application", "ET.Application"]
        errors: list[str] = []

        for prog_id in prog_ids:
            app = None
            workbook = None
            try:
                app = win32.DispatchEx(prog_id)
                app.Visible = False
                try:
                    app.DisplayAlerts = False
                except Exception:
                    pass

                workbook = app.Workbooks.Open(str(path), False, True)
                blocks: list[ArtifactBlock] = []
                sheets_meta: list[dict] = []

                sheet_count = int(workbook.Worksheets.Count)
                for sheet_index in range(1, sheet_count + 1):
                    sheet = workbook.Worksheets(sheet_index)
                    used_range = sheet.UsedRange
                    first_row = int(getattr(used_range, "Row", 1) or 1)
                    raw_rows = _normalize_com_sheet_values(
                        getattr(used_range, "Value", None)
                    )
                    grid: list[list[str]] = []
                    for offset, raw_row in enumerate(raw_rows):
                        values = [
                            normalize_spreadsheet_value(item) for item in raw_row
                        ]
                        values = _trim_trailing_empty_cells(values)
                        if not values or not any(values):
                            continue
                        grid.append(values)

                    if grid:
                        blocks.append(
                            ArtifactBlock(
                                "",
                                "table",
                                None,
                                {
                                    "sheet": str(sheet.Name),
                                    "range": _grid_range(grid, first_row=first_row),
                                },
                                {
                                    "rows": len(grid),
                                    "columns": max(
                                        (len(r) for r in grid), default=0
                                    ),
                                    "cells": grid,
                                    "extraction_method": prog_id,
                                },
                            )
                        )
                    sheets_meta.append({"name": str(sheet.Name)})

                if blocks:
                    return blocks, sheets_meta
                return "XLS 已打开，但未识别到有效单元格内容。"
            except Exception as exc:
                errors.append("{0}: {1}".format(prog_id, exc))
            finally:
                try:
                    if workbook is not None:
                        workbook.Close(False)
                except Exception:
                    pass
                try:
                    if app is not None:
                        app.Quit()
                except Exception:
                    pass

        return "无法通过 xlrd 或 Excel/WPS 打开 .xls：{0}".format(" | ".join(errors))


def _normalize_com_sheet_values(values: object) -> list[list[object]]:
    if values is None:
        return []
    if isinstance(values, tuple):
        rows = list(values)
        if rows and not isinstance(rows[0], tuple):
            rows = [tuple(rows)]
        normalized_rows: list[list[object]] = []
        for row in rows:
            if isinstance(row, tuple):
                normalized_rows.append(list(row))
            else:
                normalized_rows.append([row])
        return normalized_rows
    return [[values]]


def _column_letter(index: int) -> str:
    letters = ""
    index = int(index) + 1
    while index > 0:
        index, remainder = divmod(index - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters


def _grid_range(grid: list[list[str]], first_row: int = 1) -> str:
    if not grid:
        return "A1"
    last_row = first_row + len(grid) - 1
    last_column = max((len(row) for row in grid), default=1)
    return "A{0}:{1}{2}".format(first_row, _column_letter(last_column - 1), last_row)
