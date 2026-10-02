# HMBuddy Phase 2.1 — Desktop Application Foundation 需求规格说明书

**项目阶段：** Phase 2.1 / Desktop Application Foundation  
**版本：** V0.1  
**状态：** Draft / Architecture-aligned Rewrite  
**架构基线：** `requirements/hmbuddy-architecture-baseline.md` V0.1  
**前置阶段：** Phase 1 / 1.1 / 1.1.1 / Phase 2  
**文档目的：** 在 Phase 2 Desktop Entry 基础上，把 HMBuddy 从“一次性桌面入口”升级为可持续使用的本地办公应用；只建设产品壳、配置、状态和插件管理，不提前实现 Session、TaskEngine、AgentLoop、ToolRegistry、ExtensionHost 或其他 Agent Kernel 能力。

---

# 1. 为什么重构 Phase 2.1

Phase 2.1 第一版规格形成时，HMBuddy 尚未建立统一架构总纲，因此其中包含了较多“Application Service / Recent Task / Future Persistent Task”式设计。

新的 Canonical Architecture 已明确：

> **产品功能向 WorkBuddy 学习，Agent Harness 采用 Pi 式极简原语；产品上的 Task 未来统一映射为 Session + metadata，而不是另建 TaskEngine。**

因此 Phase 2.1 需要重新收敛。

本次重构不改变 Phase 2.1 的产品目标：

- 有 Home；
- 能记住配置；
- 能记住最近工作区；
- 能管理 Plugin；
- 能恢复基本使用上下文；
- Desktop 从单页面演示升级为长期可用应用。

但删除或延后会制造第二套 Agent Domain 的内容：

- 不实现 RecentTaskEntry 领域模型；
- 不实现 Task 状态机；
- 不实现 Persistent Task Runtime；
- 不实现 Session；
- 不实现 Planner；
- 不实现 AgentLoop；
- 不实现 ToolRegistry；
- 不实现 ExtensionHost。

Phase 2.1 只做：

> **Desktop Application Foundation。**

---

# 2. Architecture Alignment

## 2.1 Architecture Baseline

```text
requirements/hmbuddy-architecture-baseline.md
Version: V0.1
```

---

## 2.2 Product Capability

本阶段新增的产品能力：

```text
Home
Settings
Application Config
Application State
Recent Workspaces
Recent Activity
Plugin Manager
System Status
Desktop Navigation Shell
```

这些属于 WorkBuddy-like Product Layer。

---

## 2.3 Kernel Primitives Used

本阶段只使用已经存在的：

```text
Workspace
Artifact
```

以及已有 File Capability Runtime。

---

## 2.4 Kernel Primitives NOT Implemented

本阶段明确不实现：

```text
Session
AgentLoop
ToolRegistry
ExtensionHost
```

原因：

> Phase 2.1 是产品应用基础阶段，不是 Minimal Agent Kernel 阶段。

---

## 2.5 Tools

```text
None
```

Phase 2.1 不向模型暴露 Agent Tool。

---

## 2.6 Skills

```text
None
```

SenseWright 等 Skill 在后续 Minimal Agent Kernel 形成后再接入。

---

## 2.7 Extensions

```text
None
```

本阶段不为了 Config / Plugin Manager 引入 ExtensionHost。

---

## 2.8 Capability Plugins

复用当前已有 File Capability Plugins：

- DOCX；
- PDF；
- XLSX；
- PPTX；
- XLS；
- DOC；
- Text；
- External Plugins。

不新增新的 Capability Plugin Contract。

---

## 2.9 New Core Primitive

```text
No
```

---

## 2.10 Architecture Deviation

```text
None
```

---

# 3. Phase 2.1 核心问题

Phase 2 已经回答：

> 用户能否通过桌面界面选择 Workspace、读取 Artifact、查看内容并进行文档问答？

Phase 2.1 只回答：

> **HMBuddy 能否成为一个可以每天重复打开、记住配置、重新进入最近工作环境、理解当前 Plugin 能力状态的本地桌面应用？**

目标体验：

```text
Launch HMBuddy
      ↓
Home
├─ Open Workspace
├─ Open File
├─ Recent Workspaces
├─ Recent Activity
└─ System Status

Settings
├─ General
├─ Model
└─ Paths

Plugins
├─ Installed / Discovered
├─ Status
├─ Capability
├─ Permission
├─ Enable / Disable
└─ Rescan
```

