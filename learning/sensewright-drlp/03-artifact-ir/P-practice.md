# P — Practice：Artifact：Office 领域中间表示与稳定定位

> SenseWright：**Practice V0.2 / Knowledge → Execution**

## Real Engineering Scenario

为一个结构化 Markdown/TXT 解析结果增加稳定 locator，并让 Context 与 Preview 都只消费 Artifact。

## Engineering Model

- Source → Adapter → Artifact → two representations。

## End-to-End Implementation

1. 构造标题/段落 fixture。
2. 生成 line-range locator。
3. 确保 blocks 与 content 一致。
4. Context 从 blocks 渲染。
5. Preview 从 Artifact.content 渲染。
6. 增加静态测试禁止 Preview 直接 open 文件。

## One Concrete Path

```text
Native File → Adapter → ArtifactBlock + Locator → Artifact + Provenance → Context / Preview / Future Search-Write
```

真正执行时，应把一个具体输入沿链路跑完并记录中间状态，而不是只完成目录/类定义。

## Verify

- 两个消费方都不 import parser。
- locator 可回指源位置。
- provenance 完整。

## Failure & Troubleshooting

|现象|优先检查|
|---|---|
|UI 直接 Path.read_text|破坏 IR 单一事实源。|
|写回准备使用 block_id|block_id 不是跨版本定位契约。|

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
