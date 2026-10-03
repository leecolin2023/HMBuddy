# R — Review：Artifact Preview：可读取、可表示、可预览是三件不同的事

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

- Representation 层清晰。
- 数据来源单一。
- 安全边界有静态测试。

## Findings

|级别|发现|为什么重要|
|---|---|---|
|Material|未来 Office Rich Preview 需要先判断是 Presentation renderer 还是新的 render capability|如果只是本地 UI 展示可继续在 Product 层；如果多个客户端/Tool 都需要稳定渲染产物，才考虑 capability。|
|Minor|artifact_type→extension 的映射当前简单|复杂别名出现时可由 Artifact metadata 明确 representation type。|

## Materiality Reconciliation

以下边界已经被审阅，但没有因为“还能加功能”而自动列为缺陷：

- Preview 不是 artifact.render capability。
- 当前 Markdown renderer 是 Qt 子集。
- Unsupported 不影响 QA/read。

Material finding 只保留会改变**正确性、下一阶段接口、信任边界或用户可解释性**的问题。

## Review 结论

当前状态：**Phase 2.2 已实现 Markdown/TXT Preview**。

总体上，该概念在当前阶段的边界是自洽的；最重要的是继续保持“当前实现”和“Canonical Future Contract”的区分。任何后续增强都应由具体失败模式触发，而不是为了让概念列表更完整。

下一步：[L-learning.md](./L-learning.md)
