# HMBuddy × SenseWright D → R → L → P 学习协议 V0.2

本学习目录基于 HMBuddy 当前 `main`：`14b79558cf25bba31a971fe144d83c145d9e7b46`，重新从零建立概念地图并重跑四路 Skill。

SenseWright 当前版本：

- D — Deep Read V6.4
- R — Vibe Review V0.10
- L — System Learning V0.5.3
- P — Practice V0.2

## 固定执行纪律

```text
Raw Source / Canonical Architecture
      ├─ D：Coverage-Preserving 恢复认知拓扑
      └─ R：重新读 Raw Source，先覆盖再按 Materiality 报告
                    ↓
              L：真实对象 Run Once
                 + 一次高信息量 Boundary Variation
                    ↓
              P：真实工程场景
                 + End-to-End
                 + Verify
                 + Troubleshoot
```

### Source Boundary

- D 不消费 R/L/P 的判断。
- R 不把 D 当证据。
- L/P 可以参考上游模型，但版本事实仍回 Raw Source。
- 对未实现的 Session / AgentLoop / ToolRegistry / ExtensionHost，只能恢复 Canonical Architecture 的设计目标，不得写成当前能力。

### 为什么这次重建而不是增量补丁

上一版学习地图形成于 `a0f154b`。此后 HMBuddy 连续完成：

1. Canonical Architecture Baseline V0.2；
2. Phase 2.1 Desktop Application Foundation；
3. Phase 2.1.1 Desktop & Runtime Integration Hardening；
4. Phase 2.2 PySide6 Conversation-first Desktop Shell。

因此旧地图中的“Config vs State vs Task”“Human-in-the-loop Desktop”“Persistent Task”等概念边界已经发生实质变化。本版直接重建整个目录，避免旧概念残留成为错误学习材料。
