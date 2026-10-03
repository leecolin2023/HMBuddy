# P — Practice：Artifact Preview：可读取、可表示、可预览是三件不同的事

> SenseWright：**Practice V0.2 / Knowledge → Execution**

## Real Engineering Scenario

为一种新 Preview 格式实现 renderer，但保持 Artifact Runtime 入口不变。

## Engineering Model

- Artifact → PreviewModel → Renderer。

## End-to-End Implementation

1. 定义 supported 条件。
2. 只消费 Artifact fields。
3. 实现 renderer。
4. 加 AST guard/Qt smoke。

## One Concrete Path

```text
ArtifactRef → ArtifactReader → Artifact → PreviewModel → Markdown/TXT/Unsupported renderer
```

真正执行时，应把一个具体输入沿链路跑完并记录中间状态，而不是只完成目录/类定义。

## Verify

- 无直接文件 I/O。
- 不改变 parser/provider。

## Failure & Troubleshooting

|现象|优先检查|
|---|---|
|为了预览重新读原文件|双事实源。|
|把 UI renderer 塞进 plugin_runtime|职责错位。|

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
