# R — Review：Eval / Feedback Loop：如何证明系统真的工作

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

- Parser 与 Context 分开测试。
- 权限/fallback/跨 Workspace 等失败模式有回归。
- wheel smoke 捕获安装态缺陷。

## Findings

|级别|发现|意义|
|---|---|---|
|Material|真实脱敏 corpus 不足|复杂办公版式与历史模板需要 golden corpus/failure taxonomy。|
|Material|任务级 Eval 还弱|进入 Search/Agent 后要评估 evidence、tool choice、step、recovery。|
|Material|需要标准失败归因|同一“答案错”应能归 Parser/Context/Retrieval/Tool/Model/State。|

## Materiality

这里不把“未来还能做更多”自动判成缺陷。优先守住当前边界：

- 测试数量不是质量分。
- 合成 fixture 不代表真实银行文档分布。
- 关键词 QA 只能做 smoke。
- CI 证明可重复，不证明产品价值。

## Review 结论

当前设计总体能支撑它声明的阶段目标；Material findings 主要说明**下一阶段不能沿用哪些隐含假设**，而不是要求现在一次性补齐完整 Agent 架构。

下一步：[L-learning.md](./L-learning.md)
