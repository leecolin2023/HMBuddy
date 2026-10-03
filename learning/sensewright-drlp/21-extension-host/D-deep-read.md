# D — Deep Read：ExtensionHost / Hooks / Events：高级 Agent 能力的统一扩展面

> SenseWright：**Deep Read V6.4 / Coverage-Preserving**  
> HMBuddy Source Baseline：`14b79558cf25bba31a971fe144d83c145d9e7b46`  
> 当前状态：**Canonical future Kernel primitive；未实现**

## 阅读任务

只恢复 HMBuddy 当前源码/Canonical Architecture 自己建立的认知结构，不独立批判、不用外部框架改写它。

> **为什么 Approval、Memory、MCP、Automation、Plan、Subagent 应优先作为 Extension，而不是各自进入 Core？**

## Raw Source

- `requirements/hmbuddy-architecture-baseline.md`

## 认知拓扑

```text
AgentLoop events
→ ExtensionHost
→ register_tool/register_hook/register_skill
→ before/after model/tool/session hooks
→ Approval/Memory/MCP/Audit/...
```

## 独立认知单元

1. ExtensionHost 是六个 Kernel 原语之一，首版 API 应极简。
2. 建议 hooks：session_start、before_model、after_model、before_tool、after_tool、session_end。
3. Approval 可在 before_tool 做 allow/ask/deny。
4. Audit 可在 after_tool 记录。
5. Memory/RAG 可在 before_model 注入 Context。
6. MCP Extension 发现外部 tools 后注册进 ToolRegistry。
7. Automation 本质是 Scheduler Extension → Create/Resume Session，而不是 AgentLoop 内部 scheduler。
8. Subagent 可通过 Tool/Extension 启动另一个 Session。

## 认知发动机

这些能力都需要‘在 AgentLoop 周边插入行为’，但并不要求改变 Loop 基本状态机。Hook/Extension 是控制 Kernel 膨胀的统一机制。

## 当前边界

- Events 保持小，不建大型 Event Bus。
- Extension 不可绕过 Workspace/Policy。
- Hook contract 一旦稳定属于高门槛核心接口。

## Coverage Reconciliation

本篇覆盖的是与该概念有独立语义的：**角色、输入输出、控制权、调用关系、当前实现状态、明确非目标与演进接口**。未来概念只按 Canonical Architecture 恢复其目标语义，不把设计目标升级为当前事实。

## 压缩后的认知模型

- Extension = behavior around the loop；Hook = stable insertion point；Event = observable fact。

Deep Read 到此只回答“HMBuddy 在说什么、为什么这样组织”。判断是否站得住交给同目录 Review。

下一步：[R-review.md](./R-review.md)
