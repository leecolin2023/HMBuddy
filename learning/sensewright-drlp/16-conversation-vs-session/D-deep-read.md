# D — Deep Read：Conversation Surface vs Session Domain：UI 语言与 Kernel 原语

> SenseWright：**Deep Read V6.4 / Coverage-Preserving**  
> HMBuddy Source Baseline：`14b79558cf25bba31a971fe144d83c145d9e7b46`  
> 当前状态：**Conversation 已实现；Session 明确未实现**

## 阅读任务

只恢复 HMBuddy 当前源码/Canonical Architecture 自己建立的认知结构，不独立批判、不用外部框架改写它。

> **为什么界面可以叫“新建会话”，但架构上仍不能说 HMBuddy 已经有 Session？**

## Raw Source

- `desktop/controller.py`
- `desktop/widgets/conversation.py`
- `requirements/phase-2.2-desktop-ux-shell-redesign-v0.1.md`
- `requirements/hmbuddy-architecture-baseline.md`

## 认知拓扑

```text
Conversation UI transcript (process memory)
→ current artifact/workspace
→ LLM single-turn ask
→ [future] SessionStore/messages/tool_calls/artifact_refs
```

## 独立认知单元

1. Phase 2.2 Conversation 是 Presentation Surface。
2. new_conversation 只清 conversation_messages/current_artifact/active_ref，保留 Workspace。
3. state.json 明确不能出现 session/session_id。
4. 临时 transcript 不持久化，也不默认参与下一轮 LLM Context。
5. 架构总纲中的 Session 是可持续、可恢复 Agent 工作上下文，包含 messages/tool_calls/artifact_refs/metadata。

## 认知发动机

同一个产品词‘会话’在 UI 与 Kernel 可以暂时有不同成熟度。刻意不实现半套 Session，是为了防止临时 transcript 被错误固化为未来核心 Contract。

## 当前边界

- Conversation ≠ memory。
- Conversation ≠ task execution state。
- Session 未来必须是 durable/domain-level，而不是 QWidget state。

## Coverage Reconciliation

本篇覆盖的是与该概念有独立语义的：**角色、输入输出、控制权、调用关系、当前实现状态、明确非目标与演进接口**。未来概念只按 Canonical Architecture 恢复其目标语义，不把设计目标升级为当前事实。

## 压缩后的认知模型

- Conversation = Product surface；Session = durable Kernel context。

Deep Read 到此只回答“HMBuddy 在说什么、为什么这样组织”。判断是否站得住交给同目录 Review。

下一步：[R-review.md](./R-review.md)
