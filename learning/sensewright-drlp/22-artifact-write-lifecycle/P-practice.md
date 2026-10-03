# P — Practice：Artifact Write Lifecycle：Version、Patch、Validate、Diff

> SenseWright：**Practice V0.2 / Knowledge → Execution**

## Real Engineering Scenario

实现 DOCX 单一 replace-paragraph Patch V0，完整走 version/conflict/validate/diff。

## Engineering Model

- hash/mtime version + locator replace + atomic output + diff。

## End-to-End Implementation

1. 定义 ArtifactVersion。
2. 定义 replace op。
3. 读取并保存 base revision。
4. 实现 DOCX patch provider。
5. 外部修改时拒绝。
6. 生成新 Artifact。
7. 验证文本/结构。
8. 生成最小 Diff。

## One Concrete Path

```text
Artifact base version → ArtifactPatch operations(locator) → Capability Provider → New Artifact Version → Validate → ArtifactDiff → User/Agent continue
```

真正执行时，应把一个具体输入沿链路跑完并记录中间状态，而不是只完成目录/类定义。

## Verify

- 冲突不覆盖。
- 修改位置准确。
- 原文件/新版本可追踪。

## Failure & Troubleshooting

|现象|优先检查|
|---|---|
|只传 instruction 给 writer|不可验证。|
|直接覆盖原文件后再比较|缺安全版本边界。|

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
