# L — Learning：Stable Facade + Capability：应用意图与 Runtime 能力

> SenseWright：**System Learning V0.5.3**  
> 路径：Ground → Run Once → Explain → Vary One Condition → Model → Use

## Ground Object

用户点击 Markdown File Card；系统内部有两个 Provider 能 read.full。

## Run Once

1. Product 只请求 read_artifact。
2. Facade 构造 capability request。
3. Runtime 选择 Provider。
4. 结果回到同一个 Artifact Contract。

## Mechanism：为什么这样跑

- Application 不应掌握 Provider policy。
- Provider 替换不应改变产品调用语义。

## Boundary Variation

一次只改变一个高信息量条件：

> **未来 read_file Tool 需要按问题只读某页/某区间。**

结果：

- Tool 仍可叫 read_file。
- 内部可根据参数选择 read.full/read.range/read.outline。
- Agent 工具面保持小，Capability Runtime 保持细粒度。

这个变化用来检查当前模型哪些仍成立、哪些削弱、哪些变成新问题，而不是做穷举。

## Knowledge Model

- Facade = 应用稳定入口；Capability = Runtime 稳定意图；Tool = 模型动作接口。

## Gaps

- range/outline Contract。
- write capability Contract。

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
