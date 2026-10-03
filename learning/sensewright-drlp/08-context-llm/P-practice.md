# P — Practice：Context + LLM Interface：模型实际看到什么

> SenseWright：**Practice V0.2 / Knowledge → Execution**

## Real Engineering Scenario

写一个测试明确证明当前第二轮不继承第一轮，再设计 Session 化后的预期 Contract。

## Engineering Model

- Current: Artifact+question；Future: Session messages+artifact/tools/skills。

## End-to-End Implementation

1. 用 MockLLM 记录两次 user message。
2. 确认第二次不包含第一次对话。
3. 写未来 failing spec test（不并入实现）描述 Session Context。
4. 评估预算策略。

## One Concrete Path

```text
Artifact → ContextPolicy → Block serialization → Truncation/OCR warnings → System Prompt + Question → LLM
```

真正执行时，应把一个具体输入沿链路跑完并记录中间状态，而不是只完成目录/类定义。

## Verify

- 现状与未来语义不混淆。

## Failure & Troubleshooting

|现象|优先检查|
|---|---|
|UI 看起来多轮就以为模型有记忆|检查实际 prompt。|
|直接把整个 transcript 无预算拼接|会破坏 Context invariant。|

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
