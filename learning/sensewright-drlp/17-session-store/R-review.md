# R — Review：Session / SessionStore：持久工作上下文、Product Task 与 Resume

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

- 架构目标简洁。
- 可以直接映射产品 Task/Conversation/History。
- 避免旧版‘Persistent Task Engine’过度设计。

## Findings

|级别|发现|为什么重要|
|---|---|---|
|Material|Session schema 必须在 ToolRegistry/AgentLoop 同时设计|messages/tool_calls/result refs 的形状会直接影响 replay/context/audit。|
|Material|需要 runtime/config/version binding 最小语义|否则重启后插件/模型变化可能让同一 Session 行为漂移。|
|Material|Artifact 引用需要 revision 策略|长期任务中源文件变化时应明确 revalidate。|

## Materiality Reconciliation

以下边界已经被审阅，但没有因为“还能加功能”而自动列为缺陷：

- Session ≠ Planner。
- Session ≠ Scheduler。
- Session 不保存运行对象实例。
- 恢复前要重建 Runtime 并校验外部依赖。

Material finding 只保留会改变**正确性、下一阶段接口、信任边界或用户可解释性**的问题。

## Review 结论

当前状态：**Canonical future Kernel primitive；Stage B 未实现**。

总体上，该概念在当前阶段的边界是自洽的；最重要的是继续保持“当前实现”和“Canonical Future Contract”的区分。任何后续增强都应由具体失败模式触发，而不是为了让概念列表更完整。

下一步：[L-learning.md](./L-learning.md)
