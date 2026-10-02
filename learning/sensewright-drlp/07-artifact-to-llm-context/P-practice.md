# P — Practice：Artifact → LLM Context：模型上下文编译层

> SenseWright：Practice V0.2  
> 目标：Knowledge Model → Executable Engineering Model

## Real Scenario

构造“答案在尾部”的长 Artifact，做 Parser/Context/QA 分层回归，并实验 targeted block selection。

## Engineering Model

- 完整 Artifact 为 ground truth。
- ContextBuildResult 为模型证据。
- MockLLMClient 记录实际 prompt。

## End-to-End Implementation

1. 生成 600+ blocks，关键事实只放末尾。
2. 断言 Artifact 中事实存在。
3. 用小预算构造 Context，断言事实不在且 truncated。
4. Mock ask，确认 marker 进入 prompt。
5. 按已知 locator 选择尾部 blocks 重新 build_context。
6. 比较 prefix 与 targeted context。

## Concrete Path

```text
Artifact → 按 block_type 序列化 → 应用 chars/blocks/table rows 预算 → 插入截断/OCR/缺失标记 → ContextBuildResult → LLM
```

本练习执行时需要额外记录真实输入、每一步输出/状态、最终 trace 或测试结果，而不是只保留架构图。

## Verify

- 能区分 Parser Error 与 Context Selection Error。
- 绝对路径不进 prompt。
- targeted selection 不需要改 Adapter。

## Failure & Troubleshooting

|现象|优先检查|
|---|---|
|模型答错就换模型|先看 last_context_result。|
|Artifact 有事实但 Context 没有|这是 selection/预算问题。|

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
