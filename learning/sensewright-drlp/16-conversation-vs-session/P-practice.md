# P — Practice：Conversation Surface vs Session Domain：UI 语言与 Kernel 原语

> SenseWright：**Practice V0.2 / Knowledge → Execution**

## Real Engineering Scenario

为 Stage B 写 Session Contract，但不实现 AgentLoop：先把 Conversation 持久化与恢复做到最小闭环。

## Engineering Model

- Session id/workspace/messages/artifact_refs/metadata + Store。

## End-to-End Implementation

1. 定义 schema。
2. 创建/load/save SessionStore。
3. 把 Controller transient transcript 改为 active Session。
4. 重启恢复消息。
5. 保持 Tool calls 为空也合法。
6. 不引入 Planner/TaskEngine。

## One Concrete Path

```text
Conversation UI transcript (process memory) → current artifact/workspace → LLM single-turn ask → [future] SessionStore/messages/tool_calls/artifact_refs
```

真正执行时，应把一个具体输入沿链路跑完并记录中间状态，而不是只完成目录/类定义。

## Verify

- 跨重启 Conversation 恢复。
- AppState 不复制 messages。

## Failure & Troubleshooting

|现象|优先检查|
|---|---|
|只把 UI list dump 到 state.json|状态归属仍错。|
|Session 一上来做 DAG|过度设计。|

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
