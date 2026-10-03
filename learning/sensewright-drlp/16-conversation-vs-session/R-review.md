# R — Review：Conversation Surface vs Session Domain：UI 语言与 Kernel 原语

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

- Phase 2.2 用测试明确禁止 Session 字段。
- UI 已预留未来 Session 形态。

## Findings

|级别|发现|为什么重要|
|---|---|---|
|Material|Stage B 的首个重要迁移是把 transient transcript 替换为 Session-backed conversation|需要迁移 message ownership、active artifact refs、title/history。|
|Material|不能直接把当前 conversation_messages JSON 化就宣称 Session 完成|还缺 tool_calls、workspace binding、durability、context composition、lifecycle。|

## Materiality Reconciliation

以下边界已经被审阅，但没有因为“还能加功能”而自动列为缺陷：

- Conversation ≠ memory。
- Conversation ≠ task execution state。
- Session 未来必须是 durable/domain-level，而不是 QWidget state。

Material finding 只保留会改变**正确性、下一阶段接口、信任边界或用户可解释性**的问题。

## Review 结论

当前状态：**Conversation 已实现；Session 明确未实现**。

总体上，该概念在当前阶段的边界是自洽的；最重要的是继续保持“当前实现”和“Canonical Future Contract”的区分。任何后续增强都应由具体失败模式触发，而不是为了让概念列表更完整。

下一步：[L-learning.md](./L-learning.md)
