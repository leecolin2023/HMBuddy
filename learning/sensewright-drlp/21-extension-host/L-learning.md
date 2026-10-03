# L — Learning：ExtensionHost / Hooks / Events：高级 Agent 能力的统一扩展面

> SenseWright：**System Learning V0.5.3**  
> 路径：Ground → Run Once → Explain → Vary One Condition → Model → Use

## Ground Object

edit_file Tool 即将修改一个 DOCX。

## Run Once

1. AgentLoop 发出 tool_call。
2. before_tool hooks 执行。
3. Approval Extension 依据 Policy 判断 ASK。
4. Product UI 展示 diff/确认。
5. 允许后 ToolRegistry 执行。
6. after_tool Audit Extension 记录结果。

## Mechanism：为什么这样跑

- Approval 不需要重写 AgentLoop。
- Audit 也不需要 edit_file 自己知道审计系统。

## Boundary Variation

一次只改变一个高信息量条件：

> **安装两个 before_tool Extension，一个 allow、一个 deny。**

结果：

- 必须有明确组合语义：deny 是否优先、ask 如何聚合。
- 这暴露 Hook Contract 是真正 Kernel API，不可随意。

这个变化用来检查当前模型哪些仍成立、哪些削弱、哪些变成新问题，而不是做穷举。

## Knowledge Model

- Extension = behavior around the loop；Hook = stable insertion point；Event = observable fact。

## Gaps

- Hook ordering/conflict。
- Extension permission model。
- UI extension surface。

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