本阶段不回答：

> Agent 如何自主完成多步骤任务？

这是后续 Minimal Agent Kernel 的职责。

---

# 4. 阶段目标

## G1. 建立统一 AppConfig

不再由 Desktop 页面和 LLM Client 各自散读环境变量。

AppConfig 至少覆盖：

- LLM Base URL；
- LLM Model；
- API Key 来源；
- External Plugin Directories；
- OCR / Model Directory；
- Plugin enable / disable；
- Restore Last Workspace；
- Recent Workspace Limit；
- Recent Activity Limit。

调用方通过一个统一配置入口获得 Effective Config。

---

## G2. 建立最小 AppState

AppState 表达：

> 应用最近发生过什么。

只保存可恢复的轻量 UI / Workspace 元数据。

例如：

- last workspace；
- last selected artifact；
- recent workspaces；
- recent activity；
- last active page。

AppState 不是：

- Session Store；
- Task Store；
- Chat History；
- Agent Checkpoint；
- Tool Call Store。

---

## G3. 建立 Home

启动应用默认进入 Home，而不是空白 Workspace 页面。

Home 是产品导航入口，不承担业务逻辑。

至少展示：

- Open Workspace；
- Open File；
- Recent Workspaces；
- Recent Activity；
- System Status。

---

## G4. 建立 Recent Workspace

用户再次启动时可以直接回到最近 Workspace。

至少支持：

- open；
- pin；
- unpin；
- remove；
- missing path；
- clear recent。

---

## G5. 建立 Recent Activity，而不是提前建立 Task Domain

旧规格中的 `RecentTaskEntry` 删除。

Phase 2.1 改为：

```text
RecentActivityEntry
```

它只表达：

> 用户最近在哪个 Workspace / Artifact / 页面做过什么，可从哪里重新进入。

例如：

```text
打开了“需求说明书.docx”
在“制度库项目”工作区进行文档问答
最近查看“财务分析报告.xlsx”
```

它不是产品 Task 的最终数据模型。

未来 Minimal Agent Kernel 实现 Session 后：

```text
Product Task
   ↓
Session + metadata
```

Recent Activity 中与 Agent 工作相关的入口应迁移为 Session Index，而不是继续发展 RecentActivity 为 TaskEngine。

---

## G6. 将现有 Plugin Runtime 暴露给用户

Plugin Manager 只做：

> **观察和控制已有 File Capability Runtime。**

它必须直接消费现有：

- DiscoveryReport；
- PluginManifest；
- LoadReport；
- CapabilityRegistry；
- PermissionPolicy；
- CapabilityCatalog。

禁止 Desktop 维护第二套 Plugin Registry。

---

## G7. 建立 Settings

Settings 至少提供：

```text
General
Model
Paths
Plugins
```

用户不再需要修改源码或手工编辑环境变量才能完成基础设置。

---

## G8. 建立 Desktop Shell / Navigation

Desktop 不再把所有职责继续堆进一个 `desktop/app.py`。

但本阶段也不建设复杂前端框架。

目标只是形成：

```text
Desktop Shell
├─ Home
├─ Workspace
├─ Plugins
└─ Settings
```

Artifact 仍作为 Workspace 下的工作视图。

---

# 5. 非目标

## 5.1 不实现 Session

架构总纲已将 Session 定义为未来 Kernel Primitive。

Phase 2.1 不提前实现半套 Session。

---

## 5.2 不实现 TaskEngine

禁止引入：

- TaskGraph；
- TaskStep；
- WorkflowStateMachine；
- StepDependency；
- Retry Scheduler；
- Planner State；
- Task Database。

---

## 5.3 不实现 AgentLoop

不新增：

- model tool calling loop；
- planning；
- autonomous file selection；
- autonomous execution。

---

## 5.4 不实现 ToolRegistry

本阶段没有 Agent，因此没有必要建立 Agent Tool Contract。

---

## 5.5 不实现 ExtensionHost

Plugin Manager 管的是已有 File Capability Plugin，不是未来 Agent Extension。

不要因为产品页面叫“Plugins”就提前实现 Agent Extension Framework。

---

## 5.6 不实现 Skills

不实现：

