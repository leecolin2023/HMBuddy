# Requirements

本目录统一存放 HMBuddy 项目的需求规格说明书（Requirements Specification）。

## 目录约定

- 每一个阶段或独立能力使用一份 Markdown 规格说明书。
- 文件名建议采用：`phase-N-<topic>-vX.Y.md`。
- 规格说明书应优先明确：目标、非目标、模块边界、接口、数据结构、错误处理、测试、验收标准和实施顺序。
- 后续架构与功能扩展应由真实问题和已观察到的失败推动，不因“完整 Agent 架构”而提前增加无关组件。

## 当前规格

- [Phase 1 — Local Office Artifact Runtime V0.1](./phase-1-local-office-artifact-runtime-v0.1.md)
- [Phase 1.1 — Pluggable File Capability Runtime V0.1](./phase-1.1-pluggable-file-capability-runtime-v0.1.md)
- [Phase 1.1.1 — Plugin Runtime Contract Hardening V0.1](./phase-1.1.1-plugin-runtime-contract-hardening-v0.1.md)
- [Phase 2 — Desktop Entry & Human-in-the-loop Workspace V0.1](./phase-2-desktop-entry-v0.1.md)

> Phase 1.1 将固定 Adapter 路由升级为 Plugin / Capability Runtime；Phase 1.1.1 专门收口代码审阅发现的权限强制、Manifest 权威性、Workspace 与 Registry 解耦、外部插件加载、Context Budget、Locator、Trace 与 CI 等问题。两者均不回滚或重编号已完成的 Phase 2；Phase 2 继续依赖稳定的 `read_artifact()` 门面。
