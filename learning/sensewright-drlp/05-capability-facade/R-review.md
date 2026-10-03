# R — Review：Stable Facade + Capability：应用意图与 Runtime 能力

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

- 当前 Desktop 已经通过 Reader/Facade 复用 Runtime。
- 未来 Tool 可封装多个 capability。

## Findings

|级别|发现|为什么重要|
|---|---|---|
|Material|未来 read.range/read.outline/create/patch 要先定义 Result Contract|不能只把名字加进 namespace。|
|Material|Agent Tool 不应一一暴露 capability|否则模型工具面会被底层格式/模式细节淹没。|
|Minor|ArtifactReader 未来可能拆为多个 facade|由真实能力膨胀再决定。|

## Materiality Reconciliation

以下边界已经被审阅，但没有因为“还能加功能”而自动列为缺陷：

- 预留 capability 名不等于已经有 Contract。
- mode 参数未来不能与 capability 双重控制语义。
- Agent 不应直接看全部底层 capability。

Material finding 只保留会改变**正确性、下一阶段接口、信任边界或用户可解释性**的问题。

## Review 结论

当前状态：**artifact.read.full 已实现；其他能力为目标命名空间**。

总体上，该概念在当前阶段的边界是自洽的；最重要的是继续保持“当前实现”和“Canonical Future Contract”的区分。任何后续增强都应由具体失败模式触发，而不是为了让概念列表更完整。

下一步：[L-learning.md](./L-learning.md)
