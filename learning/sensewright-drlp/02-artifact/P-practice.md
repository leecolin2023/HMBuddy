# P — Practice：Artifact / ArtifactBlock：统一中间表示

> SenseWright：Practice V0.2  
> 目标：Knowledge Model → Executable Engineering Model

## Real Scenario

实现一个结构化 Markdown Reader：输出 heading/paragraph + locator，Context 层不得新增 .md 判断。

## Engineering Model

- Parser 识别 Markdown 结构。
- Adapter/Provider 映射成 ArtifactBlock。
- Locator 保留 line range。
- Context 继续只按 block_type 工作。

## End-to-End Implementation

1. 准备含两级标题与段落的 fixture。
2. 定义 line-based locator。
3. 映射 heading/paragraph。
4. 返回 Artifact 并填 provenance。
5. 通过外部 Provider 暴露 artifact.read.full。
6. 运行 Context 回归，确认无 Markdown 特例。

## Concrete Path

```text
Native Office/PDF → 格式 Parser / Adapter → ArtifactBlock + metadata + locator → Artifact + provenance → Context / Desktop / Future Search-Compare-Update
```

本练习执行时需要额外记录真实输入、每一步输出/状态、最终 trace 或测试结果，而不是只保留架构图。

## Verify

- 标题层级正确。
- 可寻址 block 有 locator。
- Context 不 import Markdown 代码。
- provenance 可追溯。

## Failure & Troubleshooting

|现象|优先检查|
|---|---|
|Context 中标题成普通文本|先修 Adapter block_type，不要让 Context 猜源语法。|
|新增格式后上层到处加 if suffix|说明 IR 边界被绕过。|

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
