# R — Review：Workspace：工作空间、发现边界与信任域

> SenseWright：Vibe Review V0.10  
> 本篇重新读取 Raw Source；D 仅可作为导航，不能作为证据。

## Review Assignment

判断该设计是否足以完成当前阶段职责，以及哪些假设会在下一阶段被放大。

## Coverage Map

- Contract / identity
- 输入输出边界
- 控制权与依赖方向
- 错误/权限/状态（适用时）
- 与相邻层的耦合
- 非目标与未来扩展
- Eval / 可观察性

## 已经成立的部分

- 发现/解析分离。
- 能力目录来自 Registry，Plugin 架构闭环。
- Ref 带 workspace_id，边界不只靠 UI 约定。

## Findings

|级别|发现|意义|
|---|---|---|
|Material|路径型 identity 的长期性有限|未来 Persistent Task 若把 artifact_id 当长期对象身份，重命名/移动会使引用失效。|
|Material|Plugin rescan 与 Catalog 生命周期必须同步|Phase 2.1 真正做 enable/disable/rescan 时，需要保证 Workspace 与重建后的 Registry 观察同一能力集。|
|Minor|大目录扫描可能阻塞 UI|这是 Desktop 调度问题，应该后台化，不应把异步复杂度塞进 Workspace 核心。|

## Materiality

这里不把“未来还能做更多”自动判成缺陷。优先守住当前边界：

- 应用级信任边界，不是 OS sandbox。
- artifact_id 由路径生成，移动/重命名后会变化。
- 当前是本地文件系统实现，不等于未来所有 Workspace provider。
- 能发现什么不等于任务应该选择什么；语义选择属于 Search/Agent。

## Review 结论

当前设计总体能支撑它声明的阶段目标；Material findings 主要说明**下一阶段不能沿用哪些隐含假设**，而不是要求现在一次性补齐完整 Agent 架构。

下一步：[L-learning.md](./L-learning.md)
