# P — Practice：Conversation-first Desktop Shell：Product Layer 与 Human-in-the-loop

> SenseWright：**Practice V0.2 / Knowledge → Execution**

## Real Engineering Scenario

在不修改 Runtime 的前提下，为 Conversation 增加一个 Tool Activity 占位展示模型（仅 UI mock），验证产品层可扩展性。

## Engineering Model

- Event/ViewModel → Conversation item；不建假 AgentLoop。

## End-to-End Implementation

1. 定义纯展示 ToolActivityItem。
2. 用 fake event 渲染。
3. 不写入 Session/State。
4. 保持 Runtime 零修改。
5. 写 Qt smoke。

## One Concrete Path

```text
Sidebar work navigation → Conversation current work → on-demand Preview → Controller/Application → unchanged Runtime/Domain
```

真正执行时，应把一个具体输入沿链路跑完并记录中间状态，而不是只完成目录/类定义。

## Verify

- Product 能预演未来 UX，但没有伪造 Kernel 能力。

## Failure & Troubleshooting

|现象|优先检查|
|---|---|
|为了 UI 演示直接建半套 Session|违反阶段边界。|
|Shell 开始读取文件正文|绕过 Controller/Artifact Runtime。|

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
