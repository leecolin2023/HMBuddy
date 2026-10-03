# R — Review：Skill：Markdown-first 工作方法与 Progressive Disclosure

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

- 与现有 SenseWright 方法天然匹配。
- 业务方法可快速迭代而不改 Kernel。

## Findings

|级别|发现|为什么重要|
|---|---|---|
|Material|需要最小 Skill discovery/selection Contract|但不要一开始做 Marketplace/Compiler/Workflow DSL。|
|Material|Skill 引用 Tool 名必须有版本/存在性验证|否则文档方法与实际 ToolRegistry 漂移。|
|Minor|Skill metadata schema 可以很小|name/description/trigger/constraints 足够首版。|

## Materiality Reconciliation

以下边界已经被审阅，但没有因为“还能加功能”而自动列为缺陷：

- Skill 不是 durable Session state。
- Skill 不直接绕过 Tool/Policy。
- 复杂 Planner 不默认成为 Core。

Material finding 只保留会改变**正确性、下一阶段接口、信任边界或用户可解释性**的问题。

## Review 结论

当前状态：**Canonical future capability；SenseWright 被指定为优先接入 Skills**。

总体上，该概念在当前阶段的边界是自洽的；最重要的是继续保持“当前实现”和“Canonical Future Contract”的区分。任何后续增强都应由具体失败模式触发，而不是为了让概念列表更完整。

下一步：[L-learning.md](./L-learning.md)
