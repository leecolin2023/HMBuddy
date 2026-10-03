# L — Learning：Adapter / Parsing Boundary：Native Structure、OCR 与 COM

> SenseWright：**System Learning V0.5.3**  
> 路径：Ground → Run Once → Explain → Vary One Condition → Model → Use

## Ground Object

读取同样是一张表：一个来自 XLSX，一个来自扫描 PDF。

## Run Once

1. XLSX 直接恢复 sheet/cell 网格。
2. PDF 先做页面/几何/OCR。
3. 两条路径直到形成 table block 才重新统一。
4. 上层 Context/Preview 不关心具体 parser。

## Mechanism：为什么这样跑

- 统一过早会扭曲源结构。
- 统一过晚会把格式知识扩散到所有上层。

## Boundary Variation

一次只改变一个高信息量条件：

> **把 PDF OCR 替换为另一个视觉模型 Provider。**

结果：

- Parser/Provider 细节变化。
- Artifact Contract 与上层保持稳定。
- 如果结果包含置信度需求，才可能触发 Artifact metadata/Contract 演进。

这个变化用来检查当前模型哪些仍成立、哪些削弱、哪些变成新问题，而不是做穷举。

## Knowledge Model

- Adapter = Native format compiler frontend。
- Provider = Runtime wrapper；Artifact = IR。

## Gaps

- 非确定性解析 evidence。
- 写能力实现边界。
- 性能/资源观测。

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