- Skill Discovery；
- Skill Registry；
- Skill Context Injection。

---

## 5.7 不实现 Automation / MCP / Memory / Multi-Agent

这些后续优先通过 Extension 实现。

---

## 5.8 不实现 Artifact 写回

不实现：

- create；
- edit；
- patch；
- version；
- diff。

---

## 5.9 不实现 Workspace 内容索引

Recent Workspace 不是：

- RAG；
- Embedding；
- Semantic Search；
- Full-text index。

---

## 5.10 不实现 Plugin Marketplace

只管理本地已经存在的 Capability Plugins。

---

## 5.11 不实现 EXE / MSI

本阶段不做 Installer / Auto Update。

---

# 6. 目标架构

```text
┌──────────────────────────────────────────┐
│ Desktop Product Layer                    │
│ Home / Workspace / Plugins / Settings    │
└───────────────────┬──────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────┐
│ Minimal Application State                │
│ AppConfig / AppState / Recent Views      │
└───────────────────┬──────────────────────┘
                    │
       ┌────────────┼─────────────┐
       ▼            ▼             ▼
   Workspace    Plugin Runtime    LLM Client
       │            │
       ▼            ▼
   Artifact     Capability
               Registry
```

注意：

> Phase 2.1 不引入新的 Agent Runtime 层。

未来 Minimal Agent Kernel 会放在 Product Layer 与现有 Runtime 之间，但不属于本阶段。

---

# 7. 模块设计原则

Phase 2.1 不采用重型：

```text
Domain Service
Repository
Use Case
CQRS
Event Bus
Application Framework
```

只引入足够小的模块。

推荐：

```text
application/
├─ config.py
├─ state.py
├─ recent.py
└─ plugins.py
```

也允许更少文件，只要职责清楚。

这些模块是：

> 简单应用逻辑模块。

不是未来 Kernel Primitive。

---

# 8. Desktop 目录建议

```text
desktop/
├─ app.py
├─ shell.py
├─ pages/
│  ├─ home.py
│  ├─ workspace.py
│  ├─ plugins.py
│  └─ settings.py
└─ presenter.py
```

不要求为了满足目录图机械拆分。

原则：

> 当单个文件职责已经明显过多时再拆。

---

# 9. 用户数据目录

必须正式建立 HMBuddy per-user data directory。

Windows 默认建议：

```text
%APPDATA%\HMBuddy\
├─ config.json
├─ state.json
└─ logs/
```

开发和企业部署允许通过：

```text
HMBUDDY_CONFIG_PATH
HMBUDDY_STATE_PATH
```

覆盖。

用户状态不得默认写入：

- Git Repository；
- Project Root；
- Workspace；
- plugins directory。

---

# 10. AppConfig

建议 V0.1：

```yaml
schema_version: 1

llm:
  base_url:
  model:
  api_key_env: HMBUDDY_LLM_API_KEY

paths:
  external_plugin_dirs: []
  model_dir:

plugins:
  disabled_plugin_ids: []

desktop:
  restore_last_workspace: true
  recent_workspace_limit: 10
  recent_activity_limit: 20
```

---

# 11. Config Source Precedence

必须保持确定性：

```text
Built-in Default
       ↓
User config.json
       ↓
Environment Variables
       ↓
Explicit Runtime Arguments
```

越下面优先级越高。

UI 必须能解释当前 Effective Value 来源。

例如：

```text
Model: deepseek
Source: Environment
HMBUDDY_LLM_MODEL
```

如果环境变量正在覆盖用户 Config：

> UI 不得假装修改 config.json 就会改变当前 Effective Value。

---

# 12. Config API

不要求复杂 Service Framework。

一个简单契约即可：

```python
load_config(...)
save_config(...)
resolve_effective_config(...)
validate_config(...)
```

如果使用类，也保持极小：

```python
ConfigStore
```

不要扩成多层 Repository / Manager / Service。

---

# 13. Config 持久化要求

## FR-C01 Atomic Write

使用：

```text
config.json.tmp
→ flush
→ replace
→ config.json
```

---

## FR-C02 Invalid Config

非法配置：

- 应用继续启动；
- 使用 Built-in Defaults / 可解析部分；
- Settings 显示错误；
- 原文件保留供排查。

---

## FR-C03 Secret

config.json 不保存明文：

