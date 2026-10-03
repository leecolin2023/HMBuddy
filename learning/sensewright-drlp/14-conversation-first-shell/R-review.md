# R — Review：Conversation-first Desktop Shell：Product Layer 与 Human-in-the-loop

> SenseWright：**Vibe Review V0.10 / Coverage Before Materiality**  
> Review 重新读取 Raw Source；D 仅作导航，**Reference ≠ Evidence**。

## Assignment

判断这套设计/实现是否足以完成它当前应该完成的任务；不因为未来还能更复杂，就把“当前没做”自动判成缺陷。

## Atomic Review Map

本次覆盖：

1. 概念身份与职责；
2. 输入 / 输出 Contract；
3. 控制权和依赖方向；
4. 状态 / 权限 /错误 / 生命周期（适用时）；
5. 与相邻概念的边界；
6. 当前实现 vs 目标架构；
7. 故障模式与可观察性；
8. 后续阶段会放大的隐含假设。

## 已经成立的部分

- Presentation 重写没有复制 Domain。
- Qt offscreen smoke 与静态 guard 保护边界。
- 布局可自然插入未来 Session。

## Findings

|级别|发现|为什么重要|
|---|---|---|
|Material|Conversation 外观会制造“已有多轮 Session”的用户预期|产品文案与后续实现需尽快对齐；当前明确标记临时 transcript 是必要边界。|
|Material|当前 Composer 仍以单 active Artifact 为前提|真正 Agent 需要从“先选文件再问”演进到 Workspace/Tool-driven selection。|
|Minor|同步/线程任务模型仍是桌面级后台线程|进入 AgentLoop/长任务后需迁移到 Session/Events，而不是继续堆 UI 线程逻辑。|

## Materiality Reconciliation

以下边界已经被审阅，但没有因为“还能加功能”而自动列为缺陷：

- 新建会话只清临时 UI 状态。
- 搜索只匹配元数据，不做 RAG。
- 当前 QA 仍需要 active Artifact。
- Conversation transcript 不持久化。

Material finding 只保留会改变**正确性、下一阶段接口、信任边界或用户可解释性**的问题。

## Review 结论

当前状态：**Phase 2.2 已实现（PySide6）**。

总体上，该概念在当前阶段的边界是自洽的；最重要的是继续保持“当前实现”和“Canonical Future Contract”的区分。任何后续增强都应由具体失败模式触发，而不是为了让概念列表更完整。

下一步：[L-learning.md](./L-learning.md)
