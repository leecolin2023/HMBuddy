# R — Review：ExtensionHost / Hooks / Events：高级 Agent 能力的统一扩展面

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

- 可以覆盖大量 WorkBuddy 式高级功能。
- AgentLoop 保持简单。

## Findings

|级别|发现|为什么重要|
|---|---|---|
|Material|Hook order/error/isolation 需要严谨 Contract|多个 Extension 同时安装时，before_tool 的 deny/ask/modify 冲突必须可预测。|
|Material|Approval 与 Policy 分工要明确|Policy 做确定性规则，ASK 的用户交互由 Product/Extension 承担。|
|Material|Extension sandbox/权限另需设计|与 Capability Plugin 类似，进程内第三方 Extension 也可能绕过治理。|

## Materiality Reconciliation

以下边界已经被审阅，但没有因为“还能加功能”而自动列为缺陷：

- Events 保持小，不建大型 Event Bus。
- Extension 不可绕过 Workspace/Policy。
- Hook contract 一旦稳定属于高门槛核心接口。

Material finding 只保留会改变**正确性、下一阶段接口、信任边界或用户可解释性**的问题。

## Review 结论

当前状态：**Canonical future Kernel primitive；未实现**。

总体上，该概念在当前阶段的边界是自洽的；最重要的是继续保持“当前实现”和“Canonical Future Contract”的区分。任何后续增强都应由具体失败模式触发，而不是为了让概念列表更完整。

下一步：[L-learning.md](./L-learning.md)
