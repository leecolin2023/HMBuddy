# R — Review：Plugin Runtime：发现、装载、注册、路由与执行

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

- 外部插件能在不改 Core 下进入完整链路。
- Phase 1.1.1 修复了 Manifest 权威、权限、选择诊断、package loader 等治理问题。
- 失败可 trace，不塌缩为“不支持格式”。

## Findings

|级别|发现|意义|
|---|---|---|
|Material|进程内插件无法隔离恶意代码|开放第三方生态前需要签名/白名单/子进程或 OS sandbox。|
|Material|动态 reload 生命周期尚未一等化|Phase 2.1 enable/disable/rescan 需要明确 Registry/Runtime/Catalog 如何原子切换。|
|Material|priority 不解决质量/成本权衡|多个 OCR/视觉 Provider 并存时可能需要更丰富选择策略。|

## Materiality

这里不把“未来还能做更多”自动判成缺陷。优先守住当前边界：

- 进程内插件不是 sandbox。
- priority 是确定性选择规则，不是质量评分。
- fallback 只针对显式 allowlist。
- API version 目前是 v1。

## Review 结论

当前设计总体能支撑它声明的阶段目标；Material findings 主要说明**下一阶段不能沿用哪些隐含假设**，而不是要求现在一次性补齐完整 Agent 架构。

下一步：[L-learning.md](./L-learning.md)
