# R — Review：Workspace：工作域、文件发现与信任边界

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

- Catalog 单一真相已打通 Product/Application/Runtime。
- workspace_id 在 Core 与 RecentWorkspace 中复用。
- Plugin 动态变化能反映到当前工作区文件列表。

## Findings

|级别|发现|为什么重要|
|---|---|---|
|Material|未来 Session 必须引用 workspace_id，而不能复制另一套 Workspace identity|Phase 2.1.1 已为此统一 RecentWorkspace ID，Stage B 应继续复用。|
|Material|open_ref_from_path 使用字符串前缀判断是否在 Workspace 内部|最终安全仍由 ArtifactReader/Workspace.resolve_path 保证，但产品层可考虑统一使用 Path.resolve/relative_to，避免 UI 层预判断在大小写/符号链接上产生不一致。|
|Minor|大目录发现仍是同步模型|真实超大 Workspace 出现后再引入索引/异步扫描，不要提前把 Search Engine 塞进 Workspace。|

## Materiality Reconciliation

以下边界已经被审阅，但没有因为“还能加功能”而自动列为缺陷：

- 不是 OS sandbox。
- 不是语义搜索引擎。
- 不是 Session Store。
- 路径型 artifact/workspace identity 有本地文件系统假设。

Material finding 只保留会改变**正确性、下一阶段接口、信任边界或用户可解释性**的问题。

## Review 结论

当前状态：**已实现并在 Phase 2.1.1 与 AppRuntime Catalog 对齐**。

总体上，该概念在当前阶段的边界是自洽的；最重要的是继续保持“当前实现”和“Canonical Future Contract”的区分。任何后续增强都应由具体失败模式触发，而不是为了让概念列表更完整。

下一步：[L-learning.md](./L-learning.md)
