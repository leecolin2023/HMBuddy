# L — Learning：Eval / Feedback Loop：如何证明系统真的工作

> SenseWright：System Learning V0.5.3  
> 路径：Ground → Run Once → Explain → Vary One Condition → Model → Use

## Ground Object

关键事实在 Artifact 第 600 block，但 Context 在第 300 block 截断，最终 QA 没答出。

## Run Once

1. Parser Eval 通过。
2. Context Eval 显示事实未进入且 truncated。
3. 最终 QA 失败不能归咎模型。
4. 把该 failure 固定成 regression case。
5. 以后 Context 策略变化都复用同一 case。

## 为什么每一步存在

- 只看最终回答无法知道优化哪层。
- 分层 Eval 把“模型不聪明”变成可定位工程问题。
- 真实 failure 应最终变成最小回归。

## Boundary Variation

只改变一个条件：

> **只把 ContextPolicy 调小，Parser 输出不变。**

观察：

- Parser 测试仍绿。
- Context/QA 行为改变。
- 说明不同层必须有独立 acceptance gate。

## Knowledge Model

- Eval = Contract × Representative Inputs × Observable Assertions。
- 先分层定位，再端到端验收。
- Agent 阶段要把 action trace/state/evidence 纳入 Eval。

## Gap

- 真实 golden corpus。
- 任务级指标。
- 用户失败→regression 的固定流程。

## 迁移到别的项目时怎么问

- 这个概念在系统里拥有哪一段控制权？
- 它的输入输出是否是稳定 Contract，还是某个实现对象？
- 改变刚才这个条件后，哪些结论仍成立、哪些立即失效？
- 失败时能否定位到本层，而不是统一归因给“模型不行”？

## Acceptance Gate

- [x] 概念已映射到真实 HMBuddy 对象。
- [x] 至少一条具体链路完整跑过。
- [x] 解释了关键步骤为何存在。
- [x] 只变化一个高信息量条件。
- [x] 明确当前模型的适用边界。

下一步：[P-practice.md](./P-practice.md)
