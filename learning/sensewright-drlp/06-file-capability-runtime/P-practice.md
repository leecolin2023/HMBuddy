# P — Practice：File Capability Runtime：Manifest、Plugin、Provider、Registry、Router

> SenseWright：**Practice V0.2 / Knowledge → Execution**

## Real Engineering Scenario

实现一个外部 .foo Provider，并验证 Discovery→Load→Registry→Route→Workspace 全链。

## Engineering Model

- Manifest 是声明权威；Runtime 是执行控制点。

## End-to-End Implementation

1. 写 plugin.json。
2. 写 package Provider。
3. 装配 runtime。
4. 检查 reports/registry。
5. 读取 .foo。
6. 制造 parse error 验证 fallback。

## One Concrete Path

```text
plugin.json → Discovery → Manifest validation → Loader → Provider instances → Registry → Router → Runtime execute
```

真正执行时，应把一个具体输入沿链路跑完并记录中间状态，而不是只完成目录/类定义。

## Verify

- Core 零修改。
- trace/provenance 完整。

## Failure & Troubleshooting

|现象|优先检查|
|---|---|
|发现但未加载|查 Manifest/entrypoint。|
|Workspace 不显示|查 Catalog 是否来自该 Registry。|

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
