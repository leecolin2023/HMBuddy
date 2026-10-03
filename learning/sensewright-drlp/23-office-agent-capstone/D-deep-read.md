# D — Deep Read：End-to-End Office Agent：从工作区到持续可修改成果

> SenseWright：**Deep Read V6.4 / Coverage-Preserving**  
> HMBuddy Source Baseline：`14b79558cf25bba31a971fe144d83c145d9e7b46`  
> 当前状态：**目标闭环；Stage B–D 尚未完成**

## 阅读任务

只恢复 HMBuddy 当前源码/Canonical Architecture 自己建立的认知结构，不独立批判、不用外部框架改写它。

> **把前面所有概念组合起来，一个真正的 HMBuddy Office Agent 任务应该怎样完整运行？**

## Raw Source

- `requirements/hmbuddy-architecture-baseline.md`
- `README.md`
- `requirements/phase-2.2-desktop-ux-shell-redesign-v0.1.md`

## 认知拓扑

```text
User Goal
→ Workspace
→ Session
→ AgentLoop
→ Search/Read Tools
→ Skills
→ Artifact Create
→ Validate
→ User Feedback
→ ArtifactPatch
→ New Version + Diff
→ Complete/Resume
```

## 独立认知单元

1. Stage A（Desktop Application Foundation）已经完成。
2. Stage B 是 Minimal Agent Kernel：Session/Store、AgentLoop、ToolRegistry、ExtensionHost/Hooks。
3. Stage C 是少量 Office Primitive Tools。
4. Stage D 用一个真实端到端任务证明架构，而不是继续堆基础设施。
5. 推荐真实闭环：找材料→部分读取→生成成果→用户反馈→修改同一 Artifact→验证→Diff→完成/恢复。
6. Skill 提供工作方法，Tool 执行动作，Capability Runtime 处理格式实现，Extension 处理 Approval/Audit 等横切行为。

## 认知发动机

单个组件都正确不等于 Office Agent 成立。真正价值必须在一个跨层任务中证明：模型能在 Workspace 内找到材料、创建/修改成果、接受用户反馈并可靠恢复，同时 Core 仍保持小。

## 当前边界

- 闭环完成前不进入 Multi-Agent。
- Computer Use 只是特殊企业系统 fallback。
- MCP/Memory/Automation 按真实任务再接。

## Coverage Reconciliation

本篇覆盖的是与该概念有独立语义的：**角色、输入输出、控制权、调用关系、当前实现状态、明确非目标与演进接口**。未来概念只按 Canonical Architecture 恢复其目标语义，不把设计目标升级为当前事实。

## 压缩后的认知模型

- 真正的 HMBuddy = Minimal Agent Harness × Artifact-native Office Runtime × WorkBuddy-like Product Surface。

Deep Read 到此只回答“HMBuddy 在说什么、为什么这样组织”。判断是否站得住交给同目录 Review。

下一步：[R-review.md](./R-review.md)
