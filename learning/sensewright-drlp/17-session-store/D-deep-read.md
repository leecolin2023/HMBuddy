# D — Deep Read：Session / SessionStore：持久工作上下文、Product Task 与 Resume

> SenseWright：**Deep Read V6.4 / Coverage-Preserving**  
> HMBuddy Source Baseline：`14b79558cf25bba31a971fe144d83c145d9e7b46`  
> 当前状态：**Canonical future Kernel primitive；Stage B 未实现**

## 阅读任务

只恢复 HMBuddy 当前源码/Canonical Architecture 自己建立的认知结构，不独立批判、不用外部框架改写它。

> **Session 应怎样同时承载 Conversation、Task、History、Resume，而不演化成重型 TaskEngine？**

## Raw Source

- `requirements/hmbuddy-architecture-baseline.md`
- `requirements/phase-2.1-desktop-application-foundation-v0.1.md`
- `application/state.py`

## 认知拓扑

```text
Workspace
→ Session
→ messages + tool_calls + artifact_refs + metadata
→ SessionStore
→ Session Index
→ Product Task/History/Resume
```

## 独立认知单元

1. Session 是一次可持续、可恢复 Agent 工作上下文。
2. Product Task = Session + task metadata，不默认引入 Step DAG。
3. SessionStore 是 durable source；Product History/Resume 读 Session Index。
4. 状态可以简单为 active/waiting_user/completed/failed/cancelled。
5. 只有真实需求证明需要稳定 Step Graph 时才考虑更强 Task Contract。
6. Recent Activity 应在 Agent 场景逐步让位于 Session Index。

## 认知发动机

Session 把多轮模型、工具调用和 Artifact 引用归到一个可恢复的工作单位中。它提供持久控制上下文，但刻意不预先规定工作流结构。

## 当前边界

- Session ≠ Planner。
- Session ≠ Scheduler。
- Session 不保存运行对象实例。
- 恢复前要重建 Runtime 并校验外部依赖。

## Coverage Reconciliation

本篇覆盖的是与该概念有独立语义的：**角色、输入输出、控制权、调用关系、当前实现状态、明确非目标与演进接口**。未来概念只按 Canonical Architecture 恢复其目标语义，不把设计目标升级为当前事实。

## 压缩后的认知模型

- Session = durable context + history；Product Task 是它的产品投影。

Deep Read 到此只回答“HMBuddy 在说什么、为什么这样组织”。判断是否站得住交给同目录 Review。

下一步：[R-review.md](./R-review.md)
