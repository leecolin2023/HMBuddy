# L — Learning：Persistent Task / Recovery：任务中断、恢复与幂等

> SenseWright：System Learning V0.5.3  
> 路径：Ground → Run Once → Explain → Vary One Condition → Model → Use

## Ground Object

比较 20 份材料的任务已完成前 7 份读取，应用崩溃。

## Run Once

1. 只有 Recent 时只能回到 Workspace。
2. 只有 Trace 能看到读过哪些文件，却不知道哪些结果已纳入 accepted state。
3. TaskRecord 应保存 goal、completed steps、pending step、status。
4. 重启后先验证 Workspace/源文件 revision。
5. 从第一个未完成的安全步骤继续。

## 为什么每一步存在

- 恢复需要 durable control state。
- Checkpoint 是系统承认进度的提交点。
- side effect 与 checkpoint 之间存在 crash window。

## Boundary Variation

只改变一个条件：

> **未来写文件任务在“文件已经写成功、checkpoint 还没写”时崩溃。**

观察：

- 只读任务的安全重跑不再成立。
- 直接重试可能重复修改。
- 必须引入 operation_id/idempotency 与 revision 检查。
- 这把任务恢复提升为执行一致性问题。

## Knowledge Model

- Recent = navigation；Trace = observation；Checkpoint = accepted durable progress。
- Persistent Task = versioned state machine + durable step records + dependency validation。
- 真正可恢复 Agent 的核心不是保存聊天记录。

## Gap

- Task/Step schema。
- Task Store/事务。
- Artifact revision/idempotency。
- 用户确认等待态。

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
