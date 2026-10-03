# L — Learning：Application Runtime Composition：Controller 与单一运行时事实

> SenseWright：**System Learning V0.5.3**  
> 路径：Ground → Run Once → Explain → Vary One Condition → Model → Use

## Ground Object

用户修改 Plugin 目录和 LLM model 后点击 Save。

## Run Once

1. ConfigStore 保存用户意图。
2. EffectiveConfig 用同一 env 重新解析。
3. assemble_app_runtime 构建新 plugin assembly/catalog/LLM。
4. Controller 替换 Reader。
5. 若 Workspace 已打开，用新 Catalog 重建 refs。
6. Shell 刷新 Product View。

## Mechanism：为什么这样跑

- 一个设置变化可能同时影响多个运行对象。
- 集中组合比各页面自己读配置更能保证一致性。

## Boundary Variation

一次只改变一个高信息量条件：

> **只改变一个条件：未来有正在执行的 Session。**

结果：

- 直接热替换全局 Runtime 可能改变 Session 中途语义。
- 需要决定 Session pin runtime config/version，或显式允许动态切换。

这个变化用来检查当前模型哪些仍成立、哪些削弱、哪些变成新问题，而不是做穷举。

## Knowledge Model

- Composition Root = 把配置意图编译成一组一致的 live objects。

## Gaps

- Session runtime snapshot。
- 未来 dependency injection 生命周期。

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
