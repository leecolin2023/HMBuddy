# R — Review：Stable Facade + Capability：稳定入口与能力语义

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

- Desktop 已只依赖稳定 Facade。
- Request 禁止实现对象穿透。
- Capability-first Registry 支持多 Provider。

## Findings

|级别|发现|意义|
|---|---|---|
|Material|未来要收口 mode 与 capability|若 mode='outline' 与 artifact.read.outline 同时决定行为，会出现组合歧义。|
|Material|预留 capability 不等于已有 Contract|artifact.update 落地前还需定义定位、冲突、权限、幂等。|
|Material|ArtifactReader 未来可能膨胀|能力变多时应考虑多个 facade 共享 Runtime，而不是所有能力都塞进 Reader。|

## Materiality

这里不把“未来还能做更多”自动判成缺陷。优先守住当前边界：

- 未来应避免 mode 参数与 capability 形成两套事实源。
- 预留名字不是实现承诺。
- Capability 不负责选择 Provider。
- 不要退化成 docx.read 这类格式别名。

## Review 结论

当前设计总体能支撑它声明的阶段目标；Material findings 主要说明**下一阶段不能沿用哪些隐含假设**，而不是要求现在一次性补齐完整 Agent 架构。

下一步：[L-learning.md](./L-learning.md)
