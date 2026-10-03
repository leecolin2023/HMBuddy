# P — Practice：Skill：Markdown-first 工作方法与 Progressive Disclosure

> SenseWright：**Practice V0.2 / Knowledge → Execution**

## Real Engineering Scenario

把 SenseWright DeepRead 作为第一个 HMBuddy Skill 接入最小 Skill Loader。

## Engineering Model

- metadata index → lazy SKILL.md load → tool requirements → context injection。

## End-to-End Implementation

1. 定义极小 metadata。
2. 索引 DeepRead。
3. 按触发条件加载。
4. 把内容注入 Session/Context。
5. 记录 selected skill。
6. 不实现 DAG。

## One Concrete Path

```text
Skill metadata name/description → 按需选择 → 加载 SKILL.md → 按需加载 references/templates/scripts → Agent 使用 Tools 执行 → Validation
```

真正执行时，应把一个具体输入沿链路跑完并记录中间状态，而不是只完成目录/类定义。

## Verify

- 未选 Skill 不占全文 Context。
- Skill 不绕过 Tool。

## Failure & Troubleshooting

|现象|优先检查|
|---|---|
|把 SKILL.md 翻译成固定 Python 节点|过早工作流化。|
|所有 Skill 一次塞 prompt|破坏 progressive disclosure。|

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
