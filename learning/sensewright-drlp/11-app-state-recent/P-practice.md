# P — Practice：AppState / Recent Workspace / Recent Activity：轻量恢复而非 Task 域

> SenseWright：**Practice V0.2 / Knowledge → Execution**

## Real Engineering Scenario

写一个 migration 练习：未来 Session 上线后，让 Recent Activity 只保留非 Agent 导航项，Agent history 改读 Session Index。

## Engineering Model

- Product history 与 Kernel session 分源。

## End-to-End Implementation

1. 定义哪些 activity 属 Agent。
2. 引入 Session ref 而非复制 messages。
3. 写兼容读取旧 state。
4. 验证旧 RecentWorkspace 保留。

## One Concrete Path

```text
User activity → AppState metadata → RecentWorkspace / RecentActivity → stable entry_id/workspace_id → UI resume_view → re-enter Product surface
```

真正执行时，应把一个具体输入沿链路跑完并记录中间状态，而不是只完成目录/类定义。

## Verify

- 没有双写完整对话。
- Recent Activity 仍可重建。

## Failure & Troubleshooting

|现象|优先检查|
|---|---|
|给 RecentActivity 增加 step/tool_calls|正在把它演化成半套 TaskEngine。|
|为了恢复 UI 存正文|只存引用。|

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
