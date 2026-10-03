# 概念地图演进：V0.1 → V0.2

旧版学习地图基线：`a0f154b`。新版基线：`14b79558cf25bba31a971fe144d83c145d9e7b46`。

## 为什么必须重画

旧版 12 概念形成时，Application Foundation 还没有真实实现，Desktop 还是更早的形态，Canonical Architecture 也尚未建立。现在继续在旧表上“加几行”会产生三个误导：

- 把已实现的 Config/State 仍当未来设计；
- 把 Conversation UI 误认为 Session；
- 把“Persistent Task”理解成即将建立的 TaskEngine，而当前架构已明确 Product Task 优先映射为 Session + metadata。

## 主要变化

- 旧 **Workspace / Artifact / Adapter / Capability / Plugin Runtime / Policy / Context / Eval** 保留，但全部按最新 2.1.1 集成事实重跑。
- 旧 **Config vs State vs Task** 拆为：
  - AppConfig / EffectiveConfig；
  - AppState / Recent Workspace / Recent Activity；
  - Application Runtime Composition。
- 旧 **Human-in-the-loop Desktop** 拆为：
  - Conversation-first Desktop Shell；
  - Artifact Preview / Representation Boundary；
  - Conversation Surface vs Session Domain。
- 旧 **Tool / Agent Loop** 拆为：
  - Session / SessionStore；
  - AgentLoop；
  - Tool / ToolRegistry。
- 旧 **Persistent Task / Recovery** 不再作为近期独立 TaskEngine 概念；其核心能力回收到 Session / Resume，并把强 DAG/Workflow 设为“只有真实失败证明才升级”。
- 新增：
  - Plugin Product View / System Status；
  - Skill / Progressive Disclosure；
  - ExtensionHost / Hooks / Events；
  - Artifact Write Lifecycle；
  - End-to-End Office Agent Capstone。

## 版本纪律

以后每次 HMBuddy 发生以下变化，应重新审阅概念地图而非只更新个别文件：

- Canonical Architecture 版本变化；
- 新增/删除 Kernel Primitive；
- Product 与 Kernel 的映射变化；
- Artifact 顶层 Contract 变化；
- Session / AgentLoop / Tool Contract 正式落地；
- Capability Plugin 与 Extension 边界变化。
