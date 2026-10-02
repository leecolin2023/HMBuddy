# D — Deep Read：Persistent Task / Recovery：任务中断、恢复与幂等

> SenseWright：Deep Read V6.4 · Coverage-Preserving  
> HMBuddy 基线：`6eb16968c31b7fbbae377eadd6b670287d69b27a` · 状态：未来能力；Recent Task 目前只是导航入口

## 任务

只恢复 HMBuddy 自身结构，不评价、不外推。核心问题：

> **为什么“最近任务”不等于“可恢复任务”，真正恢复需要持久化什么？**

## Raw Source

- `requirements/phase-2.1-desktop-application-foundation-v0.1.md`
- `README.md`
- `plugin_runtime/runtime.py`

## 认知拓扑

```text
创建 TaskRecord
→ 执行 Step
→ 保存 ToolResult/checkpoint
→ 更新 status
→ 进程中断
→ 重启 load
→ 验证依赖/revision
→ 从安全 checkpoint 继续
```

## 独立认知单元

1. RecentTaskEntry 只保存导航元数据。
2. Runtime trace 记录执行观察，但不知道任务目标/步骤依赖。
3. Persistent Task 需要 durable execution state：goal、step、结果、pending action、error/retry。
4. 恢复不是重新发一遍 Prompt，而是知道哪些步骤已经被系统接受为完成。
5. 只读任务可安全重跑很多步骤；写操作会引入 crash window 与幂等问题。
6. 持久化纯数据和引用，不序列化 Thread/Provider/LLM client。

## 认知发动机

Persistent Task 解决的是控制流跨进程存活。Recent 回答“上次在哪”，Trace 回答“过去执行过什么”，Checkpoint 才回答“系统承认已经推进到哪一步”。

## 当前边界

- 首版从只读恢复开始。
- Task status 应是严格状态机。
- Resume 前要验证 Workspace/Artifact/plugin/model 依赖。
- 写操作前必须有 idempotency/revision/confirmation。

## 压缩后的模型

> **Recent = navigation；Trace = observation；Checkpoint = accepted durable progress。**

这句话不能替代前面的机制。Deep Read 的目标是能替代理解性重读，但精确行为仍应回 Raw Source 核验。

## Acceptance Gate

- [x] 覆盖与本概念有关的当前实现/规格。
- [x] 没把未来能力写成现状。
- [x] 保留关键责任转移与边界。
- [x] 没用外部框架改写 HMBuddy 自己的设计。

下一步：[R-review.md](./R-review.md)
