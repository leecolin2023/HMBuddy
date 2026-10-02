# D — Deep Read：Human-in-the-loop Desktop：薄应用层与人工控制点

> SenseWright：Deep Read V6.4 · Coverage-Preserving  
> HMBuddy 基线：`6eb16968c31b7fbbae377eadd6b670287d69b27a` · 状态：Phase 2 已实现；Phase 2.1 尚为规格

## 任务

只恢复 HMBuddy 自身结构，不评价、不外推。核心问题：

> **为什么当前先做人机协同桌面入口，而不是直接让模型自主选文件和执行动作？**

## Raw Source

- `desktop/app.py`
- `desktop/presenter.py`
- `services/artifact_reader.py`
- `llm/client.py`
- `requirements/phase-2-desktop-entry-v0.1.md`
- `requirements/phase-2.1-desktop-application-foundation-v0.1.md`

## 认知拓扑

```text
用户选 Workspace
→ 列 Ref
→ 用户选文件
→ 后台 read_artifact
→ Presenter 展示
→ 用户提问
→ 后台 LLM.ask
→ 展示回答
```

## 独立认知单元

1. Desktop 是 Tkinter 薄应用层，不复制 Runtime。
2. 文件发现、读取、问答分别调用 Workspace/Facade/LLM。
3. Presenter 与 Tkinter 解耦，可 headless 测试。
4. parse 与 LLM 请求放后台线程。
5. 当前用户亲自选择 Workspace 与文件，这是关键人工控制点。
6. LLM 明确没有 Tool Calling Loop。

## 认知发动机

Human-in-the-loop 是控制复杂度的方法：先让人承担文件选择/确认，基础 Runtime 的错误更容易定位；等底座稳定再逐步把决策权迁移给模型。

## 当前边界

- Desktop 不应 import Adapter/Plugin。
- 后台线程解决 responsiveness，不等于任务可恢复。
- Workspace scan 当前可能仍同步阻塞大目录。
- 关闭应用后没有真正 persistent execution state。

## 压缩后的模型

> **Desktop = Control Surface，不是 Agent Runtime。**

这句话不能替代前面的机制。Deep Read 的目标是能替代理解性重读，但精确行为仍应回 Raw Source 核验。

## Acceptance Gate

- [x] 覆盖与本概念有关的当前实现/规格。
- [x] 没把未来能力写成现状。
- [x] 保留关键责任转移与边界。
- [x] 没用外部框架改写 HMBuddy 自己的设计。

下一步：[R-review.md](./R-review.md)
