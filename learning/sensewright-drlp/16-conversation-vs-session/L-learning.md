# L — Learning：Conversation Surface vs Session Domain：UI 语言与 Kernel 原语

> SenseWright：**System Learning V0.5.3**  
> 路径：Ground → Run Once → Explain → Vary One Condition → Model → Use

## Ground Object

用户连续问两轮并关闭应用。

## Run Once

1. UI 显示两轮。
2. 进程关闭，conversation_messages 消失。
3. AppState 只保留 Recent Activity。
4. 重启后可回 Workspace/Artifact，但不能恢复对话。

## Mechanism：为什么这样跑

- 这正是 Presentation transcript 和 Session durable state 的差异。

## Boundary Variation

一次只改变一个高信息量条件：

> **引入真正 SessionStore。**

结果：

- 新建会话需要创建 session_id。
- Sidebar 可出现 Session History。
- Context 可选择 Session.messages。
- Recent Agent history 应迁移到 Session Index。

这个变化用来检查当前模型哪些仍成立、哪些削弱、哪些变成新问题，而不是做穷举。

## Knowledge Model

- Conversation = Product surface；Session = durable Kernel context。

## Gaps

- Session schema/store。
- message/tool-call representation。
- migration from Recent Activity。

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
