# P — Practice：Eval / Feedback Loop：如何证明系统真的工作

> SenseWright：Practice V0.2  
> 目标：Knowledge Model → Executable Engineering Model

## Real Scenario

新增一个“Parser 正确、Context 因截断丢事实”的回归案例。

## Engineering Model

- Fixture 固定源结构。
- Parser assertion 证明 IR 完整。
- Context assertion 证明预算行为。
- Mock QA 证明模型实际收到什么。

## End-to-End Implementation

1. 构造关键事实位于后半部的 fixture。
2. 写 Artifact 断言。
3. 设置确定性 ContextPolicy 触发截断。
4. 断言 truncated/omitted/reason。
5. Mock Client 检查实际 prompt。
6. 未来 targeted selection 修复时保留此 regression。

## Concrete Path

```text
规格/真实失败 → fixture/case → Parser/Workspace/Context/Runtime 单层 Eval → 集成 Eval → baseline → CI + wheel smoke → 新失败回流
```

本练习执行时需要额外记录真实输入、每一步输出/状态、最终 trace 或测试结果，而不是只保留架构图。

## Verify

- 失败能直接定位到 Context。
- 同一 case 可用于修复前后对照。
- CI/wheel smoke 可运行。

## Failure & Troubleshooting

|现象|优先检查|
|---|---|
|测试偶发|去掉网络/时间/随机性，先固定 Contract。|
|端到端失败但单层都过|缺 integration contract，应新增跨层 case。|

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
