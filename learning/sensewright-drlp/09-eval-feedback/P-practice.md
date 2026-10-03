# P — Practice：Eval / Feedback Loop：从失败模式到可回归证据

> SenseWright：**Practice V0.2 / Knowledge → Execution**

## Real Engineering Scenario

为一个新的架构 invariant 写 static guard + integration test + baseline entry。

## Engineering Model

- Invariant → observable violation → deterministic test。

## End-to-End Implementation

1. 选一条边界，例如 Desktop 不可 import adapters。
2. 写 AST/import guard。
3. 写一条正常 Product→Controller→Facade 集成路径。
4. 加入 baseline AC。
5. 在 CI 跑跨平台。

## One Concrete Path

```text
真实问题/规格 → Atomic acceptance → unit/integration/static guard → baseline → CI source+wheel → 新失败回流
```

真正执行时，应把一个具体输入沿链路跑完并记录中间状态，而不是只完成目录/类定义。

## Verify

- 故意破坏边界时测试必须红。
- 恢复合法链路后绿。

## Failure & Troubleshooting

|现象|优先检查|
|---|---|
|只测 happy path|无法保护架构。|
|测试依赖真实网络|先用协议 fake/Mock 固定控制面。|

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
