# R — Review：Human-in-the-loop Desktop：薄应用层与人工控制点

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

- UI 通过稳定 Facade。
- Presenter 可测。
- 人工选择让任务输入与 trust domain 清晰。

## Findings

|级别|发现|意义|
|---|---|---|
|Material|desktop/app.py 未来会因 Home/Settings/Plugins 膨胀|Phase 2.1 应拆 Application Services 与页面职责。|
|Material|Workspace scan 应在真实大目录下后台化|问题属于 UI 调度，不应修改 Workspace 核心。|
|Material|Agent 化后仍需保留确认点|自动选文件不等于写操作/高权限动作也自动执行。|

## Materiality

这里不把“未来还能做更多”自动判成缺陷。优先守住当前边界：

- Desktop 不应 import Adapter/Plugin。
- 后台线程解决 responsiveness，不等于任务可恢复。
- Workspace scan 当前可能仍同步阻塞大目录。
- 关闭应用后没有真正 persistent execution state。

## Review 结论

当前设计总体能支撑它声明的阶段目标；Material findings 主要说明**下一阶段不能沿用哪些隐含假设**，而不是要求现在一次性补齐完整 Agent 架构。

下一步：[L-learning.md](./L-learning.md)
