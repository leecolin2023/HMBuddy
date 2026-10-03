# R — Review：Artifact：Office 领域中间表示与稳定定位

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

- Parser 与上层完全通过 IR 解耦。
- Preview 也坚持消费 Artifact.content，不绕过 Runtime。
- Locator 已为未来 Patch 铺路。

## Findings

|级别|发现|为什么重要|
|---|---|---|
|Material|ArtifactVersion 尚未存在|进入可修改 Office Agent 前必须解决 base revision、并发修改和冲突检测。|
|Material|关键 metadata schema 未来应逐步正式化|一旦 Tool/Search/Validation 依赖某些字段，不能继续只靠隐式 dict key。|
|Minor|content 与 blocks 重复存储|当前服务于快速展示合理，但应保持 blocks 为结构事实源。|

## Materiality Reconciliation

以下边界已经被审阅，但没有因为“还能加功能”而自动列为缺陷：

- Markdown 是一种 Representation，不是 Artifact。
- 开放 metadata 需要契约纪律。
- Locator 目前并未保证跨版本稳定重定位。
- 当前以 read 为主，写生命周期尚未落地。

Material finding 只保留会改变**正确性、下一阶段接口、信任边界或用户可解释性**的问题。

## Review 结论

当前状态：**已实现 ArtifactRef/Artifact/ArtifactBlock/ArtifactLocator；Version/Patch 未来**。

总体上，该概念在当前阶段的边界是自洽的；最重要的是继续保持“当前实现”和“Canonical Future Contract”的区分。任何后续增强都应由具体失败模式触发，而不是为了让概念列表更完整。

下一步：[L-learning.md](./L-learning.md)
