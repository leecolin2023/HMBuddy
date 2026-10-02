# R — Review：Policy / Permission / Trust Boundary：运行时安全边界

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

- required_permissions 在副作用前阻断。
- 动态权限适合 xlrd→COM fallback 这类路径。
- 安全错误不 fallback。

## Findings

|级别|发现|意义|
|---|---|---|
|Material|不能把现有 Policy 宣称为 sandbox|不可信插件需要进程/OS 级隔离或签名白名单。|
|Material|写能力不能只加 filesystem.write|还需目标范围、确认、版本冲突、回滚/审计。|
|Material|企业 Policy 不能被 UI 任意覆盖|Phase 2.1 的 Plugin Manager 应展示权限，不应顺手实现自由授予高权限。|

## Materiality

这里不把“未来还能做更多”自动判成缺陷。优先守住当前边界：

- 同进程 Python 插件可以绕过 Runtime API，因此不是恶意代码防护。
- Workspace 也不能阻止恶意插件自行访问别处。
- write/network/process 未来需要更强用户确认与审计。
- Declared、Granted、Used 是三件不同的事。

## Review 结论

当前设计总体能支撑它声明的阶段目标；Material findings 主要说明**下一阶段不能沿用哪些隐含假设**，而不是要求现在一次性补齐完整 Agent 架构。

下一步：[L-learning.md](./L-learning.md)
