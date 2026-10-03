# L — Learning：Artifact Preview：可读取、可表示、可预览是三件不同的事

> SenseWright：**System Learning V0.5.3**  
> 路径：Ground → Run Once → Explain → Vary One Condition → Model → Use

## Ground Object

用户点击 sample.docx。

## Run Once

1. Reader 成功生成 Artifact。
2. PreviewModel 判断 .docx 不在当前 supported set。
3. Pane 显示 Unsupported。
4. Conversation QA 仍可继续使用 blocks/context。

## Mechanism：为什么这样跑

- 结构解析与像素/排版还原完全不同。
- 明确 Unsupported 比偷偷显示糟糕纯文本更诚实。

## Boundary Variation

一次只改变一个高信息量条件：

> **增加一个 HTML export renderer，可被 Desktop、CLI、Tool 共同复用。**

结果：

- Presentation-only 边界开始削弱。
- 此时可评估 artifact.render capability，因为输出已成为跨产品面的稳定能力。

这个变化用来检查当前模型哪些仍成立、哪些削弱、哪些变成新问题，而不是做穷举。

## Knowledge Model

- Artifact 是事实；PreviewModel 是某个产品面的 Representation。

## Gaps

- Office Rich Preview。
- 跨客户端 render capability 判断标准。

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
