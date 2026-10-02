"""纯文本 Adapter Eval（fce 能力融入）：多编码回退 + 行级段落结构。"""
from services.artifact_reader import read_artifact


def test_utf8_text(tmp_path):
    target = tmp_path / "notes.txt"
    target.write_text("第一行内容\n第二行内容\n", encoding="utf-8")
    artifact = read_artifact(target)
    assert artifact.artifact_type == "txt"
    assert artifact.metadata["line_count"] == 3  # 含末尾空行的总行数
    assert [b.text for b in artifact.blocks_of_type("paragraph")] == [
        "第一行内容",
        "第二行内容",
    ]


def test_gb18030_encoding_fallback(tmp_path):
    """内网历史文件常见 GBK 系编码，必须能正确读取。"""
    target = tmp_path / "legacy.txt"
    target.write_bytes("会议纪要：资产池项目进展".encode("gb18030"))
    artifact = read_artifact(target)
    assert artifact.content == "会议纪要：资产池项目进展"
    assert artifact.blocks_of_type("paragraph")[0].text == "会议纪要：资产池项目进展"


def test_utf8_bom_stripped(tmp_path):
    target = tmp_path / "bom.txt"
    target.write_bytes(b"\xef\xbb\xbfBOM \xe5\x86\x85\xe5\xae\xb9")
    artifact = read_artifact(target)
    assert artifact.content == "BOM 内容"


def test_markdown_extension_type(tmp_path):
    target = tmp_path / "readme.md"
    target.write_text("# 标题\n\n正文段落\n", encoding="utf-8")
    artifact = read_artifact(target)
    assert artifact.artifact_type == "md"
    paragraph_texts = [b.text for b in artifact.blocks_of_type("paragraph")]
    assert "# 标题" in paragraph_texts
    assert "正文段落" in paragraph_texts


def test_csv_treated_as_text(tmp_path):
    """CSV 保持文本行级读取（表格化解析留待后续按真实需求引入）。"""
    target = tmp_path / "data.csv"
    target.write_text("名称,数量\n资产池,1\n", encoding="utf-8")
    artifact = read_artifact(target)
    assert artifact.artifact_type == "csv"
    assert len(artifact.blocks_of_type("paragraph")) == 2


def test_empty_lines_are_skipped(tmp_path):
    target = tmp_path / "gaps.txt"
    target.write_text("A\n\n\nB\n", encoding="utf-8")
    artifact = read_artifact(target)
    assert artifact.metadata["line_count"] == 5  # 总行数（含空行）
    assert len(artifact.blocks) == 2  # 空行不产出 block
    assert [b.location["line_index"] for b in artifact.blocks] == [0, 3]  # 保留原始行号
