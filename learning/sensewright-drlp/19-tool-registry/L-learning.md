# L — Learning：Tool / ToolRegistry：模型动作接口与 Capability 的桥

> SenseWright：**System Learning V0.5.3**  
> 路径：Ground → Run Once → Explain → Vary One Condition → Model → Use

## Ground Object

模型调用 read_file({artifact_id, mode:'outline'})。

## Run Once

1. ToolRegistry 验证 schema。
2. handler 解析受控 Ref。
3. 选择 artifact.read.outline capability。
4. Runtime 执行 Provider。
5. ToolResult 返回结构摘要/引用。

## Mechanism：为什么这样跑

- Agent 不需要知道实现细节。
- 能力细分不应膨胀模型工具面。

## Boundary Variation

一次只改变一个高信息量条件：

> **新增 PDF 专用 OCR Provider。**

结果：

- Tool schema 不变。
- Capability Runtime 内部选择变化。
- 验证了 Tool/Capability 分层。

这个变化用来检查当前模型哪些仍成立、哪些削弱、哪些变成新问题，而不是做穷举。

## Knowledge Model

- Tool = model-facing action；Capability = runtime-facing service intent。

## Gaps

- Tool Result schema。
- search/read range capabilities。
- approval integration。

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
