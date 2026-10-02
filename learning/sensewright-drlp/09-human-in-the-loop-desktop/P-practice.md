# P — Practice：Human-in-the-loop Desktop：薄应用层与人工控制点

> SenseWright：Practice V0.2  
> 目标：Knowledge Model → Executable Engineering Model

## Real Scenario

把 Desktop 演进成 Shell + Page + Presenter，保持 Runtime API 不变，并为 Phase 2.1 留出组合点。

## Engineering Model

- Shell 管窗口/导航。
- Page 管交互。
- Presenter 管纯展示。
- Application services 管配置/状态。
- Runtime 保持现有接口。

## End-to-End Implementation

1. 先固定 Phase 2 smoke。
2. 抽纯展示逻辑。
3. 拆 Workspace 页面但不改 read_artifact。
4. 抽后台任务 helper。
5. 把 Workspace scan 后台化。
6. 运行 presenter/service 单测 + GUI smoke。

## Concrete Path

```text
用户选 Workspace → 列 Ref → 用户选文件 → 后台 read_artifact → Presenter 展示 → 用户提问 → 后台 LLM.ask → 展示回答
```

本练习执行时需要额外记录真实输入、每一步输出/状态、最终 trace 或测试结果，而不是只保留架构图。

## Verify

- Desktop 不 import adapters。
- 无 GUI 可测核心展示/服务。
- scan/parse/LLM 不冻结主线程。

## Failure & Troubleshooting

|现象|优先检查|
|---|---|
|拆文件后循环依赖增多|说明只是搬文件，没有按依赖方向拆。|
|UI 直接读 parser object|回到 Artifact/Presenter。|

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
