"""T9 — Context Hardening Eval（规格第 25 节 / AC-09）。

- FR-C01 全局预算（max_chars / max_blocks），截断显式可观察；
- FR-C02 XLSX 解析期截断标记进入 Context / warnings；
- FR-C03 PDF 页级 OCR 标记；
- FR-C04 绝对路径默认不进入 LLM Context。
"""
from adapters.tables import grid_to_table_metadata
from llm.context import artifact_to_context, build_context
from workspace.artifact import Artifact, ArtifactBlock

import re


def test_no_absolute_path_in_context(pdf_standard):
    """FR-C04：Context 默认只含 name / artifact_id，不发绝对路径。"""
    context = artifact_to_context(pdf_standard)
    assert "Name: sample.pdf" in context
    assert "Artifact ID:" in context
    assert "Path:" not in context
    assert str(pdf_standard.provenance["source_path"]) not in context
    # 无反斜杠、无 Windows 盘符路径模式
    assert chr(92) not in context
    assert not re.search(r"[A-Za-z]:\\", context)


def test_relative_path_only_when_requested(pdf_standard):
    context = artifact_to_context(pdf_standard, relative_path="docs/sample.pdf")
    assert "Relative Path: docs/sample.pdf" in context
    assert chr(92) not in context


def test_global_char_budget_truncates_explicitly(docx_standard):
    result = build_context(docx_standard, max_chars=300)
    assert result.truncated is True
    assert result.omitted_blocks > 0
    assert result.reason and "max_chars=300" in result.reason
    assert result.warnings
    assert "[Context Truncated] truncated=true" in result.text
    assert f"omitted_blocks={result.omitted_blocks}" in result.text


def test_global_block_budget_truncates_explicitly(docx_standard):
    result = build_context(docx_standard, max_blocks=3)
    assert result.truncated is True
    assert result.omitted_blocks == len(docx_standard.blocks) - 3
    assert "max_blocks=3" in result.reason
    # 前 3 个 block 仍然完整保留
    assert result.text.count("[") >= 3


def test_no_budget_no_truncation(docx_standard):
    result = build_context(docx_standard)
    assert result.truncated is False
    assert result.omitted_blocks == 0
    assert "Context Truncated" not in result.text


def test_artifact_to_context_backward_compatible_string(docx_standard):
    context = artifact_to_context(docx_standard, max_chars=200)
    assert isinstance(context, str)
    assert "[Context Truncated]" in context


def _artifact_with_table(metadata):
    return Artifact(
        artifact_id="a_x",
        name="t.xlsx",
        path="D:/nowhere/t.xlsx",
        artifact_type="xlsx",
        blocks=[ArtifactBlock("b0001", "table", None, {"sheet": "S", "range": "A1:C10"}, metadata)],
    )


def test_frc02_xlsx_parse_truncation_visible():
    """FR-C02：解析期截断标记必须出现在 Context 中并进入 warnings。"""
    metadata = grid_to_table_metadata([["a", "b"]], extraction_method="openpyxl")
    metadata["rows_truncated"] = True
    metadata["columns_truncated"] = True
    metadata["cells_truncated"] = True
    artifact = _artifact_with_table(metadata)

    result = build_context(artifact)
    assert "[Note] 本表在解析阶段已被截断" in result.text
    assert "rows_truncated=true" in result.text
    assert len(result.warnings) >= 3


def test_frc02_no_truncation_no_warning(xlsx_standard):
    result = build_context(xlsx_standard)
    assert not any("解析阶段已被截断" in w for w in result.warnings)


def test_frc03_pdf_page_level_ocr_flag():
    """FR-C03：页级 requires_ocr 标记按页渲染。"""
    artifact = Artifact(
        artifact_id="a_pdf",
        name="mixed.pdf",
        path="/tmp/mixed.pdf",
        artifact_type="pdf",
        metadata={
            "page_count": 2,
            "pages": [
                {"page": 1, "text_chars": 120, "requires_ocr": False},
                {"page": 2, "text_chars": 0, "requires_ocr": True},
            ],
        },
        blocks=[
            ArtifactBlock("b0001", "text_block", "第一页正文", {"page": 1, "line_index": 0}, {}),
            ArtifactBlock("b0002", "text_block", "第二页可读残余", {"page": 2, "line_index": 0}, {}),
        ],
    )
    context = artifact_to_context(artifact)
    assert "[Page 2]" in context
    assert "[Note] 第 2 页无文本层（requires_ocr=true）" in context
    assert "第 1 页无文本层" not in context


def test_frc03_clean_pdf_has_no_ocr_notes(pdf_standard):
    context = artifact_to_context(pdf_standard)
    assert "无文本层" not in context
