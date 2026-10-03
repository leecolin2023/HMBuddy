# P — Practice：Tool / ToolRegistry：模型动作接口与 Capability 的桥

> SenseWright：**Practice V0.2 / Knowledge → Execution**

## Real Engineering Scenario

实现 ToolRegistry V0 + list_files/read_file 两个只读工具。

## Engineering Model

- registry + schemas + handlers + structured result。

## End-to-End Implementation

1. 定义 ToolSpec。
2. 实现 register/lookup/execute。
3. list_files 用 Workspace。
4. read_file 用 ArtifactReader。
5. 写 invalid args/unknown tool tests。

## One Concrete Path

```text
Model Tool Call → ToolRegistry schema/validation → Tool handler → Facade/Capability Runtime → ToolResult
```

真正执行时，应把一个具体输入沿链路跑完并记录中间状态，而不是只完成目录/类定义。

## Verify

- 模型无法传裸任意路径。
- Provider 替换不改 Tool。

## Failure & Troubleshooting

|现象|优先检查|
|---|---|
|Tool handler import Adapter|绕过 Capability。|
|工具数量随格式线性增长|抽象层错。|

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
