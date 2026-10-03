# P — Practice：Stable Facade + Capability：应用意图与 Runtime 能力

> SenseWright：**Practice V0.2 / Knowledge → Execution**

## Real Engineering Scenario

设计 read_file Tool 到多个 read capability 的映射，但暂不暴露 Provider。

## Engineering Model

- Tool schema → Facade/capability routing → Runtime。

## End-to-End Implementation

1. 定义 Tool 参数 mode/range。
2. 映射到 capability，不传 parser 名。
3. 用 Mock Provider 验证选择。
4. 错误转成 ToolResult。

## One Concrete Path

```text
Application/Tool → Stable Facade → CapabilityRequest → Registry/Router → Provider → CapabilityResult
```

真正执行时，应把一个具体输入沿链路跑完并记录中间状态，而不是只完成目录/类定义。

## Verify

- 模型看不到 Provider。
- Tool 数量没有因格式增加。

## Failure & Troubleshooting

|现象|优先检查|
|---|---|
|Tool 名变成 read_docx/read_pdf|把格式差异错误暴露给 Agent。|
|Tool handler 直接 new Adapter|绕过 Runtime。|

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
