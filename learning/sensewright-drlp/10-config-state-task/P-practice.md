# P — Practice：Config vs State vs Task：应用状态与任务状态

> SenseWright：Practice V0.2  
> 目标：Knowledge Model → Executable Engineering Model

## Real Scenario

严格按 Phase 2.1 实现最小 Application State Layer，不进入 Agent Runtime。

## Engineering Model

- ConfigService：schema/precedence/source/atomic save。
- AppStateService：recent/last session/recovery。
- RecentService：pin/limit/resume。
- PluginManagementService：把配置意图编译成 Runtime。

## End-to-End Implementation

1. 实现 App Data Path。
2. 实现 AppConfig/ConfigSnapshot 与 precedence 测试。
3. 实现 atomic save/invalid recovery。
4. 实现独立 AppState。
5. 实现 Recent Workspace/Task（只存元数据）。
6. 实现 PluginManagementService 与 Runtime 重建。
7. 最后接 Home/Settings/Plugins UI。

## Concrete Path

```text
启动 → 加载 Config + 来源优先级 → 加载 AppState → 装配 Runtime/LLM → Home Recent → 运行中分别更新 Config/State
```

本练习执行时需要额外记录真实输入、每一步输出/状态、最终 trace 或测试结果，而不是只保留架构图。

## Verify

- config/state 分离且有 schema_version。
- env override 可解释。
- secret 不落盘。
- Recent Task 不含 execution object。

## Failure & Troubleshooting

|现象|优先检查|
|---|---|
|Settings 保存成功但运行值没变|检查 effective source 是否被 env/runtime 覆盖。|
|禁用插件后 Workspace 仍显示格式|检查 Runtime/Catalog 是否同步重建。|

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