- API Key；
- Password；
- Token。

只保存：

```text
api_key_env
```

或未来 Secret Reference。

---

## FR-C04 schema_version

Config 第一版就必须有 schema_version。

---

# 14. AppState

建议 V0.1：

```yaml
schema_version: 1

last_view:
  page: home
  workspace_path:
  artifact_path:

recent_workspaces: []

recent_activity: []
```

State 与 Config 必须分开。

---

# 15. 为什么删除 RecentTaskEntry

旧规格建立：

```text
RecentTaskEntry
task_id
task_type
status
resume_target
...
```

新架构下这会产生两个问题。

### 问题 1

未来 Product Task 的正式底层已经确定为：

```text
Session + metadata
```

如果 Phase 2.1 先造 RecentTaskEntry，未来必须：

```text
RecentTask
→ Session
```

重复迁移。

### 问题 2

为了让 RecentTask 看起来完整，会逐渐诱导加入：

- status machine；
- task history；
- artifact relations；
- conversation history；
- resume state。

最终提前长出 TaskEngine。

因此 Phase 2.1 只保存：

```text
RecentActivityEntry
```

作为 UI 导航历史。

---

# 16. RecentActivityEntry

建议：

```text
entry_id
activity_type
workspace_path
artifact_path
title
last_opened_at
resume_view
```

activity_type V0.1 可以只包括：

```text
workspace
artifact
artifact_qa
```

不得保存：

- Agent execution state；
- Tool Call Stack；
- LLM hidden state；
-完整 Prompt；
-完整 Answer；
- Artifact 正文。

---

# 17. Future Session Migration

未来 Minimal Agent Kernel 建立 Session 后：

```text
Recent Activity
      │
      ├─ 普通 Workspace / Artifact activity
      │      → 继续保留
      │
      └─ Agent Task
             → Session Index
```

Home 产品层可以显示统一的：

```text
Recent Work
```

但来源可以是：

- Workspace Activity；
- Artifact Activity；
- Session。

这属于 Product Aggregation，不需要统一成一个 Task Engine。

---

# 18. Recent Workspace

建议模型：

```text
workspace_id
path
display_name
last_opened_at
pinned
last_artifact_path
```

排序：

```text
Pinned
↓
last_opened_at DESC
```

Pinned 项不因 recent limit 自动淘汰。

---

# 19. Recent Workspace 行为

## RW-01 Open

```text
click
→ validate path
→ Workspace(...)
→ list artifacts
→ update last_opened_at
→ enter Workspace page
```

---

## RW-02 Missing

路径不存在：

```text
Missing
```

支持：

- Remove；
- Relocate。

不得直接删除历史。

---

## RW-03 Clear

Clear Recent Workspaces 默认保留 pinned。

---

# 20. Home

Home 只做导航和状态。

建议布局：

```text
Home

Quick Actions
├─ Open Workspace
└─ Open File

Recent Workspaces
├─ ...
└─ ...

Recent Activity
├─ ...
└─ ...

System Status
├─ LLM
├─ Plugins
└─ OCR / Model Directory
```

Phase 2.1 不增加：

```text
Tasks
Plans
Automations
Skills
```

这些以后有真实 Runtime 后再显示。

---

# 21. Desktop Navigation

至少明确：

```text
Home
Workspace
Plugins
Settings
```

Artifact 作为 Workspace 内视图。

不要求 SPA Router。

可以只维护：

```python
current_page
navigate(page, payload=None)
```

这样的轻量机制。

---

# 22. Plugin Manager 的架构定位

Plugin Manager 是：

> **现有 File Capability Runtime 的 Product View。**

它不是新的 Plugin Engine。

调用关系：

```text
Plugin Page
     ↓
Plugin View Builder
     ↓
existing Discovery / LoadReport / Registry / Policy
```

---

# 23. Plugin Manager 展示

至少：

- Name；
- Plugin ID；
- Version；
- API Version；
- Source；
- Status；
- Extensions；
- Capabilities；
- Declared Permissions；
- Effective Permissions；
- Availability；
- Load Error。

---

# 24. Plugin Status

建议：

```text
Enabled
Disabled
Load Failed
Incompatible
Unavailable
```

Disabled Plugin：

- 仍可 Discovery；
- Manifest 仍可展示；
- 不进入 Effective Registry；
- 不参与 Routing。

