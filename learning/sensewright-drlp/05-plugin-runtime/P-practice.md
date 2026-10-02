# P — Practice：Plugin Runtime：发现、装载、注册、路由与执行

> SenseWright：Practice V0.2  
> 目标：Knowledge Model → Executable Engineering Model

## Real Scenario

实现 package 形式外部 Markdown Reader，用相对 import，并验证 priority、fallback、trace。

## Engineering Model

- plugin.json 为声明权威。
- package entrypoint 组装 Provider。
- parser.py 做解析。
- Runtime 管选择/治理。

## End-to-End Implementation

1. 创建标准 package 与 plugin.json。
2. 声明 .md、artifact.read.full、priority、filesystem.read。
3. assemble_runtime 装配。
4. 断言 Discovery/LoadReport/Registry。
5. 读取并检查 provenance/trace。
6. 模拟 ArtifactParseError 验证 fallback，再模拟权限错误验证不 fallback。

## Concrete Path

```text
Plugin dir → Manifest 校验 → Discovery → Loader → Provider 实例 → Registry → Router → Runtime execute/fallback/trace → Result
```

本练习执行时需要额外记录真实输入、每一步输出/状态、最终 trace 或测试结果，而不是只保留架构图。

## Verify

- Core 零修改。
- 外部 Provider 首选。
- fallback_from 可观察。
- 权限错误不绕过。

## Failure & Troubleshooting

|现象|优先检查|
|---|---|
|插件被发现但未注册|看 LoadReport/Manifest/entrypoint。|
|高 priority 未选中|检查 supports/availability 与 Manifest 注入后的真实字段。|

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
