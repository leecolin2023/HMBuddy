# R — Review：Config vs State vs Task：应用状态与任务状态

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

- Config/State 分离明确。
- field source tracking 解决 env override 可解释性。
- Recent Task 明确不冒充执行状态。

## Findings

|级别|发现|意义|
|---|---|---|
|Material|RecentTask.status 易被误读为执行状态|实现时应持续强调它是 history/navigation status。|
|Material|Plugin enable/disable 需要重建 live Runtime|Config 只记录意图，不能持久化 Runtime 对象。|
|Material|field-level source tracking 不能省略|否则 UI 修改后被 env 覆盖会被误判为保存失败。|

## Materiality

这里不把“未来还能做更多”自动判成缺陷。优先守住当前边界：

- Recent Task 只解决“回到哪里”。
- config 不存明文 API key。
- state 默认不存正文/Prompt/Answer。
- JSON 当前足够，大量任务/并发出现后再评估 SQLite。

## Review 结论

当前设计总体能支撑它声明的阶段目标；Material findings 主要说明**下一阶段不能沿用哪些隐含假设**，而不是要求现在一次性补齐完整 Agent 架构。

下一步：[L-learning.md](./L-learning.md)
