# P — Practice：Runtime Governance：Policy、Availability、Fallback、Trace

> SenseWright：**Practice V0.2 / Knowledge → Execution**

## Real Engineering Scenario

构造 Fake Provider 验证权限、availability、fallback 三种不同失败语义。

## Engineering Model

- 选择失败、治理失败、解析失败必须可区分。

## End-to-End Implementation

1. 建三个 Provider。
2. 分别模拟 unavailable、permission denied、parse error。
3. 执行请求。
4. 检查是否 fallback 与 trace。

## One Concrete Path

```text
Request → supports → availability → permission pre-check → execute → allowlisted fallback → trace/result
```

真正执行时，应把一个具体输入沿链路跑完并记录中间状态，而不是只完成目录/类定义。

## Verify

- 只有 allowlist 错误 fallback。
- 副作用前拒绝。

## Failure & Troubleshooting

|现象|优先检查|
|---|---|
|所有错误都 fallback|治理语义被破坏。|
|trace 无法说明为什么没选某 Provider|检查 selection diagnostics。|

## Engineering Artifacts

本练习结束时至少留下：

- 对应 Contract / schema /边界说明；
- 最小实现或实验代码；
- 正向 + 关键失败路径测试；
- 一份真实可观察结果（trace / ContextResult / ViewModel / Session record / Diff 等）；
- 对“概念不变量”和“HMBuddy 当前实现选择”的区分。

## Generalize

完成后不要只记 HMBuddy 的文件名。应能迁移回答：换一个格式、Provider、UI、模型或业务场景时，**哪些层不变、哪些层应该替换、什么变化会迫使 Contract 升级**。

本概念 D → R → L → P 闭环完成。
