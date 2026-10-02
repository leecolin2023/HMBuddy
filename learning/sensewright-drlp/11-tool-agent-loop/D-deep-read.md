# D — Deep Read：Tool / Agent Loop：从问答到自主行动

> SenseWright：Deep Read V6.4 · Coverage-Preserving  
> HMBuddy 基线：`6eb16968c31b7fbbae377eadd6b670287d69b27a` · 状态：未来能力；当前明确不实现

## 任务

只恢复 HMBuddy 自身结构，不评价、不外推。核心问题：

> **HMBuddy 在什么条件下才真正从文档问答进入 Agent？**

## Raw Source

- `README.md`
- `llm/client.py`
- `services/artifact_reader.py`
- `plugin_runtime/contracts.py`
- `plugin_runtime/runtime.py`
- `requirements/phase-2.1-desktop-application-foundation-v0.1.md`

## 认知拓扑

```text
User goal
→ Agent State
→ LLM decide Action
→ Tool Contract
→ Stable Facade/Capability Runtime
→ Observation
→ 更新 State
→ 下一步/终止
```

## 独立认知单元

1. 当前 LLM 是 Artifact→Context→Answer 的单向流程，没有 tool call。
2. 当前文件选择由人完成，相当于人承担 planner/tool selection。
3. Workspace/Capability/Policy/Artifact/Trace 已经提供 Agent Harness 的部分底座。
4. Capability Runtime 只执行明确请求，不决定下一步。
5. 真正 Agent Loop 至少需要 State、Tool schema、Action、Observation、termination/budget。
6. 首版更适合只读、有限步、可取消，而不是直接加 Planner/Memory/Multi-Agent。

## 认知发动机

Agent 与 Chatbot 的关键差异是模型获得受控行动权，并根据行动结果继续决策。Agent Loop 就是把部分控制权从人迁移到机器。

## 当前边界

- Agent Loop 不应直接 import Adapter/Provider。
- 首版不顺手开放 write/network/process。
- Planner 不是 Agent 成立的前提。
- Tool Contract 与 Capability Contract 可以映射但不是同一层。

## 压缩后的模型

> **Agent Loop = State → Decide → Act → Observe → Update → Stop。**

这句话不能替代前面的机制。Deep Read 的目标是能替代理解性重读，但精确行为仍应回 Raw Source 核验。

## Acceptance Gate

- [x] 覆盖与本概念有关的当前实现/规格。
- [x] 没把未来能力写成现状。
- [x] 保留关键责任转移与边界。
- [x] 没用外部框架改写 HMBuddy 自己的设计。

下一步：[R-review.md](./R-review.md)
