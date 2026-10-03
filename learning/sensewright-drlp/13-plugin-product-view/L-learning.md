# L — Learning：Plugin Manager / System Status：把 Runtime 事实翻译成产品可解释性

> SenseWright：**System Learning V0.5.3**  
> 路径：Ground → Run Once → Explain → Vary One Condition → Model → Use

## Ground Object

一个插件注册两个 Provider，其中一个 unavailable，另一个正常。

## Run Once

1. Runtime reports/provider availability 形成真实数据。
2. build_plugin_views 聚合为一个 Plugin 行。
3. Provider 明细展示不同状态/原因。
4. 整体 Plugin status 按规则聚合。

## Mechanism：为什么这样跑

- 用户关注‘这个插件是否可用’，但排障需要看到 Provider 层原因。

## Boundary Variation

一次只改变一个高信息量条件：

> **未来 ExtensionHost 也有可安装 Extension。**

结果：

- 安装列表可统一呈现。
- 但 Capability Plugin 的 capability/provider 与 Agent Extension 的 tools/hooks/skills 需要不同详情模型。

这个变化用来检查当前模型哪些仍成立、哪些削弱、哪些变成新问题，而不是做穷举。

## Knowledge Model

- Product View 是 Runtime facts 的 projection，不是新事实源。

## Gaps

- Capability Plugin vs Extension 的统一安装/分组 UX。
- 企业权限策略展示。

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
