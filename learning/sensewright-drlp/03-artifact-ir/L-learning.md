# L — Learning：Artifact：Office 领域中间表示与稳定定位

> SenseWright：**System Learning V0.5.3**  
> 路径：Ground → Run Once → Explain → Vary One Condition → Model → Use

## Ground Object

同一份 DOCX 既要给 LLM 问答，也要在右侧 Preview 中展示摘要，未来还要定位修改某段。

## Run Once

1. Adapter 把原生段落/表格变成 blocks。
2. Locator 记录源位置语义。
3. LLM Context 从 blocks 渲染。
4. Preview 只从 Artifact representation 构建 ViewModel。
5. 未来 edit_file 可基于 locator 产生 Patch，而不是重新解析 Prompt 文本。

## Mechanism：为什么这样跑

- 不同消费方需要不同 Representation，但都应从同一 IR 出发。
- 如果 UI/LLM/写工具分别读取原文件，就会出现三套解析事实。

## Boundary Variation

一次只改变一个高信息量条件：

> **只改变一个条件：所有文件永远是 .txt 且只做一次性问答。**

结果：

- Artifact 的复杂结构收益下降。
- 但 identity/provenance/统一错误仍有价值。
- 说明 Artifact-native 的必要性主要来自 Office 结构 + 多用途 + 持续修改。

这个变化用来检查当前模型哪些仍成立、哪些削弱、哪些变成新问题，而不是做穷举。

## Knowledge Model

- Artifact = Office 工作成果的内部 IR。
- Representation 可以很多，事实源应只有一个。
- Locator 是未来可验证写入的桥。

## Gaps

- Version/Patch/Diff。
- 跨版本 locator rebase。
- 格式无关 Validation contract。

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
