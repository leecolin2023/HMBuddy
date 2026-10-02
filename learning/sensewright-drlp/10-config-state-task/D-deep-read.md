# D — Deep Read：Config vs State vs Task：应用状态与任务状态

> SenseWright：Deep Read V6.4 · Coverage-Preserving  
> HMBuddy 基线：`6eb16968c31b7fbbae377eadd6b670287d69b27a` · 状态：Phase 2.1 已有规格，尚未见 application/ 实现

## 任务

只恢复 HMBuddy 自身结构，不评价、不外推。核心问题：

> **配置、应用历史、任务执行状态为什么必须分开？Recent Task 为什么还不是 Persistent Task？**

## Raw Source

- `requirements/phase-2.1-desktop-application-foundation-v0.1.md`
- `desktop/app.py`
- `README.md`

## 认知拓扑

```text
启动
→ 加载 Config + 来源优先级
→ 加载 AppState
→ 装配 Runtime/LLM
→ Home Recent
→ 运行中分别更新 Config/State
```

## 独立认知单元

1. AppConfig 是用户主动设置：模型地址、插件路径、禁用插件、recent limits。
2. AppState 是自动历史：last session、recent workspaces、recent tasks。
3. Config/State 分文件、分更新时机、分迁移/清理语义。
4. 配置优先级 Defaults < user file < env < runtime arguments，且 UI 要解释来源。
5. RecentTaskEntry 只是导航引用，不包含 LLM client、Provider、Thread、Tool stack。
6. Persistent Task/Agent Loop 被明确留到未来阶段。

## 认知发动机

三者生命周期不同：Config 描述系统应该怎样工作，State 描述应用上次在哪里，Task 描述一个工作过程做到哪一步。混在一起会把配置保存、历史清理、执行 checkpoint 变成同一类状态修改。

## 当前边界

- Recent Task 只解决“回到哪里”。
- config 不存明文 API key。
- state 默认不存正文/Prompt/Answer。
- JSON 当前足够，大量任务/并发出现后再评估 SQLite。

## 压缩后的模型

> **Config = desired behavior；State = recent application history；Persistent Task = durable execution progress。**

这句话不能替代前面的机制。Deep Read 的目标是能替代理解性重读，但精确行为仍应回 Raw Source 核验。

## Acceptance Gate

- [x] 覆盖与本概念有关的当前实现/规格。
- [x] 没把未来能力写成现状。
- [x] 保留关键责任转移与边界。
- [x] 没用外部框架改写 HMBuddy 自己的设计。

下一步：[R-review.md](./R-review.md)
