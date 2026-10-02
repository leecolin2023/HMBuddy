# R — Review：Adapter / Parsing Boundary：格式解析隔离层

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

- Reader 与具体 Adapter 解耦。
- 结构恢复优先于纯文本。
- OCR 模型默认本地、默认关闭，适合内网。

## Findings

|级别|发现|意义|
|---|---|---|
|Material|格式差异可能通过 metadata 隐式上泄|若上层开始读取格式专有键，应回头评估 Contract 是否不足。|
|Material|Provider 与 Adapter 责任需要持续守住|环境探针、权限、fallback 属于 Runtime，不应塞回解析器。|
|Minor|各格式 Locator 稳定性不同|进入 Update 后每种格式必须定义自己的重定位策略。|

## Materiality

这里不把“未来还能做更多”自动判成缺陷。优先守住当前边界：

- Adapter 不决定 Provider selection。
- Adapter 不负责 LLM budget。
- OCR 是解析策略，不是 UI/Context 分支。
- 未来 create/update 未必复用 read Adapter。

## Review 结论

当前设计总体能支撑它声明的阶段目标；Material findings 主要说明**下一阶段不能沿用哪些隐含假设**，而不是要求现在一次性补齐完整 Agent 架构。

下一步：[L-learning.md](./L-learning.md)
