# P — Practice：Adapter / Parsing Boundary：格式解析隔离层

> SenseWright：Practice V0.2  
> 目标：Knowledge Model → Executable Engineering Model

## Real Scenario

新增一个外部 Markdown 能力，但明确拆分 Provider 与 Adapter，两层分别测试。

## Engineering Model

- Provider 管声明/环境/权限。
- Adapter 只做 Markdown → Artifact。
- Runtime 管选择/fallback。
- Context 只消费 Artifact。

## End-to-End Implementation

1. 先写 Adapter 单测。
2. 再写 Provider 包装 Adapter。
3. Manifest 声明 capability 与权限。
4. 写 priority/provenance 集成测试。
5. 模拟解析失败，验证 Runtime fallback。
6. 模拟权限失败，验证不进入 Adapter。

## Concrete Path

```text
CapabilityRequest → Provider → Adapter → 第三方 Parser/OCR/COM → 结构恢复 → Artifact
```

本练习执行时需要额外记录真实输入、每一步输出/状态、最终 trace 或测试结果，而不是只保留架构图。

## Verify

- Adapter 测试无需装配 Runtime。
- Runtime 测试无需知道 Markdown 解析细节。
- Context 无格式 import。

## Failure & Troubleshooting

|现象|优先检查|
|---|---|
|Adapter 单测必须启动整个 Runtime|说明解析与运行时耦合过深。|
|Provider 内复制 parser 逻辑|说明 Adapter 边界失效。|

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
