# R — Review：Artifact / ArtifactBlock：统一中间表示

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

- 内部 IR 与 LLM Context 分离。
- 保留格式特有结构，避免最低公分母。
- Locator 进入核心契约，为未来写回建立寻址基础。

## Findings

|级别|发现|意义|
|---|---|---|
|Material|开放 metadata 可能变成隐式协议垃圾桶|当 Search/Compare/Update 依赖某些字段时，应将关键语义升级成版本化 Contract。|
|Material|Locator 尚缺跨版本重定位语义|paragraph_index/table_index 在源文档插入内容后可能漂移，Update 阶段需 revision/conflict 机制。|
|Material|写回前还缺 source revision|解析后文件若被外部修改，仅靠 path+locator 无法安全 patch。|

## Materiality

这里不把“未来还能做更多”自动判成缺陷。优先守住当前边界：

- 统一不等于纯文本化，复杂结构继续保留。
- metadata 是开放 dict，扩展性高但也有 schema 漂移风险。
- Locator 是 Update 的前提，不等于完整写回契约。
- 路径型 artifact_id 不是内容哈希或全局对象 ID。

## Review 结论

当前设计总体能支撑它声明的阶段目标；Material findings 主要说明**下一阶段不能沿用哪些隐含假设**，而不是要求现在一次性补齐完整 Agent 架构。

下一步：[L-learning.md](./L-learning.md)
