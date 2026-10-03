# Learning

HMBuddy 的学习资料。

## 当前状态

2026-10-03 起 Canonical Architecture 已切换为：

- [HMBuddy Architecture Baseline V1.0 — Pi-native](../requirements/hmbuddy-architecture-baseline.md)

现有：

- [SenseWright D → R → L → P 概念学习地图 V0.2](./sensewright-drlp/README.md)

是基于旧 V0.2 “Pi-like Minimal Harness” 架构形成的，因此从现在起标记为 **Legacy Learning Map / Pending Rebuild**。

下一轮学习目录不再以“自己实现 Session / AgentLoop / ToolRegistry / ExtensionHost”为目标，而应转为：

```text
Concept
  ↓
Understand why it exists
  ↓
Locate the real implementation in Pi
  ↓
Run it
  ↓
Vary one boundary / condition
  ↓
Build a Pi Extension / Skill / Tool
  ↓
Map the remaining Office-specific gap
```

Office Domain（Artifact / Patch / Diff / Validation / DOCX/XLSX/PPTX/PDF/OCR/WPS）仍属于 HMBuddy 自己需要深入工程化的学习主线。

现有 V0.2 学习材料暂不删除，待 Pi-native baseline 稳定并完成第一个 integration spike 后，再用 SenseWright D → R → L → P 全量重建。