---

# 25. Plugin Enable / Disable

enable / disable 属于：

```text
AppConfig
```

不修改：

- plugin.json；
- plugin.py。

例如：

```yaml
plugins:
  disabled_plugin_ids:
    - user.foo.reader
```

---

# 26. Built-in Plugin

Built-in Plugin 可以允许 Disabled，但必须提示影响。

例如：

> 禁用 DOCX Core Plugin 后，当前 Runtime 可能失去 DOCX read provider。

不得从 UI 删除 Built-in Plugin 文件。

---

# 27. External Plugin Directory

Settings 支持：

- Add；
- Remove；
- Rescan。

来源：

```text
AppConfig
HMBUDDY_PLUGIN_PATH
```

Effective Discovery Paths：

- 去重；
- 保持顺序确定；
- UI 展示 Source。

环境变量来源路径不能由 UI 假装删除。

---

# 28. Plugin Rescan

调用现有 Runtime：

```text
Discover
→ Validate Manifest
→ Apply disabled ids
→ Load
→ Build Registry
→ Build Catalog
→ Refresh Product View
```

不得在 Desktop 重写一套 Loader。

---

# 29. Permission 边界

Phase 2.1 只展示：

- Declared Permissions；
- Effective Permissions；
- Permission Error / Unavailable。

不新增 GUI 动态授权体系。

原因：

> Permission Policy 属于 Kernel / Capability Runtime 安全边界。

未来 WorkBuddy-like Approval 应通过：

```text
Policy + before_tool Hook
```

实现，而不是混进 Phase 2.1 Plugin Manager。

---

# 30. Settings

## General

- Restore Last Workspace；
- Recent Workspace Limit；
- Recent Activity Limit。

## Model

- Base URL；
- Model；
- API Key Source；
- Effective Source。

## Paths

- Model Directory；
- External Plugin Directories。

## Plugins

跳转到 Plugin Manager。

---

# 31. Config 生效策略

## Immediate

例如：

- recent limit；
- restore last workspace。

---

## Rebuild Plugin Runtime

例如：

- external plugin dirs；
- plugin enable / disable。

---

## Recreate LLM Client

例如：

- base url；
- model；
- api key source。

---

## Restart Required

V0.1 尽量没有。

如确实存在必须明确提示。

---

# 32. System Status

只做用户可解释性，不建设监控平台。

至少：

### LLM

```text
Ready
Not Configured
Error
```

### Plugins

```text
Loaded: N
Disabled: N
Error: N
```

### Model Directory

```text
Configured
Missing
Not Required
```

### Last Workspace

```text
Available
Missing
None
```

---

# 33. 启动流程

目标：

```text
Start
  ↓
Resolve App Data Paths
  ↓
Load Config
  ↓
Resolve Effective Config
  ↓
Load AppState
  ↓
Assemble Plugin Runtime
  ↓
Initialize LLM Client
  ↓
Build Desktop Shell
  ↓
Home
```

以下问题不得阻止应用进入 Home：

- LLM Missing；
- Config 部分错误；
- State Corrupt；
- External Plugin Error；
- Last Workspace Missing；
- OCR Model Missing。

只有 Kernel / GUI 本身无法初始化时才启动失败。

---

# 34. Composition Root

`desktop/app.py` 应逐渐成为：

> Application Composition Root。

负责组装：

- config；
- state；
- plugin runtime；
- llm client；
- desktop shell。

不继续承载全部页面业务逻辑。

---

# 35. State 持久化

## 35.1 Atomic Write

state.json 也使用 atomic replace。

---

## 35.2 Corrupt State

State 可重建。

策略：

```text
保留 corrupt file
→ empty AppState
→ 应用继续启动
```

---

## 35.3 schema_version

必须存在。

---

# 36. State 保存内容边界

允许：

- paths；
- ids；
- timestamps；
- UI view；
- display title；
- pin；
- activity type。

禁止：

- Artifact 正文；
- LLM Prompt 全文；
- LLM Answer 全文；
- API Key；
- Token；
- Provider instance；
- Tk Widget；
- Thread；
- Python arbitrary object。

---

# 37. State 保存时机

立即：

- Settings；
- Plugin enable / disable；
- pin / unpin；
- remove recent。

可节流：

- recent activity；
- last workspace；
- last artifact。

