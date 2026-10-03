# R — Review：AgentLoop：最小自主决策闭环

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

- 现有 Workspace/Runtime/Policy 可复用为执行底座。
- 架构已明确 Hook 扩展方向。

## Findings

|级别|发现|为什么重要|
|---|---|---|
|Material|首版必须只读且 bounded|在 Session/Tool trace 还未成熟前开放 write 会把安全与恢复复杂度同时放大。|
|Material|Loop 与 Context composition 必须一起设计|tool result/messages/tool descriptions 都会进入下一轮模型输入。|
|Material|Event hooks 要避免改变核心控制流语义|Extension 可观察/阻断，但 Loop state transitions 必须有唯一 owner。|

## Materiality Reconciliation

以下边界已经被审阅，但没有因为“还能加功能”而自动列为缺陷：

- 不内置 Planner。
- 不直接访问 Provider/Adapter。
- 不把 Memory/MCP/Automation 写死在循环里。

Material finding 只保留会改变**正确性、下一阶段接口、信任边界或用户可解释性**的问题。

## Review 结论

当前状态：**Canonical future Kernel primitive；未实现**。

总体上，该概念在当前阶段的边界是自洽的；最重要的是继续保持“当前实现”和“Canonical Future Contract”的区分。任何后续增强都应由具体失败模式触发，而不是为了让概念列表更完整。

下一步：[L-learning.md](./L-learning.md)
