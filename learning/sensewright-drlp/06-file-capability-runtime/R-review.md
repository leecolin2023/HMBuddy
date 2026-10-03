# R — Review：File Capability Runtime：Manifest、Plugin、Provider、Registry、Router

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

- 外部 package/相对 import 已支持。
- 失败隔离与选择诊断已建立。
- Workspace Catalog 能从 Registry 派生。

## Findings

|级别|发现|为什么重要|
|---|---|---|
|Material|动态重载已经进入产品，但仍是重建 Runtime 模式|未来存在长 Session/AgentLoop 时，要定义 active run 与 plugin rescan 的一致性。|
|Material|不要把 ExtensionHost 塞进现有 plugin_runtime|架构总纲已明确两者职责不同。|
|Minor|未来 Provider 质量/成本选择可能超出 priority|由真实多 Provider 场景再引入策略。|

## Materiality Reconciliation

以下边界已经被审阅，但没有因为“还能加功能”而自动列为缺陷：

- 进程内插件不是安全隔离。
- Capability Plugin ≠ Agent Extension。
- priority ≠ 质量评分。

Material finding 只保留会改变**正确性、下一阶段接口、信任边界或用户可解释性**的问题。

## Review 结论

当前状态：**已实现并硬化**。

总体上，该概念在当前阶段的边界是自洽的；最重要的是继续保持“当前实现”和“Canonical Future Contract”的区分。任何后续增强都应由具体失败模式触发，而不是为了让概念列表更完整。

下一步：[L-learning.md](./L-learning.md)
