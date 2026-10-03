# L — Learning：AgentLoop：最小自主决策闭环

> SenseWright：**System Learning V0.5.3**  
> 路径：Ground → Run Once → Explain → Vary One Condition → Model → Use

## Ground Object

“在工作区找到最新报告并告诉我风险点。”

## Run Once

1. Session 保存 goal。
2. Model 选择 list/search Tool。
3. Observation 返回候选。
4. Model 选择 read Tool。
5. Runtime 读取 Artifact。
6. Observation 回 Session。
7. Model 输出最终答案并 finish。

## Mechanism：为什么这样跑

- 没有循环时，人必须自己选文件。
- 一旦模型自己选择并根据结果继续，才出现 Agent control loop。

## Boundary Variation

一次只改变一个高信息量条件：

> **模型连续 5 次调用同一 read_file。**

结果：

- 需要 max_steps/repetition guard。
- 这不是 Planner 问题，先在 Loop 做最小 termination safety。

这个变化用来检查当前模型哪些仍成立、哪些削弱、哪些变成新问题，而不是做穷举。

## Knowledge Model

- AgentLoop = Decide → Act → Observe → Persist → Repeat/Stop。

## Gaps

- Tool schema。
- Session integration。
- Events/hooks。
- compaction。

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
