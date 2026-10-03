# R — Review：Adapter / Parsing Boundary：Native Structure、OCR 与 COM

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

- 多格式解析已证明可统一产出 Artifact。
- OCR 离线友好且默认不隐式下载。
- COM 权限能在副作用前受控。

## Findings

|级别|发现|为什么重要|
|---|---|---|
|Material|未来 create/patch 需要新的实现责任边界|应按 capability 定义 writer/patch provider，而不是让 AdapterBase 变成读写万能类。|
|Material|视觉/模型解析若引入非确定性，需要 evidence/confidence|否则 Artifact 会把概率结果伪装成确定结构。|
|Minor|性能 profile 尚未进入正式 Contract|真实大文件/视觉模型上线后再由 trace/Provider metadata 驱动。|

## Materiality Reconciliation

以下边界已经被审阅，但没有因为“还能加功能”而自动列为缺陷：

- Adapter 不做 Agent Tool selection。
- Adapter 不拥有 Workspace policy。
- Adapter 不决定 Context budget。
- 未来 writer/patcher 不应因为目录方便就强行塞进 read adapter。

Material finding 只保留会改变**正确性、下一阶段接口、信任边界或用户可解释性**的问题。

## Review 结论

当前状态：**已实现多格式读取与 OCR/COM fallback**。

总体上，该概念在当前阶段的边界是自洽的；最重要的是继续保持“当前实现”和“Canonical Future Contract”的区分。任何后续增强都应由具体失败模式触发，而不是为了让概念列表更完整。

下一步：[L-learning.md](./L-learning.md)
