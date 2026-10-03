# L — Learning：AppConfig / EffectiveConfig：配置、来源优先级与本地数据目录

> SenseWright：**System Learning V0.5.3**  
> 路径：Ground → Run Once → Explain → Vary One Condition → Model → Use

## Ground Object

config.json 里 model=qwen，但启动环境 HMBUDDY_LLM_MODEL=deepseek。

## Run Once

1. 加载 AppConfig 得到用户值。
2. resolve_effective_config 发现 env override。
3. EffectiveValue=model=deepseek/source=Environment。
4. Settings 展示实际值与来源。
5. Runtime 用 deepseek，而不是误导用户认为 qwen 已生效。

## Mechanism：为什么这样跑

- 保存成功不等于运行值改变。
- 没有 source tracking 时用户会把部署策略误判成 bug。

## Boundary Variation

一次只改变一个高信息量条件：

> **用户显式设置 restore_last_workspace=False。**

结果：

- False 必须被识别为 User Config，而不是 falsey→Default True。
- 这正是 2.1.1 修复的语义。

这个变化用来检查当前模型哪些仍成立、哪些削弱、哪些变成新问题，而不是做穷举。

## Knowledge Model

- AppConfig = desired settings；EffectiveConfig = resolved runtime truth。

## Gaps

- 企业强制策略 source。
- 未来 schema migration。

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
