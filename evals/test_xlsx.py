"""XLSX Parser Eval（TC-XLSX-01）：sheet 数、sheet 名、formula、value、merged cells、used range。"""


def _find_record(block, address):
    return next(r for r in block.metadata["cell_records"] if r["address"] == address)


def test_standard_xlsx_sheet_info(xlsx_standard):
    assert xlsx_standard.metadata["sheet_count"] == 1
    sheet = xlsx_standard.metadata["sheets"][0]
    assert sheet["name"] == "资产负债表"
    assert sheet["dimensions"] == "A1:D8"


def test_standard_xlsx_values(xlsx_standard):
    block = xlsx_standard.blocks_of_type("table")[0]
    assert block.location["sheet"] == "资产负债表"
    assert block.location["range"] == "A1:D8"
    # 数值单元格：value 保留，无 formula
    assert _find_record(block, "B2")["value"] == 1200
    assert _find_record(block, "C2")["value"] == 1500
    assert _find_record(block, "B2")["formula"] is None
    assert _find_record(block, "B2")["row"] == 2
    assert _find_record(block, "B2")["column"] == 2


def test_standard_xlsx_formulas(xlsx_standard):
    """公式单元格：formula 必须保留。

    已知限制（记录于 baseline）：openpyxl 写出的公式没有 Excel 计算缓存，
    因此 value 为 None；真实业务文件（Excel 保存过）会同时拿到缓存值。
    """
    block = xlsx_standard.blocks_of_type("table")[0]
    record = _find_record(block, "D2")
    assert record["formula"] == "=C2-B2"
    assert record["value"] is None


def test_standard_xlsx_merged_cells(xlsx_standard):
    block = xlsx_standard.blocks_of_type("table")[0]
    assert "A8:D8" in block.metadata["merged_cells"]


def test_standard_xlsx_grid_preview(xlsx_standard):
    block = xlsx_standard.blocks_of_type("table")[0]
    assert block.metadata["cells"][0] == ["项目", "2024", "2025", "变动"]
    assert block.metadata["cells"][1] == ["营业收入", 1200, 1500, ""]
    assert not block.metadata["rows_truncated"]
    assert not block.metadata["cells_truncated"]


def test_multisheet_xlsx_sheet_order(xlsx_multisheet):
    assert xlsx_multisheet.metadata["sheet_count"] == 3
    assert [s["name"] for s in xlsx_multisheet.metadata["sheets"]] == [
        "利润表",
        "现金流量表",
        "预算对比",
    ]
    blocks = xlsx_multisheet.blocks_of_type("table")
    assert [b.location["sheet"] for b in blocks] == ["利润表", "现金流量表", "预算对比"]


def test_multisheet_xlsx_formulas_and_merged(xlsx_multisheet):
    profit = xlsx_multisheet.blocks_of_type("table")[0]
    assert _find_record(profit, "B4")["formula"] == "=B2-B3"
    assert _find_record(profit, "C4")["formula"] == "=C2-C3"
    budget = xlsx_multisheet.blocks_of_type("table")[2]
    assert "A5:C5" in budget.metadata["merged_cells"]


def test_xlsx_not_flattened_to_csv(xlsx_multisheet):
    """规格禁止 2：不能把 Excel 粗暴转成一段 CSV 文本——必须有 Sheet/Range/Cell 结构。"""
    assert xlsx_multisheet.metadata["sheet_count"] == 3
    for block in xlsx_multisheet.blocks_of_type("table"):
        assert block.metadata["cell_records"]
        assert "range" in block.location
