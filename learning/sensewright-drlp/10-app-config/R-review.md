# R — Review：AppConfig / EffectiveConfig：配置、来源优先级与本地数据目录

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

- 来源可解释。
- Secret 边界清楚。
- 原子写与 schema_version 从第一版建立。

## Findings

|级别|发现|为什么重要|
|---|---|---|
|Material|未来企业集中策略可能高于普通 Environment|如果出现强制模型/插件策略，需要显式 Enterprise Policy source，而不是偷偷复用 Runtime override。|
|Material|Config change 的 live-effect contract 要持续明确|哪些立即生效、哪些重建 Runtime/LLM、哪些未来需要 restart。|
|Minor|未知字段保留策略可在真正 schema 演进时加强|当前版本足够。|

## Materiality Reconciliation

以下边界已经被审阅，但没有因为“还能加功能”而自动列为缺陷：

- Config 不是 AppState。
- Runtime object 不持久化进 Config。
- 环境变量来源的值不能让 UI 假装已被用户设置覆盖。

Material finding 只保留会改变**正确性、下一阶段接口、信任边界或用户可解释性**的问题。

## Review 结论

当前状态：**Phase 2.1 已实现，2.1.1 已加固 False/0 与显式 env**。

总体上，该概念在当前阶段的边界是自洽的；最重要的是继续保持“当前实现”和“Canonical Future Contract”的区分。任何后续增强都应由具体失败模式触发，而不是为了让概念列表更完整。

下一步：[L-learning.md](./L-learning.md)
