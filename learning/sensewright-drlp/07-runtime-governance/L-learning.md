# L — Learning：Runtime Governance：Policy、Availability、Fallback、Trace

> SenseWright：**System Learning V0.5.3**  
> 路径：Ground → Run Once → Explain → Vary One Condition → Model → Use

## Ground Object

旧 .doc Provider 需要 Office COM，但默认 Policy 只允许 filesystem.read。

## Run Once

1. Router 找到 Provider。
2. Runtime 检查 required office.com。
3. Policy 拒绝。
4. Provider 不进入 execute。
5. 失败 trace 记录 PermissionError，且无 fallback。

## Mechanism：为什么这样跑

- 权限记录若不控制执行，没有安全意义。
- 安全失败不能通过替换 Provider 偷偷继续。

## Boundary Variation

一次只改变一个高信息量条件：

> **显式授权 office.com。**

结果：

- 执行资格变化。
- Manifest 声明仍必须存在。
- 动态 gate 仍阻止未声明权限。

这个变化用来检查当前模型哪些仍成立、哪些削弱、哪些变成新问题，而不是做穷举。

## Knowledge Model

- Declared ≠ Granted ≠ Used。
- Runtime Governance 的核心是统一控制权。

## Gaps

- Agent 级 Approval。
- Session-linked audit。
- 写操作细粒度 policy。

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
