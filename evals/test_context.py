"""Context 构造 Eval（规格第 17 节）：Artifact 必须能渲染成对 LLM 友好的结构。"""
from llm.context import artifact_to_context
from workspace.artifact import Artifact, ArtifactBlock


def test_docx_context_structure(docx_standard):
    context = artifact_to_context(docx_standard)
    assert context.startswith("[Document]")
    assert "Name: sample.docx" in context
    assert "Type: DOCX" in context
    assert "[Heading 1] 一、项目背景" in context
    assert "[Heading 2] 2.1 申请流程" in context
    assert "[Paragraph]" in context
    assert "[List Item] 支持 DOCX/PDF/XLSX/PPTX 四种格式" in context
    assert "[Table 4x3]" in context
    assert "| 阶段 | 操作 | 责任主体 |" in context
    assert "| 采集 | 上传材料并OCR识别 | 系统 |" in context
    assert "[Image Reference]" in context


def test_xlsx_context_structure(xlsx_multisheet):
    context = artifact_to_context(xlsx_multisheet)
    assert "Type: XLSX" in context
    assert "[Table 4x3 | sheet=利润表 range=A1:C4]" in context
    assert "| 营业收入 | 1200 | 1500 |" in context
    assert "sheet=预算对比" in context
    # used range 是 A1:C5（A5:C5 是其中的合并区域，渲染为合并后首格内容）
    assert "range=A1:C5" in context
    assert "| 口径：万元 |" in context


def test_pdf_context_structure(pdf_standard):
    context = artifact_to_context(pdf_standard)
    assert "Type: PDF" in context
    assert "[Page 1]" in context
    assert "[Page 2]" in context
    assert "[Text] 3. 主要风险结论" in context
    assert "[Text] 建议维持现金流缓冲并缩短资产久期。" in context


def test_pptx_context_structure(pptx_standard):
    context = artifact_to_context(pptx_standard)
    assert "Type: PPTX" in context
    assert "[Slide 1] 2025年度经营计划" in context
    assert "[Slide 3] 当前面临的问题" in context
    assert "[Textbox] 问题一：文档分散在多个共享目录，查找困难" in context
    assert "[Table 3x3 | slide=4]" in context
    assert "| 季度 | 目标(亿元) | 负责人 |" in context


def test_context_table_truncation():
    """超长表格必须截断并显式标注，而不是无声丢弃。"""
    artifact = Artifact(
        artifact_id="a_x",
        name="big.xlsx",
        path="/tmp/big.xlsx",
        artifact_type="xlsx",
        blocks=[
            ArtifactBlock(
                "b0001",
                "table",
                None,
                {"sheet": "Sheet1", "range": "A1:C300"},
                {
                    "rows": 300,
                    "columns": 3,
                    "cells": [[f"r{i}", i, i * 2] for i in range(300)],
                },
            )
        ],
    )
    context = artifact_to_context(artifact, max_table_rows=200)
    assert "| r199 | 199 | 398 |" in context
    assert "| r299 | 299 | 598 |" not in context
    assert "已截断" in context


def test_context_does_not_leak_none_cells():
    artifact = Artifact(
        artifact_id="a_x",
        name="t.xlsx",
        path="/tmp/t.xlsx",
        artifact_type="xlsx",
        blocks=[
            ArtifactBlock(
                "b0001",
                "table",
                None,
                {"sheet": "S", "range": "A1:B1"},
                {"rows": 1, "columns": 2, "cells": [[None, "值"]]},
            )
        ],
    )
    context = artifact_to_context(artifact)
    assert "|  | 值 |" in context
    assert "None" not in context
