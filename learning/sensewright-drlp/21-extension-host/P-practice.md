# P — Practice：ExtensionHost / Hooks / Events：高级 Agent 能力的统一扩展面

> SenseWright：**Practice V0.2 / Knowledge → Execution**

## Real Engineering Scenario

实现 ExtensionHost V0，只支持 before_tool/after_tool，并做 Approval+Audit 两个内置 Extension。

## Engineering Model

- ordered hooks + typed decision/result + isolation。

## End-to-End Implementation

1. 定义 hook payload。
2. 实现 register/emit。
3. 实现 Policy decision adapter。
4. 实现 ask mock。
5. 实现 audit recorder。
6. 测试 deny short-circuit 与 exception isolation。

## One Concrete Path

```text
AgentLoop events → ExtensionHost → register_tool/register_hook/register_skill → before/after model/tool/session hooks → Approval/Memory/MCP/Audit/...
```

真正执行时，应把一个具体输入沿链路跑完并记录中间状态，而不是只完成目录/类定义。

## Verify

- AgentLoop 核心无业务分支。
- Hook 顺序确定。

## Failure & Troubleshooting

|现象|优先检查|
|---|---|
|每个能力都修改 while loop|缺 Extension boundary。|
|Hook 可以直接任意改 Session 内部|Contract 过宽。|

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
