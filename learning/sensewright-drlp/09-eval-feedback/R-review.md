# R — Review：Eval / Feedback Loop：从失败模式到可回归证据

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

- 阶段 baseline 清晰。
- 有失败路径与安装态 smoke。
- UI 重构通过守护测试保证 Domain/Runtime 不被绕过。

## Findings

|级别|发现|为什么重要|
|---|---|---|
|Material|下一阶段 Agent Kernel 需要新增 trace-level Eval|要验证 Tool call sequence、termination、Session replay，而不只是最终答案。|
|Material|真实企业文档 golden corpus 仍不足|Office write/validate 阶段尤其需要真实脱敏样本。|
|Minor|重复/漂移测试需要持续整理|例如当前 Qt test 中可见重复命名测试，后续可清理但不影响核心边界。|

## Materiality Reconciliation

以下边界已经被审阅，但没有因为“还能加功能”而自动列为缺陷：

- 测试数量不是质量分。
- 合成 fixture 不替代真实 Office corpus。
- static guard 保护架构边界但不证明用户体验好。

Material finding 只保留会改变**正确性、下一阶段接口、信任边界或用户可解释性**的问题。

## Review 结论

当前状态：**已实现多层 Eval、Phase baseline 与跨平台 CI**。

总体上，该概念在当前阶段的边界是自洽的；最重要的是继续保持“当前实现”和“Canonical Future Contract”的区分。任何后续增强都应由具体失败模式触发，而不是为了让概念列表更完整。

下一步：[L-learning.md](./L-learning.md)
