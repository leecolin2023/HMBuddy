"""PDF Parser Eval（TC-PDF-01）：page 数、page text、page attribution、文本顺序。"""


def test_pdf_page_count(pdf_standard):
    assert pdf_standard.metadata["page_count"] == 2


def test_pdf_page_attribution(pdf_standard):
    """每个 block 都必须知道自己在第几页（规格第 14/12 节）。"""
    pages = {b.location["page"] for b in pdf_standard.blocks}
    assert pages == {1, 2}
    for block in pdf_standard.blocks:
        assert block.location["page"] in (1, 2)


def test_pdf_page_text(pdf_standard):
    page1 = [b.text for b in pdf_standard.blocks if b.location["page"] == 1]
    page2 = [b.text for b in pdf_standard.blocks if b.location["page"] == 2]
    assert page1[0] == "Quarterly Risk Report 2025 Q3"
    assert any("Interest rate volatility" in t for t in page1)
    joined_page2 = "\n".join(page2)
    assert "主要风险结论" in joined_page2
    assert "流动性" in joined_page2
    assert "久期" in joined_page2


def test_pdf_text_order(pdf_standard):
    """同页内文本块保持自上而下的阅读顺序。"""
    page1 = [b.text for b in pdf_standard.blocks if b.location["page"] == 1]
    assert page1.index("1. Market Risk") < page1.index("2. Credit Risk")
    page1_line_indexes = [
        b.location["line_index"]
        for b in pdf_standard.blocks
        if b.location["page"] == 1 and b.block_type == "text_block"
    ]
    assert page1_line_indexes == sorted(page1_line_indexes)
    # 第 1 页的块整体位于第 2 页的块之前
    pages_in_order = [b.location["page"] for b in pdf_standard.blocks]
    assert pages_in_order == sorted(pages_in_order)


def test_pdf_metadata(pdf_standard):
    assert pdf_standard.metadata["requires_ocr"] is False
    assert pdf_standard.metadata["title"] == "Quarterly Risk Report 2025 Q3"
    assert pdf_standard.provenance["parser_library"] == "pdfplumber"


def test_pdf_content_is_plain_text(pdf_standard):
    assert "Quarterly Risk Report" in pdf_standard.content
    assert "流动性紧张" in pdf_standard.content
