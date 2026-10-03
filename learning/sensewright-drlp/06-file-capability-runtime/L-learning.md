# L — Learning：File Capability Runtime：Manifest、Plugin、Provider、Registry、Router

> SenseWright：**System Learning V0.5.3**  
> 路径：Ground → Run Once → Explain → Vary One Condition → Model → Use

## Ground Object

用户在 Settings 中禁用一个 PDF Provider 并 Rescan。

## Run Once

1. AppConfig 记录 disabled ID。
2. assemble_app_runtime 重新发现/加载插件。
3. 有效 Registry 排除 disabled provider。
4. Catalog、PluginView、Workspace 使用同一 assembly。

## Mechanism：为什么这样跑

- 声明存在与当前启用状态是不同维度。
- 重建 Registry 比在多处打 enabled if 更容易保持单一事实。

## Boundary Variation

一次只改变一个高信息量条件：

> **只改变一个条件：Agent Session 正在执行时 Rescan。**

结果：

- 当前桌面阶段没有 durable Session，所以影响有限。
- 未来必须决定一个 Session 固定 Runtime snapshot，还是允许中途切换。
- 这会成为 Stage B 的一致性问题。

这个变化用来检查当前模型哪些仍成立、哪些削弱、哪些变成新问题，而不是做穷举。

## Knowledge Model

- Capability Plugin 管“某能力如何实现”；Agent Extension 管“Agent 如何行为”。

## Gaps

- Session 期间 runtime snapshot 语义。
- 不可信插件隔离。

这些 Gap 只有在阻塞下一步时才进入实现，不为了“完整”全部提前建设。

## Prediction Check

如果把当前概念放到相邻场景，至少应能预测：

- 哪一层最先受到条件变化影响；
- 哪些 Contract 仍可复用；
- 哪些只是当前实现选择；
- 什么情况下需要回到 Architecture Change / Contract redesign。

## Project to Use

学习完本篇后，面对别的 Agent/办公系统，应先定位：**谁拥有控制权、状态在哪、实现细节在哪一层结束、上层依赖的稳定 Contract 是什么。**

下一步：[P-practice.md](./P-practice.md)
