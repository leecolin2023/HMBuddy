# P — Practice：Persistent Task / Recovery：任务中断、恢复与幂等

> SenseWright：Practice V0.2  
> 目标：Knowledge Model → Executable Engineering Model

## Real Scenario

实现只读 Persistent Task V0：10 文件读取任务可在任意步骤退出并从 checkpoint 继续。

## Engineering Model

- TaskRecord：goal/status/workspace/schema_version。
- StepRecord：input/status/result/attempts/error。
- TaskStore：原子 checkpoint。
- Runner：执行 pending step。
- Recovery：重建 Runtime 并验证依赖。

## End-to-End Implementation

1. 定义 task/step 状态机。
2. 只保存纯数据引用。
3. 创建 10 个 read steps。
4. 每步成功后原子 checkpoint。
5. 在第 3/7 步模拟退出并重启。
6. Resume 时从首个未完成 step 继续。
7. 中断期间修改一个源文件，验证进入 revalidation/failed。

## Concrete Path

```text
创建 TaskRecord → 执行 Step → 保存 ToolResult/checkpoint → 更新 status → 进程中断 → 重启 load → 验证依赖/revision → 从安全 checkpoint 继续
```

本练习执行时需要额外记录真实输入、每一步输出/状态、最终 trace 或测试结果，而不是只保留架构图。

## Verify

- 已完成步骤不无脑重跑。
- 重启不依赖旧进程对象。
- 源变化有明确状态。
- Recent Task 只链接该 Task，不充当执行状态。

## Failure & Troubleshooting

|现象|优先检查|
|---|---|
|恢复靠重新发送整个 Prompt|这是重做，不是 checkpoint recovery。|
|把 provider/client pickle 到磁盘|应保存配置/ID，重建运行对象。|
|写能力沿用只读重试|先解决 idempotency/revision/confirmation。|

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