具体 debounce 属于实现细节。

---

# 38. JSON vs SQLite

Phase 2.1 继续使用：

```text
config.json
state.json
```

理由：

- 数据小；
- 无复杂查询；
- 单用户；
- 单进程；
- 易调试；
- 无额外依赖。

未来 Session / Conversation / ArtifactVersion 大规模进入后，再基于真实数据模型决定是否 SQLite。

**不得为了“以后肯定会用数据库”提前引入。**

---

# 39. 多进程边界

V0.1 假设：

> 单用户单 Desktop 实例。

不处理：

- file lock；
- multi-process state merge；
- IPC；
- SQLite concurrency。

---

# 40. Logging

建议 logger：

```text
hmbuddy.config
hmbuddy.state
hmbuddy.desktop
hmbuddy.plugins
```

日志允许记录：

- config load/save；
- state load/save；
- plugin rescan；
- plugin enable/disable；
- workspace open；
- missing path。

禁止记录：

- API key；
- token；
- artifact full content；
- full prompt。

---

# 41. 错误处理

## ER-01 Config Error

继续启动，展示 Settings Error。

## ER-02 Config Save Error

不覆盖当前有效内存状态，并提示用户。

## ER-03 State Corrupt

创建空 State，保留错误文件。

## ER-04 Workspace Missing

显示 Missing，可 Remove / Relocate。

## ER-05 Plugin Discovery / Load Error

Plugin Manager 显示错误，其他插件继续运行。

## ER-06 Disabled Provider

打开文件时如果唯一 Provider 被禁用，应明确提示：

> 所需文件能力当前已禁用。

不要只返回 Unsupported File。

## ER-07 LLM Not Configured

文件浏览和 Artifact 阅读仍可正常使用。

---

# 42. 测试策略

## T1 Config

覆盖：

- default；
- load；
- env override；
- runtime override；
- validation；
- invalid JSON；
- atomic write；
- secret not persisted；
- schema version。

---

## T2 State

覆盖：

- load/save；
- corrupt recovery；
- atomic write；
- schema version；
- last view。

---

## T3 Recent Workspace

覆盖：

- add；
- deduplicate；
- open；
- pin；
- limit；
- missing；
- remove；
- clear。

---

## T4 Recent Activity

覆盖：

- workspace activity；
- artifact activity；
- artifact_qa activity；
- ordering；
- limit；
- resume_view；
- no content persistence。

---

## T5 Plugin Product View

覆盖：

- built-in；
- external；
- enabled；
- disabled；
- load failed；
- incompatible；
- unavailable；
- permissions；
- capabilities；
- extensions。

---

## T6 Plugin Config

覆盖：

- disable 不修改 Manifest；
- disabled 不进 Effective Registry；
- rescan；
- external directory add/remove；
- env source path 不被 UI 删除。

---

## T7 Config Precedence

验证：

```text
Default
<
User Config
<
Environment
<
Runtime Argument
```

---

## T8 Desktop Smoke

至少：

1. 启动进入 Home；
2. 打开 Workspace；
3. Workspace 进入 Recent；
4. 重启后 Recent 仍在；
5. Missing Workspace 正确展示；
6. Settings 修改模型配置；
7. Plugin Manager 查看现有插件；
8. Disabled External Plugin；
9. Rescan 后状态正确；
10. LLM 未配置仍可读取文件。

---

## T9 Architecture Guard Test

代码审阅 / 测试应确认 Phase 2.1 没有新增：

```text
TaskEngine
Session
AgentLoop
ToolRegistry
ExtensionHost
Planner
Workflow Graph
```

如实现过程中发现确实需要，必须先走 Architecture Change，而不是直接加入。

---

# 43. 验收标准

Phase 2.1 V0.1 完成必须满足：

### AC-01 Architecture Alignment

实现遵守 `hmbuddy-architecture-baseline.md V0.1`，无新增 Core Primitive。

### AC-02 Unified Config

Desktop 不再散落读取 LLM / Plugin 路径等配置。

### AC-03 Config / State 分离

两者使用独立文件和独立语义。

### AC-04 Per-user Data

默认数据不写 Git Repository / Workspace。

### AC-05 Atomic Persistence

Config / State 均 atomic write。

### AC-06 Schema Version

Config / State 均有 schema_version。

