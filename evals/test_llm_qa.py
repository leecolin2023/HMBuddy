"""端到端 QA Eval（规格第 21 节 / 22-D）。

两层：
1. Context 事实完整性（无需 LLM 即可运行）：验证问题所需的事实确实进入了
   Context。失败时能区分是 Parser Error（结构没解析出来）还是 Context Error
   （解析出来了但渲染丢失）。
2. 真实 LLM 问答（配置 HMBUDDY_LLM_BASE_URL / HMBUDDY_LLM_MODEL 后自动启用）：
   验证 LLM 基于 Context 能给出含关键事实的回答。
"""
import pytest

from llm.client import client_from_env
from llm.context import artifact_to_context

# (fixture 名, 问题, Context 中必须存在的事实, LLM 回答中期望出现的关键词)
CASES = [
    ("xlsx_standard", "2025年营业收入是多少？", ["营业收入", "1500"], "1500"),
    ("docx_standard", "审批流程由谁负责？", ["2.2 审批流程", "运营部"], "运营部"),
    (
        "pptx_standard",
        "第 3 页提出了哪三个问题？",
        ["[Slide 3]", "问题一", "问题二", "问题三"],
        "问题一",
    ),
    (
        "pdf_standard",
        "报告对主要风险的结论是什么？",
        ["流动性", "久期"],
        "流动性",
    ),
]


@pytest.mark.parametrize("fixture_name,question,facts,llm_keyword", CASES)
def test_context_contains_facts_required_by_question(
    request, fixture_name, question, facts, llm_keyword
):
    """22-D 前置：Context 层事实完整性（Parser Error / Context Error 可区分）。"""
    artifact = request.getfixturevalue(fixture_name)
    context = artifact_to_context(artifact)
    for fact in facts:
        assert fact in context, (
            f"问题「{question}」所需事实 {fact!r} 不在 Context 中："
            f"可能是 Parser 没解析出该内容（Parser Error），"
            f"也可能是 Context 渲染丢失（Context Error）"
        )


@pytest.mark.skipif(
    client_from_env() is None,
    reason="未配置 HMBUDDY_LLM_BASE_URL / HMBUDDY_LLM_MODEL，跳过真实 LLM 问答 Eval",
)
@pytest.mark.parametrize("fixture_name,question,facts,llm_keyword", CASES)
def test_llm_answers_basic_factual_questions(
    request, fixture_name, question, facts, llm_keyword
):
    artifact = request.getfixturevalue(fixture_name)
    client = client_from_env()
    answer = client.ask(artifact, question)
    assert llm_keyword in answer, (
        f"LLM 回答未包含预期事实 {llm_keyword!r}。\n问题：{question}\n回答：{answer}"
    )
