# L — Learning：Artifact Write Lifecycle：Version、Patch、Validate、Diff

> SenseWright：**System Learning V0.5.3**  
> 路径：Ground → Run Once → Explain → Vary One Condition → Model → Use

## Ground Object

用户要求把 DOCX 第 3 节某段改成新表述，然后查看差异再确认保存。

## Run Once

1. 读取 base Artifact + version。
2. LLM 生成语义修改意图。
3. Tool 转成 replace(locator,new_content) Patch。
4. Provider 校验 base_version 并应用。
5. 生成新版本。
6. Validate。
7. Diff 展示给用户。

## Mechanism：为什么这样跑

- 写入副作用需要可定位、可版本化、可审计。
- 自然语言 instruction 不能作为唯一执行 Contract。

## Boundary Variation

一次只改变一个高信息量条件：

> **源文件在 Patch 应用前被 Word 外部修改。**

结果：

- base_version 不匹配。
- 系统应 conflict/reload/rebase，而不是盲写。
- 这正是 Version 不可省略的原因。

这个变化用来检查当前模型哪些仍成立、哪些削弱、哪些变成新问题，而不是做穷举。

## Knowledge Model

- Write = Patch against Version → New Version → Validate → Diff。

## Gaps

- Version schema。
- 第一批 patch ops。
- DOCX writer/provider。
- visual/business validation。

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
