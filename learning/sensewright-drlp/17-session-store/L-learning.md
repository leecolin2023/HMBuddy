# L — Learning：Session / SessionStore：持久工作上下文、Product Task 与 Resume

> SenseWright：**System Learning V0.5.3**  
> 路径：Ground → Run Once → Explain → Vary One Condition → Model → Use

## Ground Object

用户让 Agent 阅读 8 份文件生成报告，中途关闭应用，第二天继续。

## Run Once

1. 创建 Session 绑定 workspace_id。
2. 每轮 message/tool call/result 写入 SessionStore。
3. Artifact refs 留在 Session。
4. 关闭后仅 SessionStore 保留 durable context。
5. 重启从 Session Index 载入并继续。

## Mechanism：为什么这样跑

- 恢复需要的是工作上下文，而不是 UI 页位置。
- 工具轨迹比重型 DAG 更贴近极简 AgentLoop。

## Boundary Variation

一次只改变一个高信息量条件：

> **任务出现严格步骤依赖和跨日 exactly-once side effect。**

结果：

- 简单 Session 可能不够。
- 这才构成引入更强 Task/Workflow Contract 的真实证据。

这个变化用来检查当前模型哪些仍成立、哪些削弱、哪些变成新问题，而不是做穷举。

## Knowledge Model

- Session = durable context + history；Product Task 是它的产品投影。

## Gaps

- schema/versioning。
- runtime snapshot。
- artifact revision。

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
