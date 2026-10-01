"""PPTX Parser Eval（TC-PPTX-01）：slide 数、title、textbox、table、slide attribution。"""


def test_pptx_slide_count_and_titles(pptx_standard):
    assert pptx_standard.metadata["slide_count"] == 4
    assert [s["title"] for s in pptx_standard.metadata["slides"]] == [
        "2025年度经营计划",
        "年度目标",
        "当前面临的问题",
        "季度目标",
    ]


def test_pptx_slide_blocks_in_order(pptx_standard):
    slide_blocks = pptx_standard.blocks_of_type("slide")
    assert [b.location["slide"] for b in slide_blocks] == [1, 2, 3, 4]
    assert [b.text for b in slide_blocks] == [
        "2025年度经营计划",
        "年度目标",
        "当前面临的问题",
        "季度目标",
    ]


def test_pptx_slide_attribution(pptx_standard):
    """所有内容块都必须知道自己在第几页 slide（规格第 14 节硬要求）。"""
    for block in pptx_standard.blocks:
        if block.block_type == "slide":
            continue
        assert "slide" in block.location
        assert 1 <= block.location["slide"] <= 4


def test_pptx_textboxes(pptx_standard):
    slide3_texts = [
        b.text
        for b in pptx_standard.blocks_of_type("textbox")
        if b.location["slide"] == 3
    ]
    joined = "\n".join(slide3_texts)
    assert "问题一" in joined
    assert "问题二" in joined
    assert "问题三" in joined


def test_pptx_table(pptx_standard):
    tables = pptx_standard.blocks_of_type("table")
    assert len(tables) == 1
    table = tables[0]
    assert table.location["slide"] == 4
    assert table.metadata["rows"] == 3
    assert table.metadata["columns"] == 3
    assert table.metadata["cells"][0] == ["季度", "目标(亿元)", "负责人"]
    assert table.metadata["cells"][1][1] == "4.5"


def test_pptx_content_follows_slide_order(pptx_standard):
    content = pptx_standard.content
    slide2_position = content.index("[Slide 2]")
    slide3_position = content.index("[Slide 3]")
    slide4_position = content.index("[Slide 4]")
    assert slide2_position < slide3_position < slide4_position
