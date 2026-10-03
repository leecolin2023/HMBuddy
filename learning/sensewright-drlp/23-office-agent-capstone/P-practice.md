# P — Practice：End-to-End Office Agent：从工作区到持续可修改成果

> SenseWright：**Practice V0.2 / Knowledge → Execution**

## Real Engineering Scenario

把这个 Capstone 作为下一阶段验收主线，先 Markdown-only 跑通，再升级 DOCX。

## Engineering Model

- 一条真实用户目标贯穿所有层，每新增抽象都必须在该链路中找到位置。

## End-to-End Implementation

1. 先定义 Session/Tool/Loop 最小 Contract。
2. 实现 list/search/read。
3. 用 Markdown create/edit 做第一版。
4. Conversation 接 Session。
5. 加入 restart/resume。
6. 加入 Approval/Audit。
7. 最后替换/扩展为 DOCX Patch。

## One Concrete Path

```text
User Goal → Workspace → Session → AgentLoop → Search/Read Tools → Skills → Artifact Create → Validate → User Feedback → ArtifactPatch → New Version + Diff → Complete/Resume
```

真正执行时，应把一个具体输入沿链路跑完并记录中间状态，而不是只完成目录/类定义。

## Verify

- 用户不需要手工选每个文件。
- 任务可跨轮/跨重启继续。
- 所有文件动作经 Workspace/Policy。
- 修改可 diff/validate。
- Kernel 无 Planner/Multi-Agent 依赖。

## Failure & Troubleshooting

|现象|优先检查|
|---|---|
|实现很多 Engine 但场景仍跑不通|回到 Capstone 链路删减/补缺。|
|先做 Multi-Agent|单 Agent 闭环尚未证明。|

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
