# R — Review：Persistent Task / Recovery：任务中断、恢复与幂等

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

- Phase 2.1 已明确 Recent Task ≠ execution state。
- Workspace/Artifact/Trace 可作为未来 Task 引用基础。
- 先做 read-only recovery 符合项目节奏。

## Findings

|级别|发现|意义|
|---|---|---|
|Material|当前没有 Task/Step 状态机|没有严格状态转换无法可靠 resume。|
|Material|Trace 不能替代 checkpoint|观察日志不等于 accepted durable progress。|
|Material|side effect 需要幂等键|动作已成功但 checkpoint 未写时，简单重试会重复副作用。|

## Materiality

这里不把“未来还能做更多”自动判成缺陷。优先守住当前边界：

- 首版从只读恢复开始。
- Task status 应是严格状态机。
- Resume 前要验证 Workspace/Artifact/plugin/model 依赖。
- 写操作前必须有 idempotency/revision/confirmation。

## Review 结论

当前设计总体能支撑它声明的阶段目标；Material findings 主要说明**下一阶段不能沿用哪些隐含假设**，而不是要求现在一次性补齐完整 Agent 架构。

下一步：[L-learning.md](./L-learning.md)
