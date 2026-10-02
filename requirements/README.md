# Requirements

本目录统一存放 HMBuddy 项目的架构基线与需求规格说明书。

## 架构基线（Canonical）

- [HMBuddy 架构设计总纲 — WorkBuddy-like Product on a Pi-like Minimal Harness](./hmbuddy-architecture-baseline.md)

该文档是 HMBuddy 后续产品设计、需求规格、实现方案和重构的上位架构基线。

核心原则：

- 产品功能层向 WorkBuddy 学习；
- Agent Harness 架构哲学采用 Pi 式极简原语；
- Office 领域保留 HMBuddy 自己的 Artifact-native Runtime；
- 新功能优先通过 Tool / Skill / Extension / Capability Plugin 组合实现；
- 不因产品新增一个功能就新增一个 Core Engine；
- 架构文档本身可持续迭代，当前文件始终代表最新有效版本，历史由 Git 保留。

从架构基线生效后，新的需求规格说明书必须包含 `Architecture Alignment`，至少说明：

- 依赖的架构基线版本；
- 使用哪些 Kernel Primitive；
- 新增哪些 Tool / Skill / Extension / Capability Plugin；
- 是否新增 Core Primitive；
- 是否存在架构偏离；
- 如存在架构变更，必须给出理由、替代方案、兼容性和迁移方案。

## 目录约定

- 架构原文档使用固定 Canonical 文件持续迭代，不为小版本复制多个“final”文件。
- 每一个阶段或独立能力使用一份 Markdown 需求规格说明书。
- Phase 文件名建议采用：`phase-N-<topic>-vX.Y.md`。
- 规格说明书应优先明确：目标、非目标、Architecture Alignment、模块边界、接口、数据结构、错误处理、测试、验收标准和实施顺序。
- 后续架构与功能扩展应由真实问题和已观察到的失败推动，不因“完整 Agent 架构”而提前增加无关组件。
- 如果需要新增 Kernel Primitive、修改 Artifact 顶层 Contract、Session 持久化语义、AgentLoop、Tool Contract、Extension Hook 或 Workspace 安全边界，必须同步更新架构总纲。

## 当前规格

- [Phase 1 — Local Office Artifact Runtime V0.1](./phase-1-local-office-artifact-runtime-v0.1.md)
- [Phase 1.1 — Pluggable File Capability Runtime V0.1](./phase-1.1-pluggable-file-capability-runtime-v0.1.md)
- [Phase 1.1.1 — Plugin Runtime Contract Hardening V0.1](./phase-1.1.1-plugin-runtime-contract-hardening-v0.1.md)
- [Phase 2 — Desktop Entry & Human-in-the-loop Workspace V0.1](./phase-2-desktop-entry-v0.1.md)
- [Phase 2.1 — Desktop Application Foundation V0.1](./phase-2.1-desktop-application-foundation-v0.1.md)

> Phase 1 / 1.1 / 1.1.1 已形成 Workspace、Artifact 和 File Capability Runtime 基础；Phase 2 建立 Desktop Entry；重构后的 Phase 2.1 只建设 Home、Config、AppState、Recent Workspace / Activity、Plugin Manager 与 Settings，不提前建立 RecentTaskEntry、Session、TaskEngine、AgentLoop、ToolRegistry 或 ExtensionHost。Phase 2.1 完成后，再按架构总纲进入 Minimal Agent Kernel。
