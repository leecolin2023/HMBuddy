# P — Practice：Plugin Manager / System Status：把 Runtime 事实翻译成产品可解释性

> SenseWright：**Practice V0.2 / Knowledge → Execution**

## Real Engineering Scenario

构造一个多 Provider 插件的 Product View 测试，覆盖 enabled/unavailable/load-failed。

## Engineering Model

- Runtime reports → deterministic view model → UI。

## End-to-End Implementation

1. 造 provider 状态。
2. build_plugin_views。
3. 断言一插件一行。
4. 展示原因/权限。
5. 切 disable 并重建 runtime。

## One Concrete Path

```text
Discovery/LoadReport/Registry/Policy → PluginView + ProviderView → Plugin Manager → SystemStatus → User action enable/disable/rescan
```

真正执行时，应把一个具体输入沿链路跑完并记录中间状态，而不是只完成目录/类定义。

## Verify

- UI 状态可由 Runtime 证据重建。

## Failure & Troubleshooting

|现象|优先检查|
|---|---|
|UI 状态靠本地 bool 缓存|会漂移。|
|插件重复多行|应按 plugin identity 聚合。|

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
