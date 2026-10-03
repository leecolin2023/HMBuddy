# R — Review：AppState / Recent Workspace / Recent Activity：轻量恢复而非 Task 域

> SenseWright：**Vibe Review V0.10 / Coverage Before Materiality**  
> Review 重新读取 Raw Source；D 仅作导航，**Reference ≠ Evidence**。

## Assignment

判断这套设计/实现是否足以完成它当前应该完成的任务；不因为未来还能更复杂，就把“当前没做”自动判成缺陷。

## Atomic Review Map

本次覆盖：

1. 概念身份与职责；
2. 输入 / 输出 Contract；
3. 控制权和依赖方向；
4. 状态 / 权限 /错误 / 生命周期（适用时）；
5. 与相邻概念的边界；
6. 当前实现 vs 目标架构；
7. 故障模式与可观察性；
8. 后续阶段会放大的隐含假设。

## 已经成立的部分

- 隐私边界收紧。
- Workspace identity 统一。
- Recent UI 选择稳定。

## Findings

|级别|发现|为什么重要|
|---|---|---|
|Material|Stage B 引入 Session 后要避免双历史事实|Agent 相关 Recent Activity 应逐步迁移为 Session Index，而不是再维护一套‘伪 Session’。|
|Material|last_view 仍是 Product navigation state|不要让 AgentLoop 依赖它决定执行进度。|
|Minor|State JSON 足够当前规模|无需提前 SQLite。|

## Materiality Reconciliation

以下边界已经被审阅，但没有因为“还能加功能”而自动列为缺陷：

- Recent Activity ≠ Session。
- resume_view ≠ checkpoint。
- State 不存正文与隐藏模型状态。

Material finding 只保留会改变**正确性、下一阶段接口、信任边界或用户可解释性**的问题。

## Review 结论

当前状态：**Phase 2.1 已实现，2.1.1 统一 Workspace ID 与隐私语义**。

总体上，该概念在当前阶段的边界是自洽的；最重要的是继续保持“当前实现”和“Canonical Future Contract”的区分。任何后续增强都应由具体失败模式触发，而不是为了让概念列表更完整。

下一步：[L-learning.md](./L-learning.md)
