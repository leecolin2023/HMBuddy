# D — Deep Read：Context + LLM Interface：模型实际看到什么

> SenseWright：**Deep Read V6.4 / Coverage-Preserving**  
> HMBuddy Source Baseline：`14b79558cf25bba31a971fe144d83c145d9e7b46`  
> 当前状态：**已实现并在 Phase 2.1.1 修复真实 OpenAI Client 初始化**

## 阅读任务

只恢复 HMBuddy 当前源码/Canonical Architecture 自己建立的认知结构，不独立批判、不用外部框架改写它。

> **为什么 Parser 正确、Artifact 完整，仍可能让 LLM 得到错误或不完整证据？**

## Raw Source

- `llm/context.py`
- `llm/client.py`
- `evals/test_context_hardening.py`
- `tests/test_phase2_1_1_hardening.py`

## 认知拓扑

```text
Artifact
→ ContextPolicy
→ Block serialization
→ Truncation/OCR warnings
→ System Prompt + Question
→ LLM
```

## 独立认知单元

1. Artifact 是程序事实，Context 是一次模型调用实际可见内容。
2. 默认 max_chars/max_blocks/max_table_rows 使主路径有界。
3. 截断、表格解析期丢失、PDF requires_ocr 都显式标记。
4. 绝对路径默认不进入 Context。
5. BaseLLMClient.ask 负责统一 Artifact→Context→Prompt；OpenAICompatibleClient 在 2.1.1 修复为正确初始化 Base context_policy。
6. Conversation transcript 当前不会自动进入下一轮 Context；Phase 2.2 的 Conversation 仍只是 Presentation Surface。

## 认知发动机

模型只能对它实际收到的证据推理。Context 层是“系统知道什么”到“模型本轮看到什么”的信息闸门，因此必须独立建模、预算、验证。

## 当前边界

- 字符预算不是语义检索。
- 当前单 Artifact QA。
- 临时 Conversation 不等于 Session messages。

## Coverage Reconciliation

本篇覆盖的是与该概念有独立语义的：**角色、输入输出、控制权、调用关系、当前实现状态、明确非目标与演进接口**。未来概念只按 Canonical Architecture 恢复其目标语义，不把设计目标升级为当前事实。

## 压缩后的认知模型

- Context = model-call visibility boundary。
- UI 上看得到 ≠ 模型本轮看得到。

Deep Read 到此只回答“HMBuddy 在说什么、为什么这样组织”。判断是否站得住交给同目录 Review。

下一步：[R-review.md](./R-review.md)
