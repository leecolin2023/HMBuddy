# R — Review：Tool / Agent Loop：从问答到自主行动

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

- 现有 Runtime 为工具执行提供稳定治理底座。
- 项目没有过早引入 Agent Loop。
- Phase 2.1 先补应用状态是合理前置。

## Findings

|级别|发现|意义|
|---|---|---|
|Material|缺 Tool Contract|CapabilityRequest 是 Runtime 内部请求，不等于模型可见的参数/结果 schema。|
|Material|缺 Agent State/termination|没有 step/budget/action/observation 状态就无法调试或稳定停止。|
|Material|Search 能力不足|只给模型 list-all + read-full 会在大 Workspace 中高成本且容易选错。|

## Materiality

这里不把“未来还能做更多”自动判成缺陷。优先守住当前边界：

- Agent Loop 不应直接 import Adapter/Provider。
- 首版不顺手开放 write/network/process。
- Planner 不是 Agent 成立的前提。
- Tool Contract 与 Capability Contract 可以映射但不是同一层。

## Review 结论

当前设计总体能支撑它声明的阶段目标；Material findings 主要说明**下一阶段不能沿用哪些隐含假设**，而不是要求现在一次性补齐完整 Agent 架构。

下一步：[L-learning.md](./L-learning.md)
