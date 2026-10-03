# L — Learning：Eval / Feedback Loop：从失败模式到可回归证据

> SenseWright：**System Learning V0.5.3**  
> 路径：Ground → Run Once → Explain → Vary One Condition → Model → Use

## Ground Object

Preview UI 开发者为了方便直接 Path.read_text()。

## Run Once

1. 功能表面正常。
2. AST guard 在 CI 中捕获 open/read_text。
3. 失败直接说明破坏 Artifact Runtime boundary。
4. 开发者改为 Controller→Reader→Artifact→PreviewModel。

## Mechanism：为什么这样跑

- 边界问题往往 happy path 看不出来。
- Static architecture test 能把“设计原则”变成不可轻易回退的工程契约。

## Boundary Variation

一次只改变一个高信息量条件：

> **只改变一个条件：进入 AgentLoop 后模型能自主调用多个 Tool。**

结果：

- 最终文本断言不足。
- 必须记录/验证 action sequence、tool args、policy decision、stop reason。
- Eval 需要从输出级升级到轨迹级。

这个变化用来检查当前模型哪些仍成立、哪些削弱、哪些变成新问题，而不是做穷举。

## Knowledge Model

- 每个真实 failure 最终应变成最小回归证据。
- 分层 Eval 负责定位，端到端 Eval 负责用户任务。

## Gaps

- 真实 corpus。
- Agent trace Eval。
- Office write golden/diff validation。

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
