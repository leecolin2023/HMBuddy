# P — Practice：Adapter / Parsing Boundary：Native Structure、OCR 与 COM

> SenseWright：**Practice V0.2 / Knowledge → Execution**

## Real Engineering Scenario

实现一个新的解析 Provider，并证明替换 Parser 后上层零修改。

## Engineering Model

- Provider 管 availability/permission；Adapter 管解析；Artifact 管输出。

## End-to-End Implementation

1. 写 Adapter fixture。
2. 映射到 blocks/locator。
3. 用 Provider 包装并注册 capability。
4. 替换实现或 priority。
5. 跑 Context/Preview 回归。

## One Concrete Path

```text
Provider → Adapter → Native parser / OCR / COM → 结构恢复 → Artifact
```

真正执行时，应把一个具体输入沿链路跑完并记录中间状态，而不是只完成目录/类定义。

## Verify

- 上层无新格式分支。
- 失败归因能落到 parser/provider。

## Failure & Troubleshooting

|现象|优先检查|
|---|---|
|Context 需要 import 新 parser|边界泄漏。|
|Adapter 内自己选择备用 Provider|fallback 应回 Runtime。|

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
