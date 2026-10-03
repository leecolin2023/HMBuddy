# Requirements

本目录统一存放 HMBuddy 的 Canonical Architecture、VNext 需求规格与历史规格。

## Canonical Architecture

- [HMBuddy Architecture Baseline V1.0 — Pi-native Banking Office Agent](./hmbuddy-architecture-baseline.md)

V1.0 自 2026-10-03 起生效，并正式取代 V0.2。

核心原则：

- **Pi-native**：直接使用 Pi 的 Agent / Session / Context / Tool / Extension / Skill / Model Runtime，不再在 HMBuddy 内重建通用 Agent Kernel；
- **Upstream First**：通用能力先跟随 Pi，上游能力成熟后优先删除重复实现；
- **No Fork by Default**：默认使用 SDK / Extension / Skill / Package / RPC，不维护长期 Pi Fork；
- **Thin Integration**：Pi 依赖集中在薄适配层，不向 Office / Banking Domain 扩散；
- **TS Host + Python Office Runtime**：TypeScript 负责 Pi-native Agent Host，Python 负责 Office 工程；
- **Domain Ownership**：HMBuddy 长期投入 Office Artifact、Patch/Diff/Validation、银行 Skills、企业治理和内网集成；
- **Migration by Capability**：旧实现不整体搬迁，只迁移重新证明有价值的领域能力；
- **Upgradeability First**：持续跟进 Pi 是正式架构能力。

## VNext Specifications

- [VNext-01 — Pi-native Bootstrap & Office Integration Spike V0.1](./vnext-01-pi-native-bootstrap-integration-spike-v0.1.md)

当前 VNext 只验证最小纵向链：Pi AgentSession → HMBuddy Extension / Tool → Python Office Bridge → DOCX → Pi final answer。VNext-01 完成前，不进入 Office Read Pack、写回、GUI 或银行业务 Skill 扩展。

## Legacy Architecture

- [V0.2 — WorkBuddy-like Product on a Pi-like Minimal Harness](./legacy/hmbuddy-architecture-baseline-v0.2.md)

旧 V0.2 及 Phase 1–2.2 已进入 Legacy。它们仍然是历史实现、学习材料、算法和 Eval 素材来源，但不再约束 VNext 架构。

Legacy implementation 已固定在：

```text
legacy/pre-pi-v0.2
```

## Legacy Phase Specifications

- [Phase 1 — Local Office Artifact Runtime V0.1](./phase-1-local-office-artifact-runtime-v0.1.md)
- [Phase 1.1 — Pluggable File Capability Runtime V0.1](./phase-1.1-pluggable-file-capability-runtime-v0.1.md)
- [Phase 1.1.1 — Plugin Runtime Contract Hardening V0.1](./phase-1.1.1-plugin-runtime-contract-hardening-v0.1.md)
- [Phase 2 — Desktop Entry & Human-in-the-loop Workspace V0.1](./phase-2-desktop-entry-v0.1.md)
- [Phase 2.1 — Desktop Application Foundation V0.1](./phase-2.1-desktop-application-foundation-v0.1.md)
- [Phase 2.1.1 — Desktop & Runtime Integration Hardening V0.1](./phase-2.1.1-desktop-runtime-integration-hardening-v0.1.md)
- [Phase 2.2 — Desktop UX Shell Redesign V0.1](./phase-2.2-desktop-ux-shell-redesign-v0.1.md)

> 不再继续原规划中的 “Phase 3 / Minimal Agent Kernel”。VNext 从 Pi-native bootstrap 重新编号和设计。

## VNext Specification Rule

所有新的需求规格必须包含 `Architecture Alignment`，至少回答：

1. 依赖哪个 Pi release / public contract；
2. 使用 Pi SDK、Extension、Skill、Package 还是 RPC；
3. HMBuddy 新增的是 Banking / Office Domain 能力，还是通用 Agent 能力；
4. 为什么不能直接由 Pi 上游能力满足；
5. 是否增加 Pi 耦合面；
6. 是否迁移 Legacy 代码，如迁移，迁移的是哪项能力与哪些 tests；
7. 对 Pi 升级兼容性有什么影响；
8. 是否触发 Architecture Change Threshold。