### AC-07 Secret Boundary

Secret 不明文持久化。

### AC-08 Config Explainability

Effective Config 可以解释 Source。

### AC-09 Home

启动默认进入 Home。

### AC-10 Recent Workspace

支持 reopen / pin / missing / remove / clear。

### AC-11 Recent Activity

能够恢复基本 Workspace / Artifact / View 上下文。

### AC-12 No Fake Task Domain

不存在 RecentTaskEntry / TaskEngine / Task State Machine。

### AC-13 Future Session Compatibility

规格与实现明确预留未来：

```text
Product Task = Session + metadata
```

而不建立平行 Task 模型。

### AC-14 Plugin Manager Reuse

直接消费现有 Plugin Runtime 状态。

### AC-15 Plugin Enable / Disable

用户偏好在 AppConfig，不修改 Manifest。

### AC-16 Plugin Rescan

单插件错误不影响应用。

### AC-17 Permission Visible

Declared / Effective Permission 可查看。

### AC-18 LLM Missing Degrades Gracefully

不影响 Workspace / Artifact Runtime。

### AC-19 Desktop Responsibilities Reduced

页面职责不继续集中在单一 `desktop/app.py`。

### AC-20 Existing Runtime Reused

不重写 Workspace / Artifact / Capability Runtime。

### AC-21 No Agent Kernel Yet

不实现 Session / AgentLoop / ToolRegistry / ExtensionHost。

### AC-22 Regression

Phase 1 / 1.1 / 1.1.1 / Phase 2 回归测试继续通过。

---

# 44. 推荐实施顺序

## Step 1 — App Data Paths

先建立：

```text
config path
state path
logs path
```

---

## Step 2 — Config

集中当前 LLM / Plugin / Model 路径配置。

---

## Step 3 — AppState + Recent Workspace

先解决最直接的：

> 关闭再打开后不失忆。

---

## Step 4 — Desktop Shell + Home

有真实 Recent 数据以后再做 Home。

---

## Step 5 — Plugin Product View

把现有 Runtime 映射为 UI View Model。

---

## Step 6 — Plugin Manager

增加 enable / disable / paths / rescan。

---

## Step 7 — Recent Activity

只记录导航型 activity，不造 Task Domain。

---

## Step 8 — Settings

将 Config 暴露给用户。

---

## Step 9 — Error Recovery / Regression

收口：

- corrupt config；
- corrupt state；
- missing workspace；
- broken plugin；
- no LLM。

---

# 45. 与后续 Minimal Agent Kernel 的关系

Phase 2.1 完成后，系统应该是：

```text
Desktop Product Shell
+
Workspace / Artifact Runtime
+
File Capability Runtime
+
Config
+
AppState
+
Plugin Management
```

此时下一阶段再正式建立：

```text
Session
AgentLoop
ToolRegistry
ExtensionHost
```

而不是在 Phase 2.1 中提前混入。

---

# 46. Product Task 的后续迁移原则

未来有 Session 后：

```text
Task UI
    ↓
Session Index
    ↓
Session
```

Home 可以从：

```text
Recent Activity
```

逐步升级为：

```text
Recent Work
├─ Workspaces
├─ Artifacts
└─ Sessions / Tasks
```

无需推翻 Phase 2.1 Config / State / Shell。

---

# 47. 本阶段成功标准

Phase 2.1 是否成功，不看：

- 页面数量；
- Service 类数量；
- 代码分层复杂度。

只看四件事：

1. **用户重新打开应用，不需要重新配置。**
2. **用户可以快速回到最近 Workspace / Artifact。**
3. **用户能够理解 HMBuddy 当前有哪些文件能力、哪些可用、哪些不可用。**
4. **实现没有因为这些产品功能而提前长出新的 Agent Engine。**

---

# 48. 最终阶段定义

Phase 2：

> **HMBuddy 有了桌面入口。**

Phase 2.1：

> **HMBuddy 成为可持续使用、可配置、可恢复基本工作上下文的本地桌面应用，但仍然不是 Agent Runtime。**

Phase 2.1 完成以后，再进入：

> **Minimal Agent Kernel。**

这与 HMBuddy 的长期架构保持一致：

> **WorkBuddy-like Product on a Pi-like Minimal Harness, with an Artifact-native Office Runtime.**
