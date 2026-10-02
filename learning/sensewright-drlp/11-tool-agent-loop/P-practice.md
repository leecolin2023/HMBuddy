# P — Practice：Tool / Agent Loop：从问答到自主行动

> SenseWright：Practice V0.2  
> 目标：Knowledge Model → Executable Engineering Model

## Real Scenario

实现最多 5 步的只读 Agent Loop，只暴露 workspace.list 与 artifact.read.full，用 Mock Model 驱动确定性动作。

## Engineering Model

- AgentState：goal/step/observations/status。
- ToolRegistry：schema→handler。
- Handler 只调 Workspace/Facade。
- Guard：max_steps/cancel/repeat detection。

## End-to-End Implementation

1. 定义纯数据 ToolCall/ToolResult。
2. workspace.list 返回受控 handle，不给任意裸路径。
3. artifact.read.full 用 handle/Ref 调 Facade。
4. Mock Model 固定 list→read→final。
5. 实现 max_steps 与 invalid tool Observation。
6. 把 Runtime trace 与 Agent step 关联。
7. 加入重复动作检测。

## Concrete Path

```text
User goal → Agent State → LLM decide Action → Tool Contract → Stable Facade/Capability Runtime → Observation → 更新 State → 下一步/终止
```

本练习执行时需要额外记录真实输入、每一步输出/状态、最终 trace 或测试结果，而不是只保留架构图。

## Verify

- 模型无直接文件系统访问。
- 读取仍受 Workspace/Policy。
- 超过 max_steps 稳定终止。
- 每一步可解释/可重放。

## Failure & Troubleshooting

|现象|优先检查|
|---|---|
|模型重复同一工具|先加状态/重复检测/budget，不要先上 Planner。|
|模型传任意绝对路径|Tool Contract 应使用受控 handle。|

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
