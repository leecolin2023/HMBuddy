# P — Practice：Session / SessionStore：持久工作上下文、Product Task 与 Resume

> SenseWright：**Practice V0.2 / Knowledge → Execution**

## Real Engineering Scenario

先实现只读 Session V0：Conversation + Artifact refs + Tool call log 可跨重启恢复。

## Engineering Model

- Session dataclass + append-only-ish events/records + atomic store/index。

## End-to-End Implementation

1. 定义最小 schema。
2. 实现 create/load/list/save。
3. 迁移 Conversation messages。
4. 加入 artifact refs。
5. 用 fake tool call 记录结果。
6. 重启 replay。

## One Concrete Path

```text
Workspace → Session → messages + tool_calls + artifact_refs + metadata → SessionStore → Session Index → Product Task/History/Resume
```

真正执行时，应把一个具体输入沿链路跑完并记录中间状态，而不是只完成目录/类定义。

## Verify

- 不依赖 UI objects。
- 不建立 DAG。
- 跨重启恢复。

## Failure & Troubleshooting

|现象|优先检查|
|---|---|
|把 RecentActivity 扩成 Session|语义与生命周期不同。|
|Session 中 pickle Provider/LLM|应保存 ID/config ref。|

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
