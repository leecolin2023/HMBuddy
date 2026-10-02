# P — Practice：Stable Facade + Capability：稳定入口与能力语义

> SenseWright：Practice V0.2  
> 目标：Knowledge Model → Executable Engineering Model

## Real Scenario

设计一个最小 artifact.read.outline，从 Contract 到 Provider 到 Facade 全链扩展，不改变 full-read。

## Engineering Model

- 先定义 outline Result。
- Provider 实现格式差异。
- Runtime 继续复用 Registry/Router。
- Facade 只提供语法糖。

## End-to-End Implementation

1. 先写 capability contract 与失败测试。
2. 实现至少一个 Outline Provider。
3. 注册并验证 capability 可见。
4. 新增 read_outline()，不在 facade 判断格式。
5. 加入第二 Provider 验证 priority。
6. 运行 full-read 全部回归。

## Concrete Path

```text
Application 调 read_artifact → Facade 通用校验 → CapabilityRequest(artifact.read.full) → Registry/Router 选择 Provider → Runtime → CapabilityResult → Artifact
```

本练习执行时需要额外记录真实输入、每一步输出/状态、最终 trace 或测试结果，而不是只保留架构图。

## Verify

- Capability 名不绑定格式。
- Facade 不 import Provider。
- 未知能力走统一错误。
- full-read baseline 不回退。

## Failure & Troubleshooting

|现象|优先检查|
|---|---|
|Facade 出现 if .docx|Provider selection 泄漏。|
|outline 同时由 mode 和 capability 控制|出现双事实源。|

## Operationalize

完成后至少保留：

- 实现或最小实验代码；
- 对应 Contract / schema；
- 正向与失败路径测试；
- 一份可观察结果（trace / provenance / checkpoint / ContextResult 等，视概念而定）；
- 对“当前实现选择”与“概念不变量”的区分说明。

## 完成标准

你应能同时回答：

1. HMBuddy 当前怎么做；
2. 为什么这样分层；
3. 一个关键条件变化后哪里失效；
4. 自己实现时从哪开始、怎样验证、怎样排错。

本概念 D → R → L → P 闭环完成。
