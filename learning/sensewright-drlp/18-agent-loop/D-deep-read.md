# D — Deep Read：AgentLoop：最小自主决策闭环

> SenseWright：**Deep Read V6.4 / Coverage-Preserving**  
> HMBuddy Source Baseline：`14b79558cf25bba31a971fe144d83c145d9e7b46`  
> 当前状态：**Canonical future Kernel primitive；未实现**

## 阅读任务

只恢复 HMBuddy 当前源码/Canonical Architecture 自己建立的认知结构，不独立批判、不用外部框架改写它。

> **什么时候 HMBuddy 才真正成为 Agent，而不是 Conversation UI + 文档问答？**

## Raw Source

- `requirements/hmbuddy-architecture-baseline.md`
- `llm/client.py`
- `desktop/controller.py`

## 认知拓扑

```text
Session Context
→ Model
→ Tool Call?
→ ToolRegistry.execute
→ Observation
→ append Session
→ Model again
→ finish
```

## 独立认知单元

1. AgentLoop 是模型根据 Observation 持续决定下一 Action 的控制循环。
2. 当前 HMBuddy 没有 Tool Calling Loop；模型只回答当前 Artifact 问题。
3. AgentLoop 应保持极小，Approval/Memory/Plan/Audit 通过 Hooks/Extensions 进入。
4. 必须有 termination、max steps/cancel、错误转 Observation 等基本控制。
5. Session 是 AgentLoop 的 durable state owner。

## 认知发动机

Agent 的关键不是会显示聊天，而是模型获得受控行动权，并能基于行动结果继续决策。AgentLoop 是控制权从人到模型迁移的最小原语。

## 当前边界

- 不内置 Planner。
- 不直接访问 Provider/Adapter。
- 不把 Memory/MCP/Automation 写死在循环里。

## Coverage Reconciliation

本篇覆盖的是与该概念有独立语义的：**角色、输入输出、控制权、调用关系、当前实现状态、明确非目标与演进接口**。未来概念只按 Canonical Architecture 恢复其目标语义，不把设计目标升级为当前事实。

## 压缩后的认知模型

- AgentLoop = Decide → Act → Observe → Persist → Repeat/Stop。

Deep Read 到此只回答“HMBuddy 在说什么、为什么这样组织”。判断是否站得住交给同目录 Review。

下一步：[R-review.md](./R-review.md)
