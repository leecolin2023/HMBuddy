# R — Review：Plugin Manager / System Status：把 Runtime 事实翻译成产品可解释性

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

- 真实聚合状态。
- 错误插件不阻断其他插件。
- Product 表达与 Runtime 单一事实保持一致。

## Findings

|级别|发现|为什么重要|
|---|---|---|
|Material|未来 Capability Plugin 与 Agent Extension UI 需要概念分组|安装体验可以统一，但 Product View 不能把二者语义混成同一种插件。|
|Minor|外部插件目录增删 UI 尚未完整|当前允许 config/env + rescan，属于产品完善项而非 Kernel 缺陷。|

## Materiality Reconciliation

以下边界已经被审阅，但没有因为“还能加功能”而自动列为缺陷：

- UI enable/disable 写 AppConfig，不修改 plugin.json。
- Plugin Manager 不负责授予高权限。
- Status Dot 是解释入口，不是监控平台。

Material finding 只保留会改变**正确性、下一阶段接口、信任边界或用户可解释性**的问题。

## Review 结论

当前状态：**Phase 2.1 已实现，2.1.1/2.2 加固产品视图**。

总体上，该概念在当前阶段的边界是自洽的；最重要的是继续保持“当前实现”和“Canonical Future Contract”的区分。任何后续增强都应由具体失败模式触发，而不是为了让概念列表更完整。

下一步：[L-learning.md](./L-learning.md)
