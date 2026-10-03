# L — Learning：Context + LLM Interface：模型实际看到什么

> SenseWright：**System Learning V0.5.3**  
> 路径：Ground → Run Once → Explain → Vary One Condition → Model → Use

## Ground Object

用户连续问两轮：第一轮解释缩写，第二轮说“那它的期限呢？”

## Run Once

1. UI 显示两轮 Conversation。
2. Controller 保存临时 transcript。
3. 但 llm_client.ask 当前只接 current Artifact + 当前 question。
4. 第二轮模型并不会自动看到第一轮回答。

## Mechanism：为什么这样跑

- Presentation transcript 与模型 Session Context 是两套概念。
- Phase 2.2 刻意不提前实现半套 Session。

## Boundary Variation

一次只改变一个高信息量条件：

> **只改变一个条件：Stage B 引入 Session.messages。**

结果：

- Context Builder 需要加入 Session message selection。
- Conversation 才真正变成多轮语义。
- Context budget/compaction 变成更重要的 Kernel invariant。

这个变化用来检查当前模型哪些仍成立、哪些削弱、哪些变成新问题，而不是做穷举。

## Knowledge Model

- Context = model-call visibility boundary。
- UI 上看得到 ≠ 模型本轮看得到。

## Gaps

- Session message composition。
- 多 Artifact/search context。
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
