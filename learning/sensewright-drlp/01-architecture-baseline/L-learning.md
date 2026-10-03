# L — Learning：架构总纲：WorkBuddy-like Product on a Pi-like Minimal Harness

> SenseWright：**System Learning V0.5.3**  
> 路径：Ground → Run Once → Explain → Vary One Condition → Model → Use

## Ground Object

产品提出“加入 Task、Memory、MCP、Automation、Planner 五个功能”。

## Run Once

1. 先把五个需求识别为 Product Capability。
2. 逐一尝试映射现有原语：Task→Session+metadata，Memory→before_model Extension，MCP→Extension 注册 Tools，Automation→Scheduler Extension 启动 Session，Planner→Skill/Extension。
3. 检查是否存在现有原语无法表达的真实失败。
4. 只有确实出现无法兼容的状态/安全/一致性需求，才提出 Architecture Change。

## Mechanism：为什么这样跑

- 功能名不等于系统原语。
- 减少 Core 数量能降低组合复杂度与迁移成本。
- Extension/Skill/Tool 允许产品快迭代，同时保护 AgentLoop/Workspace/Artifact 等关键 Contract。

## Boundary Variation

一次只改变一个高信息量条件：

> **只改变一个条件：某个长期自动化任务需要可靠 DAG 依赖、跨日重试和 exactly-once side effect。**

结果：

- “Task=Session+metadata”开始削弱。
- 此时不是因为市场上有 Workflow Engine 才增加模块，而是现有原语无法表达稳定依赖/重试/事务。
- 这成为可能的 Architecture Change 证据，但仍要比较 Extension/Scheduler 能否解决。

这个变化用来检查当前模型哪些仍成立、哪些削弱、哪些变成新问题，而不是做穷举。

## Knowledge Model

- Product features ≠ Kernel primitives。
- Kernel 保持小，复杂功能优先组合扩展面。
- Office 的领域复杂性通过 Artifact Runtime 承担，而不是塞进 AgentLoop。

## Gaps

- 六原语真正落地后的耦合是否仍足够小尚未被 Stage B 验证。
- Artifact 写能力尚未实证目标 Contract。
- ExtensionHost/Events 的最小 API 尚未实现。

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
