# R — Review：Runtime Governance：Policy、Availability、Fallback、Trace

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

- 安全错误不 fallback。
- 权限在副作用前阻断。
- 选择异常与 provider unavailable 可区分。

## Findings

|级别|发现|为什么重要|
|---|---|---|
|Material|未来写工具需要 ALLOW/ASK/DENY 与 operation scope|现有 permission 枚举不足以表达“只允许修改这个 Artifact 的这个版本”。|
|Material|Trace 需要与未来 Session/tool_call_id 关联|否则 Agent 级审计只能看到孤立 capability 调用。|
|Minor|Availability probe 仍是进程内探测|足够当前本地 Runtime。|

## Materiality Reconciliation

以下边界已经被审阅，但没有因为“还能加功能”而自动列为缺陷：

- 同进程恶意代码可绕过 Policy。
- 未来 ASK/Approval 需要 Product/Extension 配合。
- Trace 不是 Session checkpoint。

Material finding 只保留会改变**正确性、下一阶段接口、信任边界或用户可解释性**的问题。

## Review 结论

当前状态：**已实现**。

总体上，该概念在当前阶段的边界是自洽的；最重要的是继续保持“当前实现”和“Canonical Future Contract”的区分。任何后续增强都应由具体失败模式触发，而不是为了让概念列表更完整。

下一步：[L-learning.md](./L-learning.md)
