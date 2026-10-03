# HMBuddy SenseWright Learning

> **Current protocol:** Technical Learning Protocol V1.0  
> **Canonical architecture:** HMBuddy Architecture Baseline V1.0 — Pi-native  
> **Status of old 23-concept map:** Legacy / Pending Rebuild

## V1.0 quality baseline

当前只允许一个新样板先跑通质量门：

- ./00-quality-baseline-pi-agentsession-tool-calling/README.md

它负责建立后续所有技术学习材料的最低质量标准：

~~~text
真实源码
→ 人类可读的 D
→ 独立 R
→ 真实机制 L
→ 真实工程 P
→ 证据状态明确
~~~

在该样板达到 QUALITY-BASELINE 前，不再批量生成新的 23×4 学习文件。

## Legacy Concept Map V0.2

原有 01–23 概念目录全部基于旧的：

> WorkBuddy-like Product on a Pi-like Minimal Harness

它们当前仅作为历史材料，不再代表 Canonical Architecture，也不再代表 V1.0 学习质量。

特别是旧：

~~~text
17 Session / SessionStore
18 AgentLoop
19 ToolRegistry
21 ExtensionHost
~~~

不能再按“HMBuddy 自研 Kernel”方向继续。

在 Pi-native V1.0 下，这些通用 Agent 概念必须转为：

~~~text
Locate real implementation in Pi
→ run it
→ understand public seam
→ build HMBuddy extension/tool/skill only where domain requires
~~~

旧目录暂不删除，待 quality baseline 完成后逐个决定：

- 重写；
- 合并；
- 废弃；
- 或迁移为 Office Domain 学习材料。
