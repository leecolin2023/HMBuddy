"""PDF 矢量表格 Eval（fce 引擎融入）：矢量网格重建、表头识别、跨页续表链接。"""


def test_vector_tables_extracted(pdf_table):
    tables = pdf_table.blocks_of_type("table")
    assert len(tables) == 2
    assert all(
        block.metadata.get("extraction_method") == "pdf-vector-grid"
        for block in tables
    )
    assert [block.location["page"] for block in tables] == [1, 2]


def test_vector_table_grid_content(pdf_table):
    table = pdf_table.blocks_of_type("table")[0]
    assert table.metadata["rows"] == 3
    assert table.metadata["columns"] == 3
    assert table.metadata["cells"][0] == ["项目", "2024", "2025"]
    assert table.metadata["cells"][1] == ["营业收入", "1200", "1500"]
    assert table.metadata["cells"][2] == ["营业成本", "800", "900"]


def test_header_row_detected(pdf_table):
    for block in pdf_table.blocks_of_type("table"):
        assert block.metadata.get("repeated_header_row") == 1


def test_cross_page_continuation_linking(pdf_table):
    """跨页续表：同列数 + 同表头签名 → 串成同一条链。"""
    first, second = pdf_table.blocks_of_type("table")
    assert first.metadata.get("continued_on_next") is True
    assert second.metadata.get("continues_from_previous") is True
    assert (
        first.metadata["continuation_id"]
        == second.metadata["continuation_id"]
        == "table-chain-1"
    )


def test_page2_grid_content(pdf_table):
    second = pdf_table.blocks_of_type("table")[1]
    assert second.metadata["cells"][1] == ["毛利润", "400", "600"]
    assert second.metadata["cells"][2] == ["净利润", "350", "520"]


def test_context_marks_continuation(pdf_table):
    from llm.context import artifact_to_context

    context = artifact_to_context(pdf_table)
    assert "续上一页表格" in context
    assert "（表格在下一页继续）" in context


def test_plain_pdf_has_no_fake_tables(pdf_standard):
    """纯文本 PDF 不应凭空产出表格。"""
    assert pdf_standard.blocks_of_type("table") == []
