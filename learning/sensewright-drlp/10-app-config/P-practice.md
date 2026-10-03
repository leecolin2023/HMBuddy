# P — Practice：AppConfig / EffectiveConfig：配置、来源优先级与本地数据目录

> SenseWright：**Practice V0.2 / Knowledge → Execution**

## Real Engineering Scenario

增加一个新配置字段并完整实现 Default/User/Env/Runtime precedence 与 UI source。

## Engineering Model

- Typed resolver + EffectiveValue + atomic persistence。

## End-to-End Implementation

1. 定义 dataclass 字段。
2. 区分 unset sentinel。
3. 加入 env/runtime override。
4. 写 precedence matrix。
5. 在 Settings 展示 source。
6. 确保 secret/状态边界。

## One Concrete Path

```text
Built-in Defaults → User config.json → Environment → Runtime Overrides → EffectiveConfig + source → Runtime Assembly/UI
```

真正执行时，应把一个具体输入沿链路跑完并记录中间状态，而不是只完成目录/类定义。

## Verify

- False/0/空字符串语义明确。
- 重启稳定。

## Failure & Troubleshooting

|现象|优先检查|
|---|---|
|用户值被莫名回退 Default|检查 truthy 判断。|
|UI 显示与 runtime 不一致|检查是否绕过 EffectiveConfig。|

## Engineering Artifacts

本练习结束时至少留下：

- 对应 Contract / schema /边界说明；
- 最小实现或实验代码；
- 正向 + 关键失败路径测试；
- 一份真实可观察结果（trace / ContextResult / ViewModel / Session record / Diff 等）；
- 对“概念不变量”和“HMBuddy 当前实现选择”的区分。

## Generalize

完成后不要只记 HMBuddy 的文件名。应能迁移回答：换一个格式、Provider、UI、模型或业务场景时，**哪些层不变、哪些层应该替换、什么变化会迫使 Contract 升级**。

本概念 D → R → L → P 闭环完成。
