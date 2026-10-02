# P — Practice：Policy / Permission / Trust Boundary：运行时安全边界

> SenseWright：Practice V0.2  
> 目标：Knowledge Model → Executable Engineering Model

## Real Scenario

用 Fake Provider 验证 office.com 的拒绝与授权路径，证明拒绝发生在副作用前。

## Engineering Model

- Provider 声明 required_permissions。
- Runtime pre-check。
- Policy 决定 grant。
- Trace 记录结果。

## End-to-End Implementation

1. Fake Provider execute 内设置 side_effect_called=True。
2. 默认 Policy 下执行，断言 PermissionError 且 flag=False。
3. 检查失败 trace。
4. 显式 grant office.com 后再执行，断言成功。
5. 动态申请一个未声明权限，断言拒绝。
6. 加入 fallback 候选，确认权限错误不 fallback。

## Concrete Path

```text
输入/Ref → Workspace boundary → Manifest permissions → Runtime required_permissions gate → effective permissions → dynamic gate → Provider → trace/context boundary
```

本练习执行时需要额外记录真实输入、每一步输出/状态、最终 trace 或测试结果，而不是只保留架构图。

## Verify

- 拒绝在副作用前。
- 声明与授权缺一不可。
- 安全错误无 fallback。

## Failure & Troubleshooting

|现象|优先检查|
|---|---|
|报 PermissionError 但副作用已发生|gate 放晚了。|
|grant 后仍失败|检查 Manifest/Provider 是否声明。|

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
