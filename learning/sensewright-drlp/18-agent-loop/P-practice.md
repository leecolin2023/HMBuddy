# P — Practice：AgentLoop：最小自主决策闭环

> SenseWright：**Practice V0.2 / Knowledge → Execution**

## Real Engineering Scenario

实现 read-only 5-step loop，用 Mock Model 固定 list→read→final。

## Engineering Model

- Session + ModelAdapter + ToolRegistry + Loop guards。

## End-to-End Implementation

1. 定义 ModelResponse/ToolCall。
2. 实现 max_steps。
3. 执行 ToolResult append。
4. 将 errors 转 Observation。
5. 记录 stop reason。

## One Concrete Path

```text
Session Context → Model → Tool Call? → ToolRegistry.execute → Observation → append Session → Model again → finish
```

真正执行时，应把一个具体输入沿链路跑完并记录中间状态，而不是只完成目录/类定义。

## Verify

- deterministic trace。
- 超步数稳定停止。
- 所有 file access 经 Tool→Capability Runtime。

## Failure & Troubleshooting

|现象|优先检查|
|---|---|
|模型死循环|先加 guard/trace，不上 Planner。|
|Loop 自己读取文件|职责越界。|

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
