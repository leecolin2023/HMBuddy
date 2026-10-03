# L — Learning：AppState / Recent Workspace / Recent Activity：轻量恢复而非 Task 域

> SenseWright：**System Learning V0.5.3**  
> 路径：Ground → Run Once → Explain → Vary One Condition → Model → Use

## Ground Object

用户昨天打开一个 Artifact 并做 QA，今天重启应用。

## Run Once

1. state.json 恢复 RecentWorkspace/Activity。
2. Sidebar 显示对应条目。
3. 点击 activity 按 workspace/artifact path 恢复视图。
4. 没有恢复昨天的对话、模型状态或执行步骤。

## Mechanism：为什么这样跑

- 导航恢复需要很少元数据。
- 执行恢复需要强一致 Session state，语义完全不同。

## Boundary Variation

一次只改变一个高信息量条件：

> **只改变一个条件：昨天 Agent 已完成 5/10 个 Tool calls 后崩溃。**

结果：

- Recent Activity 无法回答下一步是什么。
- 需要 Session/SessionStore，而不是给 RecentActivity 继续加 execution fields。

这个变化用来检查当前模型哪些仍成立、哪些削弱、哪些变成新问题，而不是做穷举。

## Knowledge Model

- AppState = rebuildable product history；Session = durable agent work context。

## Gaps

- Session Index 迁移策略。
- 更多隐私清理策略。

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
