# L — Learning：Conversation-first Desktop Shell：Product Layer 与 Human-in-the-loop

> SenseWright：**System Learning V0.5.3**  
> 路径：Ground → Run Once → Explain → Vary One Condition → Model → Use

## Ground Object

用户打开 HMBuddy，只选择 Workspace，然后点击某 Markdown，再提问。

## Run Once

1. Sidebar 定位工作上下文。
2. 点击 File Card/搜索结果触发 Controller 读取 Artifact。
3. Conversation 负责提问/回答呈现。
4. Preview 同时展示 Artifact representation。
5. Runtime 链路保持原样。

## Mechanism：为什么这样跑

- Product Surface 可以重组而不改变 Domain Contract。
- UI 中‘当前工作’比‘功能页’更符合 Agent 心智。

## Boundary Variation

一次只改变一个高信息量条件：

> **只改变一个条件：用户不再先选择 Artifact，直接问“找最新报告并总结”。**

结果：

- 当前 Conversation Shell 仍可承载交互。
- 但 Controller/Kernel 不具备自主 list/search/read Tool loop。
- 缺口被清晰暴露为 Stage B/C，而不是 UI 再加按钮。

这个变化用来检查当前模型哪些仍成立、哪些削弱、哪些变成新问题，而不是做穷举。

## Knowledge Model

- Conversation-first 是 Product surface；Agent autonomy 是 Kernel control loop。两者独立演进。

## Gaps

- 持久 Session。
- Tool activity/approval presentation。
- 多 Artifact autonomous selection。

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
