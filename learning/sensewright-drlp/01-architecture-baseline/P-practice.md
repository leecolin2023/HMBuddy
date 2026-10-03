# P — Practice：架构总纲：WorkBuddy-like Product on a Pi-like Minimal Harness

> SenseWright：**Practice V0.2 / Knowledge → Execution**

## Real Engineering Scenario

为一个新产品功能做 Architecture Alignment：证明它如何由现有原语组合完成，或给出新增 Core 的充分证据。

## Engineering Model

- 先写 Product Capability。
- 再列 Kernel Primitives Used。
- 再判断属于 Tool/Skill/Extension/Capability Plugin。
- 最后列 New Core Primitive=No/Yes 与依据。

## End-to-End Implementation

1. 选一个真实需求，例如“审批前自动检查并让用户确认”。
2. 写 Architecture Alignment 小节。
3. 优先映射为 validate Tool + before_tool Approval Hook。
4. 画出调用链和状态归属。
5. 列出失败模式：用户离线、确认超时、工具失败。
6. 只有无法用现有原语解决时才提交 ADR。

## One Concrete Path

```text
WorkBuddy-like Product Capability → 映射到少量 Kernel Primitives → 通过 Tool / Skill / Extension / Capability Plugin 组合 → Office 文件落到 Artifact-native Runtime → Policy / Events / Context 作为 Kernel Invariants
```

真正执行时，应把一个具体输入沿链路跑完并记录中间状态，而不是只完成目录/类定义。

## Verify

- 需求实现不要求新增 Engine。
- AgentLoop 不因产品菜单变化而修改。
- Workspace/Policy/Artifact Contract 没被绕过。
- 若新增 Core，ADR 能明确证明现有原语不足。

## Failure & Troubleshooting

|现象|优先检查|
|---|---|
|每个新功能都新建 Manager/Engine|先回到产品→原语映射表。|
|为了保持极简拒绝必要状态|极简不是少代码竞赛；真实一致性需求优先。|

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
