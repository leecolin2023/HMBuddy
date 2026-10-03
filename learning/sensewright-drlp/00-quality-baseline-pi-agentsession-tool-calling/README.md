# Quality Baseline — Pi AgentSession / Tool Calling Vertical Slice

**学习协议：** HMBuddy × SenseWright Technical Learning Protocol V1.0  
**状态：** MECHANISM-VALIDATED / Practice mapping ready; HMBuddy VNext runtime execution pending  
**Pi source pin：** earendil-works/pi@4c6fb7cfe8c538a668726f6f8b3554098c39faee  
**Pi package：** @earendil-works/pi-coding-agent 1.0.0  
**HMBuddy baseline：** Architecture V1.0 + VNext-01

---

这不是旧 23 个概念中的“第 24 篇”。

它是 V1.0 学习协议的第一个质量样板，用来回答：

> 一个原本没有读过 Pi 源码的人，怎样真正理解“AgentSession 如何把一次用户 Prompt 变成模型 Tool Call、Tool 执行、Observation、再一次模型调用，直到最终回答”？

为什么选它：

1. 它跨过 HMBuddy V1.0 最关键的 Ownership Boundary；
2. 能同时看到 Session、Model、Tool、Extension、AgentLoop、事件；
3. VNext-01 的核心验收链就是这个 vertical slice；
4. 如果这一篇仍然只能被熟悉 Agent 的人读懂，说明 V1.0 协议没有解决旧问题。

文件：

- D — Deep Read：从“为什么需要”开始，沿真实源码恢复调用链；
- R — Review：独立审阅理解是否准确，以及对 HMBuddy 的约束；
- L — Learning：使用 Pi 自己的 checked deterministic test 让 Tool Calling 真正跑一次；
- P — Practice：把理解投影到 HMBuddy VNext-01，具体到文件、接口、测试、trace、failure；
- Evidence — Source Map：固定源码证据与 source / derived / HMBuddy decision 边界。

## 当前为什么不是 PRACTICE-VALIDATED

Pi upstream 的机制路径已有真实 checked test 作为执行证据，因此 L 可以标记 MECHANISM-VALIDATED。

但 HMBuddy VNext-01 尚未在本仓库真正实现和运行，所以 P 中的工程路径虽然具体可执行，不能谎称已经在 HMBuddy runtime 中执行成功。

等 VNext-01 实施完成后，应把真实 test result / trace 回填到 P，并升级为：

~~~text
PRACTICE-VALIDATED
→ QUALITY-BASELINE
~~~

这个状态区分本身就是 V1.0 的一部分：**不再用“文档写完”代替“机制真的跑过”。**
