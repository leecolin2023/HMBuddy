# D — Deep Read：架构总纲：WorkBuddy-like Product on a Pi-like Minimal Harness

> SenseWright：**Deep Read V6.4 / Coverage-Preserving**  
> HMBuddy Source Baseline：`14b79558cf25bba31a971fe144d83c145d9e7b46`  
> 当前状态：**Canonical Architecture V0.2；当前有效**

## 阅读任务

只恢复 HMBuddy 当前源码/Canonical Architecture 自己建立的认知结构，不独立批判、不用外部框架改写它。

> **为什么 HMBuddy 要让产品层丰富、Kernel 长期保持小，并保留 Artifact-native Office Runtime？**

## Raw Source

- `requirements/hmbuddy-architecture-baseline.md`
- `README.md`
- `requirements/README.md`

## 认知拓扑

```text
WorkBuddy-like Product Capability
→ 映射到少量 Kernel Primitives
→ 通过 Tool / Skill / Extension / Capability Plugin 组合
→ Office 文件落到 Artifact-native Runtime
→ Policy / Events / Context 作为 Kernel Invariants
```

## 独立认知单元

1. 产品功能和 Kernel 模块不是一一对应：Task、Memory、Automation、MCP、Planner 等产品能力不自动意味着 TaskEngine、MemoryEngine、AutomationEngine。
2. 长期 Kernel 被限定为 Workspace、Artifact、Session、AgentLoop、ToolRegistry、ExtensionHost 六类原语；新增第七个原语属于高门槛 Architecture Change。
3. Policy、Events、Context 被定义为 Kernel Invariants：它们必须由 Core 保证，但不独立膨胀成大型 Engine。
4. File Capability Runtime 保留，但职责被限定为“某项文件/Artifact 能力由哪个 Provider 实现”，不是全局 Agent Plugin Framework。
5. 产品能力优先通过四个扩展面组合：Tool、Skill、Extension、Capability Plugin。
6. Office 领域不机械照搬 coding agent 的 read/write/edit/bash，因为 DOCX/XLSX/PPTX/PDF 需要结构、定位、版本和验证语义。

## 认知发动机

这套架构在控制两种相反风险：一边是产品功能不够像真正办公 Agent，另一边是为了追求功能完整把 Kernel 过早做成平台。核心策略是“Primitives, not features”，同时承认 Office 文件领域确实需要自己的 Artifact 原语。

## 当前边界

- 架构总纲是默认基线，不是永远不可修改的宪法。
- 新增 Core 原语必须由真实失败模式证明现有原语不足。
- Product Layer 可以快速演化，但不能反向要求每个页面都有同名 Engine。
- Pi-like 指极简 Harness 哲学，不等于机械复制 Pi 的实现。

## Coverage Reconciliation

本篇覆盖的是与该概念有独立语义的：**角色、输入输出、控制权、调用关系、当前实现状态、明确非目标与演进接口**。未来概念只按 Canonical Architecture 恢复其目标语义，不把设计目标升级为当前事实。

## 压缩后的认知模型

- Product features ≠ Kernel primitives。
- Kernel 保持小，复杂功能优先组合扩展面。
- Office 的领域复杂性通过 Artifact Runtime 承担，而不是塞进 AgentLoop。

Deep Read 到此只回答“HMBuddy 在说什么、为什么这样组织”。判断是否站得住交给同目录 Review。

下一步：[R-review.md](./R-review.md)
