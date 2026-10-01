"""DOCX Parser Eval（TC-DOCX-01）：标题顺序、heading level、段落、表格、block 顺序。"""


def test_standard_docx_heading_order_and_levels(docx_standard):
    headings = docx_standard.blocks_of_type("heading")
    assert [(b.text, b.metadata["level"]) for b in headings] == [
        ("一、项目背景", 1),
        ("二、业务流程", 1),
        ("2.1 申请流程", 2),
        ("2.2 审批流程", 2),
        ("三、系统架构", 1),
    ]


def test_standard_docx_paragraph_and_list_counts(docx_standard):
    assert docx_standard.metadata["paragraph_count"] == 4
    list_items = docx_standard.blocks_of_type("list_item")
    assert len(list_items) == 3
    assert list_items[0].text.startswith("支持 DOCX/PDF/XLSX/PPTX")


def test_standard_docx_table_content(docx_standard):
    """表格不得被压成一句文本：rows / columns / cells 都要保留。"""
    tables = docx_standard.blocks_of_type("table")
    assert len(tables) == 1
    table = tables[0]
    assert table.metadata["rows"] == 4
    assert table.metadata["columns"] == 3
    assert table.metadata["cells"][0] == ["阶段", "操作", "责任主体"]
    assert table.metadata["cells"][1] == ["采集", "上传材料并OCR识别", "系统"]
    assert table.metadata["cells"][2][2] == "运营部"


def test_standard_docx_block_order(docx_standard):
    """最低要求：原始阅读顺序不能明显错乱。"""
    blocks = docx_standard.blocks
    assert blocks[0].block_type == "heading"
    type_sequence = [b.block_type for b in blocks]
    heading_texts = [b.text for b in blocks if b.block_type == "heading"]
    table_index = type_sequence.index("table")
    first_list_index = type_sequence.index("list_item")
    architecture_heading_index = heading_texts.index("三、系统架构")
    # 表格位于"三、系统架构"之后、列表之前，图片引用在最后
    assert table_index > architecture_heading_index
    assert table_index < first_list_index
    assert blocks[-1].block_type == "image_reference"


def test_standard_docx_image_reference(docx_standard):
    images = docx_standard.blocks_of_type("image_reference")
    assert len(images) == 1
    assert images[0].metadata["count"] == 1
    assert any("image1.png" in path for path in images[0].metadata["images"])


def test_standard_docx_metadata(docx_standard):
    assert docx_standard.metadata["title"] == "资产池需求方案"
    assert docx_standard.metadata["heading_count"] == 5
    assert docx_standard.metadata["table_count"] == 1
    assert docx_standard.metadata["section_count"] >= 1
    assert "author" in docx_standard.metadata["core_properties"]


def test_complex_docx_three_level_headings_and_two_tables(docx_complex):
    headings = docx_complex.blocks_of_type("heading")
    levels = [b.metadata["level"] for b in headings]
    assert 3 in levels
    assert levels.count(1) == 4
    assert len(docx_complex.blocks_of_type("table")) == 2
    assert docx_complex.metadata["list_item_count"] == 3
    # 三级标题确实出现在正确的层级位置
    level3_texts = [b.text for b in headings if b.metadata["level"] == 3]
    assert level3_texts == ["2.1.1 文件发现", "2.1.2 统一读取"]


def test_docx_artifact_ids_stable(reader, fixtures_dir):
    first = reader.read_artifact(fixtures_dir / "sample.docx")
    second = reader.read_artifact(fixtures_dir / "sample.docx")
    assert first.artifact_id == second.artifact_id
    assert [b.block_id for b in first.blocks] == [b.block_id for b in second.blocks]
