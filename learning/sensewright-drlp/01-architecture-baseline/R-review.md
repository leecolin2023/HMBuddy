# R — Review：架构总纲：WorkBuddy-like Product on a Pi-like Minimal Harness

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

- 架构变更门槛明确。
- Capability Plugin 与 Agent Extension 被清晰分层。
- Product Task 映射到 Session+metadata，避免预建 TaskEngine。
- Artifact-native 保留了 HMBuddy 的 Office 领域差异。

## Findings

|级别|发现|为什么重要|
|---|---|---|
|Material|六原语是设计约束，不是当前实现清单|当前真正落地的仍主要是 Workspace/Artifact/File Runtime/Application/Product Shell；Session/AgentLoop/ToolRegistry/ExtensionHost 仍是未来。学习资料必须持续区分目标架构与当前代码。|
|Material|极简原则必须与真实 Office 写能力共同演进|如果未来 Patch/Version/Diff 证明 Artifact Contract 需要兼容扩展，应按 Architecture Change 机制更新，而不是为了守住“六个”而压制真实需求。|
|Minor|产品 benchmark 容易被误用成架构依据|WorkBuddy/Goose/Cherry Studio 等更适合提供 UX/产品模式，Kernel 选择仍应由 HMBuddy 自身失败模式驱动。|

## Materiality Reconciliation

以下边界已经被审阅，但没有因为“还能加功能”而自动列为缺陷：

- 架构总纲是默认基线，不是永远不可修改的宪法。
- 新增 Core 原语必须由真实失败模式证明现有原语不足。
- Product Layer 可以快速演化，但不能反向要求每个页面都有同名 Engine。
- Pi-like 指极简 Harness 哲学，不等于机械复制 Pi 的实现。

Material finding 只保留会改变**正确性、下一阶段接口、信任边界或用户可解释性**的问题。

## Review 结论

当前状态：**Canonical Architecture V0.2；当前有效**。

总体上，该概念在当前阶段的边界是自洽的；最重要的是继续保持“当前实现”和“Canonical Future Contract”的区分。任何后续增强都应由具体失败模式触发，而不是为了让概念列表更完整。

下一步：[L-learning.md](./L-learning.md)
