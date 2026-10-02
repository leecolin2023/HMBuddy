
# HMBuddy Phase 2.1 — Desktop Application Foundation 需求规格说明书

**项目阶段：** Phase 2.1 / Desktop Application Foundation  
**版本：** V0.1  
**阶段主题：** Configuration / Plugin Management / Recent Workspace & Task Entry  
**文档目的：** 在已完成 Phase 2 Desktop Entry 的基础上，为 HMBuddy 建立真正桌面应用所需要的最小“应用状态层”，统一解决配置管理、Plugin 管理、最近工作区与最近任务入口，使桌面端从一次性入口升级为可持续使用、可配置、可恢复上下文的办公应用。

---

## 1. 为什么新建 Phase 2.1，而不是修改 Phase 2

Phase 2 已经完成并形成明确的历史合同，其核心问题是：

> 用户能否启动一个桌面界面，选择 Workspace、读取 Artifact，并在同一界面完成查看与问答？

Phase 2 已经实现并验收了桌面启动入口、Workspace 选择、文件列表、Artifact 读取、文件概览、LLM 问答、后台线程和 Windows 启动脚本。

因此 Phase 2 不应再被反向扩写。

本次新增的三类能力——配置管理、Plugin 管理、最近工作区 / 最近任务入口——解决的是另一个问题：

> **HMBuddy 能否记住用户的应用级偏好和使用上下文，并把已有 Plugin Runtime 变成用户可观察、可控制的桌面能力？**

这已经超出 Desktop Entry，但又尚未进入完整 Agent / Persistent Task Runtime。

因此阶段关系确定为：

Phase 2 Desktop Entry  
→ Phase 2.1 Desktop Application Foundation  
→ Future Phase: Workspace Search / Artifact Update / Persistent Task / Agent Loop

Phase 2.1 是“桌面入口”与“长期桌面工作台”之间的应用基础层。

---

## 2. 当前系统基础

### 2.1 Phase 1 — Artifact Runtime

已有 Workspace、ArtifactRef、Artifact、ArtifactBlock、read_artifact() 以及 Office / PDF / Text 等文件读取能力。

### 2.2 Phase 1.1 / 1.1.1 — Plugin Runtime

已有 Plugin Manifest、Plugin Discovery、Plugin Loader、Capability Registry、Capability Router、Permission Policy、Runtime Trace、Built-in / External Plugin，以及 HMBUDDY_PLUGIN_PATH 外部插件目录。

Plugin Runtime 已经是实际运行能力，而不是未来设计。

### 2.3 Phase 2 — Desktop Entry

已有桌面页面可以完成：

选择 Workspace → 查看文件 → 读取 Artifact → 查看概览 → LLM 问答。

但桌面端目前基本属于“无记忆应用”：

- 关闭后不会记住最近 Workspace；
- 模型配置依赖环境变量；
- Plugin Runtime 没有桌面可视化管理入口；
- 没有应用级 Config Store；
- 没有 Recent State；
- 没有 Home / Recent Entry；
- 没有真正意义上的“继续上次工作”。

Phase 2.1 即解决这些问题。

---

## 3. Phase 2.1 核心问题

本阶段只回答：

> **HMBuddy 能否在保持本地优先、离线友好和插件化架构的前提下，建立统一的应用配置与本地状态存储，使用户可以管理模型与路径配置、观察和启停插件、从最近 Workspace 或最近 Task 继续工作？**

目标体验：

启动 HMBuddy  
→ Home  
→ 新工作区 / 最近工作区 / 最近任务  
→ 恢复工作上下文

同时提供：

Settings  
- General  
- Model  
- Paths  
- Plugins

Plugin Manager  
- 已发现插件  
- 状态 / 来源 / 版本  
- Capability  
- 权限  
- 启用 / 禁用  
- Discovery / Load Error

---

## 4. 阶段目标

### G1. 建立统一 App Config

系统必须有正式的应用配置模型，而不是由 Desktop 各处直接读取环境变量。

配置至少覆盖：

- LLM Base URL；
- LLM Model；
- API Key 的引用方式；
- 外部 Plugin 路径；
- OCR / Model 目录；
- Plugin 启停偏好；
- 最近记录数量；
- 是否恢复上次 Workspace；
- 其他真正属于用户偏好的桌面设置。

调用方统一通过 Config Service 获取配置。

禁止 Desktop 页面把 os.environ.get(...) 散落成事实上的配置系统。

### G2. 区分 Config 与 State

Phase 2.1 必须明确两个完全不同的对象。

Config 表示：

> 用户明确设置了什么。

例如模型、服务地址、Plugin 路径、Plugin enabled / disabled、Recent Limit。

State 表示：

> 用户最近做过什么、应用上次停在哪里。

例如最近 Workspace、最近 Task、最后打开的 Workspace、最后活动时间。

二者不得混成一个 JSON。

目标关系：

AppConfig = 用户主动设置、相对稳定。  
AppState = 应用运行历史、自动更新。

这样未来才能分别处理配置迁移、历史清理、策略覆盖、隐私清理和 Task Runtime 接入。

### G3. 提供桌面配置管理入口

桌面端必须有 Settings 页面。

至少包含：

- General；
- Model；
- Paths；
- Plugins。

V0.1 不追求复杂设置中心，但必须解决“改配置不需要修改源码或手工改环境变量”的问题。

### G4. 将现有 Plugin Runtime 暴露为 Plugin Manager

Plugin Manager 必须直接基于现有 DiscoveryReport、PluginManifest、LoadReport、CapabilityRegistry、PermissionPolicy 展示真实状态。

禁止 Desktop 再维护一套独立 Plugin 清单。

用户至少可以：

- 查看已发现插件；
- 区分 Built-in / External；
- 查看版本；
- 查看支持扩展名；
- 查看 Capability；
- 查看声明权限；
- 查看加载状态；
- 查看加载错误；
- 启用 / 禁用插件；
- 增加 / 删除 External Plugin Directory；
- 手动重新扫描 Plugin。

本阶段不是 Plugin Marketplace。

### G5. 建立 Recent Workspace

Home 页面必须展示最近使用的 Workspace。

至少记录：

- Workspace Path；
- Display Name；
- Last Opened At；
- Pinned；
- Last Selected Artifact，可选引用。

支持：

- 点击直接重新打开；
- Pin / Unpin；
- 从记录中移除；
- 清空 Recent Workspace；
- 路径不存在时明确标记 Missing，而不是启动报错退出。

### G6. 建立 Recent Task Entry

Phase 2.1 需要建立“最近任务入口”，但不得因此提前实现完整 Persistent Task Runtime。

这里的 Task 定义为：

> 一个可供桌面重新进入的工作上下文引用，而不是正在执行的 Agent 状态机。

Phase 2.1 只定义 RecentTaskEntry 元数据：

- task_id；
- title；
- task_type；
- workspace_path；
- artifact_refs；
- status；
- created_at；
- updated_at；
- resume_target。

当前可以存在的 task_type，例如 artifact_qa、document_review、workspace_session。

“继续任务”在 Phase 2.1 的语义是：

> 恢复 Workspace / Artifact / 页面入口等可恢复 UI Context。

不要求恢复 Planner 内部状态、Tool Call Stack、模型隐藏状态、Agent execution checkpoint、未完成代码执行或任意 Python 对象。

这些属于未来 Persistent Task Runtime。

### G7. 支持启动后的 Home Entry

HMBuddy 启动后不再强制首先面对空白 Workspace 页面。

应进入 Home，至少提供：

- 打开工作区；
- 打开文件；
- 最近工作区；
- 最近任务；
- 系统状态摘要。

系统状态摘要至少覆盖：

- LLM Ready / Not Configured / Error；
- Plugins Loaded / Disabled / Error；
- OCR / Model Directory 状态。

Home 是导航入口，不承担业务处理。

---

## 5. 非目标

### 5.1 不实现完整 Persistent Task Engine

不实现 Task Graph、Step 状态机、Checkpoint、Agent 中断恢复、Tool Call Replay、Planner State、多步骤自动执行恢复。

Recent Task 只是桌面级引用。

### 5.2 不实现 Plugin Marketplace

不实现在线插件商店、自动下载、自动升级、在线依赖解析、插件评分和插件账号系统。

企业内网环境下，本阶段只管理已经存在于本地的插件。

### 5.3 不自动修改 Plugin 文件

启用 / 禁用不得修改 plugin.json 或 plugin.py。

用户偏好必须存放在 App Config。

Plugin Manifest 仍然是插件自身事实的权威来源。

### 5.4 不在 Config 中保存明文 Secret

Phase 2.1 V0.1 不在普通 JSON 配置中保存 API Key、Password、Token。

允许保存 api_key_env，例如 HMBUDDY_LLM_API_KEY，或者只显示当前 Secret 为 Available / Missing。

未来如确有需要，再引入 Windows Credential Manager、OS Keyring 或企业 Secret Service。

### 5.5 不实现 Workspace 内容索引

Recent Workspace 是导航历史，不是 RAG、Semantic Search、文件内容索引或 Embedding Store。

### 5.6 不包含 EXE / MSI 打包

Phase 2.1 只建立桌面应用内部基础。

不要求 PyInstaller、Nuitka、MSI、自动更新或安装器。

Packaging 应在应用配置、Plugin 目录、数据目录稳定后单独立项。

---

## 6. 核心架构

Phase 2.1 引入新的 Application State Layer。

Desktop  
- Home  
- Workspace  
- Settings  
- Plugins  

↓  

Application Services  
- ConfigService  
- AppStateService  
- PluginManagementService  
- RecentService  

↓  

Local Stores  
- config.json  
- state.json  

↓  

Existing Runtime  
- Workspace  
- Artifact  
- Plugin Runtime  
- LLM  
- Capability Registry

原则：

> Desktop 不直接读写 JSON；Desktop 调用 Application Service。

---

## 7. 本地数据目录

Phase 2.1 必须正式定义 HMBuddy 的用户数据目录。

Windows 默认建议：

%APPDATA%\HMBuddy\  
- config.json  
- state.json  
- logs\

未来打包后仍使用同一目录。

不得默认把用户配置和运行历史写入 Git Repository、Project Root、plugins 或 workspace。

原因：

- 避免 Git 污染；
- 避免多个项目副本产生不同配置；
- 为未来 EXE / MSI 做准备；
- 用户配置属于用户，而不是源码。

允许通过 HMBUDDY_CONFIG_PATH 和 HMBUDDY_STATE_PATH 覆盖默认位置，以支持开发测试、企业集中部署和 Portable Mode 实验。

Portable Mode 本身不是本阶段验收项。

---

## 8. AppConfig 设计

建议首版逻辑结构：

schema_version: 1

llm:
- base_url
- model
- api_key_env

paths:
- external_plugin_dirs
- model_dir

plugins:
- disabled_plugin_ids

desktop:
- restore_last_workspace
- recent_workspace_limit
- recent_task_limit

### 8.1 schema_version

必须存在。

未来字段结构变化时必须经过显式 Migration，不得假设 Config 永远不会变化。

---

## 9. 配置来源与优先级

必须定义确定性的配置覆盖顺序。

推荐：

1. Built-in Defaults  
2. User config.json  
3. Environment Variables  
4. Explicit Runtime Arguments

越下面优先级越高。

例如：

User Config 中 model = qwen。  
环境变量 HMBUDDY_LLM_MODEL = deepseek。  
最终 Effective Config 中 model = deepseek。

Settings 页面必须能够显示：

- 当前值；
- 来源；
- 是否可编辑。

如果环境变量覆盖了 Config，用户在 UI 中修改 Config 后不得假装修改立即生效。

应明确提示：

> 当前值由环境变量 HMBUDDY_LLM_MODEL 覆盖。

这是 Config 可解释性的必要要求。

---

## 10. Config Service

建议契约：

ConfigService.load() → ConfigSnapshot  
ConfigService.get() → AppConfig  
ConfigService.update(patch) → AppConfig  
ConfigService.validate(config) → ValidationResult  
ConfigService.save(config)  
ConfigService.reload() → ConfigSnapshot

ConfigSnapshot 至少包含：

- effective_config；
- field_sources；
- validation_warnings；
- config_path。

Desktop 不负责合并环境变量。

---

## 11. Config 写入要求

### FR-C01 Atomic Write

不得直接原地覆盖 config.json。

推荐流程：

config.json.tmp → flush → replace → config.json。

避免应用异常退出导致配置半写入。

### FR-C02 Invalid Config

Config 非法时：

- 不允许应用直接崩溃；
- 记录错误；
- 回退 Built-in Defaults；
- Settings 显示 Config Error；
- 保留原文件供排查。

### FR-C03 Unknown Field

V0.1 应优先兼容未来字段。

未知字段不影响已知字段读取，不应静默改变运行语义，保存时尽量保留。

---

## 12. AppState 设计

AppState 与 AppConfig 分开。

建议包含：

schema_version: 1

last_session:
- workspace_path
- selected_artifact_path

recent_workspaces: []

recent_tasks: []

State 可以由应用自动更新。

---

## 13. Recent Workspace 数据模型

建议 RecentWorkspace 包含：

- workspace_id；
- path；
- display_name；
- last_opened_at；
- pinned；
- last_artifact_path。

workspace_id 不得仅使用列表 index，建议基于 canonical path 产生稳定 ID。

默认排序：

Pinned 优先，然后 last_opened_at 降序。

数量由 desktop.recent_workspace_limit 控制。

Pinned Workspace 不应因为达到 Recent Limit 自动删除。

---

## 14. Recent Workspace 行为

### RW-01 打开

点击 Recent Workspace 后：

1. 检查路径；
2. 创建 Workspace；
3. 刷新文件；
4. 更新 last_opened_at；
5. 进入 Workspace 页面。

### RW-02 Missing

路径不存在时显示“路径不存在”，并提供：

- 移除记录；
- 重新定位。

不得直接删除历史，也不得应用崩溃。

### RW-03 Clear

支持 Clear Recent Workspaces。

Pinned 项默认保留，除非用户明确选择全部清理。

---

## 15. Recent Task 数据模型

Phase 2.1 的 Task 是导航引用，不是执行对象。

建议 RecentTaskEntry 包含：

- task_id；
- title；
- task_type；
- workspace_path；
- artifact_paths；
- status；
- created_at；
- updated_at；
- resume_target。

status V0.1 可使用：

- active；
- paused；
- completed；
- failed；
- unknown。

这里的状态是 UI / History 状态，不代表 Agent Engine 的强一致执行状态。

---

## 16. Resume Target

Resume Target 表达：

> 点击“继续”以后桌面应用应该导航到哪里。

例如目标可以是 Workspace 页面，也可以是 Artifact QA 页面，并携带 workspace_path 与 artifact_path。

禁止在 State 中序列化：

- Python Object；
- LLM Client；
- Adapter Instance；
- Plugin Provider Instance；
- Tkinter Widget；
- Thread；
- Tool Call Stack。

Recent Task 必须是纯数据引用。

---

## 17. Current Phase 的 Task 产生方式

Phase 2.1 不要求建立通用 Task Engine。

当前可以由 Desktop 在以下场景产生 RecentTaskEntry：

### artifact_qa

用户打开 Workspace、打开 Artifact、发起文档问答后，可以形成 task_type = artifact_qa。

### workspace_session

用户持续在同一个 Workspace 工作，可以形成 task_type = workspace_session。

但：

> 不得为了“生成任务记录”而改变 Phase 2 现有业务流程。

Recent Task 是旁路记录。

---

## 18. Task History 隐私边界

State 默认不得存储：

- Artifact 正文；
- 完整 Context；
- LLM Prompt；
- LLM Answer；
- API Key；
- Office 文件内容。

V0.1 只保存恢复入口所需要的元数据。

如果未来要保存完整 Chat History，应作为独立需求讨论。

---

## 19. Plugin Manager 页面

Plugin Manager 至少展示：

- Name；
- Version；
- Source；
- Status。

建议状态至少包括：

- Enabled；
- Disabled；
- Load Failed；
- Incompatible；
- Unavailable。

支持搜索或过滤，但复杂筛选不是强制项。

点击 Plugin 后进入详情。

---

## 20. Plugin Detail

至少展示：

### Identity

- Name；
- Plugin ID；
- Version；
- API Version；
- Source；
- Plugin Directory。

### Capability

例如 artifact.read.full。

### Accepts

例如 .docx、.doc。

### Permission

区分：

- Declared Permissions；
- Effective Permissions。

### Runtime Status

至少支持：

- Discovered；
- Loaded；
- Disabled；
- Incompatible；
- Load Failed；
- Unavailable。

---

## 21. Plugin Enable / Disable

Plugin enable 状态属于 AppConfig，不属于 plugin.json。

配置可采用 disabled_plugin_ids。

Disabled Plugin：

- 仍可以 Discovery；
- 仍可以显示 Manifest；
- 不进入有效 Registry；
- 不参与 Capability Routing；
- UI 显示 Disabled。

这样用户仍然知道：

> “这个插件存在，只是被我禁用了。”

---

## 22. Built-in Plugin 的处理

Built-in Plugin 可以允许 Disable，但必须给出影响提示。

例如：

> 禁用 hmbuddy.docx.core 后，HMBuddy 可能无法读取 .docx 文件。

V0.1 不允许从 UI 删除 Built-in Plugin 文件。

---

## 23. External Plugin Directory 管理

Settings / Plugins 页面支持：

- Add Directory；
- Remove Directory；
- Rescan。

目录来源至少包括：

- AppConfig.paths.external_plugin_dirs；
- HMBUDDY_PLUGIN_PATH。

最终 Discovery Paths 必须去重并保持确定性。

UI 必须显示每一个目录的 Source。

环境变量来源的目录不能由 UI 假装删除。

---

## 24. Plugin Rescan

用户点击 Rescan 后：

Discover  
→ Validate Manifest  
→ Apply enabled / disabled policy  
→ Load  
→ Build Registry  
→ Refresh UI

单个 Plugin 失败不得导致整个 HMBuddy 无法启动。

必须复用现有 DiscoveryReport、LoadReport、Registry 和 Runtime Error Model。

---

## 25. Plugin Permission 边界

Phase 2.1 V0.1 的 Plugin Manager：

### 必须

- 展示 declared permissions；
- 展示 effective permissions；
- 展示权限不足导致的 unavailable / error。

### 不要求

- 在 GUI 中动态授予 filesystem.write；
- 动态授予 network；
- 动态授予 process.execute；
- 动态授予 COM 权限。

原因：

Permission Policy 属于 Runtime 安全策略。

Phase 2.1 不应顺手重构 Phase 1.1.1 的安全模型。

未来如果需要“用户在 GUI 授权插件权限”，必须单独设计 per-plugin grant、enterprise policy、audit 与 override precedence。

---

## 26. Home 页面

Phase 2.1 应把启动页升级为 Home。

Home 至少包含：

- 打开工作区；
- 打开文件；
- 最近工作区；
- 最近任务；
- System Status。

System Status 至少显示：

- LLM；
- Plugins；
- OCR / Model Directory。

---

## 27. Desktop Navigation

Phase 2.1 建议建立明确导航概念：

- Home；
- Workspace；
- Artifact；
- Plugins；
- Settings。

但不要求复杂 SPA Router。

关键是页面职责不再全部塞进 desktop/app.py。

Desktop App 应逐渐成为：

> Shell / Navigation / Application Composition Root。

---

## 28. 建议模块边界

后续实施时建议：

desktop/
- app.py
- shell.py
- pages/home.py
- pages/workspace.py
- pages/plugins.py
- pages/settings.py
- presenter.py

application/
- config.py
- state.py
- recent.py
- plugin_management.py

注意：

这是推荐边界，不是要求为了“目录漂亮”机械拆文件。

只有当实际职责已经形成时再拆。

---

## 29. Application Service 边界

### ConfigService

负责：

- 配置加载；
- 配置合并；
- 配置校验；
- Source Tracking；
- 持久化。

### AppStateService

负责：

- state.json；
- Last Session；
- State Migration；
- Atomic Write。

### RecentService

负责：

- Recent Workspace；
- Recent Task；
- limit；
- pin；
- remove；
- clear。

### PluginManagementService

负责：

- 调用 Plugin Discovery；
- 应用 enable / disable；
- Registry Refresh；
- Plugin Status View Model。

Desktop Page 不直接操作底层 Runtime。

---

## 30. 启动流程

Phase 2.1 启动顺序应确定：

Start  
→ Resolve App Data Paths  
→ Load Config  
→ Build Effective Config  
→ Load State  
→ Discover Plugins  
→ Apply Plugin Preferences  
→ Load Plugin Registry  
→ Initialize LLM Client  
→ Build Desktop Shell  
→ Home

如果 Config Broken、Plugin Broken、LLM Missing、Workspace Missing，均不得直接阻止应用启动，除非 Core 本身无法初始化。

---

## 31. 配置生效策略

不同设置应区分：

### Immediate

例如 Recent Limit、Restore Last Workspace。

保存后立即生效。

### Runtime Reload

例如 External Plugin Directory、Plugin Enable / Disable。

保存后触发 Plugin Runtime Reload。

### Recreate Client

例如 LLM Base URL、Model。

保存后重新构造 LLM Client。

### Restart Required

V0.1 尽量减少需要重启的设置。

如确实无法热更新，UI 必须明确提示 Restart required。

---

## 32. 错误处理

### ER-A01 Config Parse Error

应用继续启动，使用 defaults，并在 Settings 显示错误。

### ER-A02 Config Write Error

不得覆盖内存中的 Effective Config，提示设置保存失败。

### ER-A03 State Corrupt

State 可重建。

策略：

- 保留错误文件；
- 初始化空 State；
- 不影响 Core 功能。

### ER-A04 Recent Workspace Missing

标记 Missing，不删除。

### ER-A05 Plugin Discovery Error

进入 Plugin Manager 的 Error 区域。

### ER-A06 Plugin Load Error

单插件失败，不阻止其他插件。

### ER-A07 Disabled Required Provider

如果当前文件没有可用 Provider，应显示：

> 当前文件读取能力不可用，相关插件已被禁用。

而不是仅显示 Unsupported file。

---

## 33. Logging

Application Foundation 应建立新的 logger：

- hmbuddy.config；
- hmbuddy.state；
- hmbuddy.desktop；
- hmbuddy.plugin_management。

日志记录：

- Config load；
- Config validation；
- Config save；
- State load / save；
- Plugin rescan；
- Plugin enable / disable；
- Recent open / missing。

不得记录：

- API Key；
- Token；
- Artifact 正文；
- Prompt 全文。

---

## 34. 数据迁移

Config 与 State 都必须包含 schema_version。

即使 V0.1 只有版本 1，也必须从第一版建立 migration 概念。

禁止未来直接假设所有用户已有新字段。

---

## 35. Settings 页面详细要求

### General

至少：

- Restore Last Workspace；
- Recent Workspace Limit；
- Recent Task Limit。

### Model

至少：

- Base URL；
- Model；
- API Key Source Status。

API Key 只显示 Source 和 Available / Missing，不显示实际值。

### Paths

至少：

- Model Directory；
- External Plugin Directories。

### Plugins

可以跳转到独立 Plugin Manager 页面。

---

## 36. System Status

Home 或 Settings 应提供最小状态摘要：

LLM：
- Ready；
- Not Configured；
- Error。

Plugins：
- Loaded；
- Disabled；
- Error。

Model Directory：
- Configured；
- Missing。

Workspace：
- Last Workspace Available；
- Missing。

目的不是做监控平台，而是减少“为什么功能不可用”的黑盒感。

---

## 37. State 保存时机

不要求每一次 UI 操作都写磁盘。

### 立即保存

- Settings 修改；
- Plugin enable / disable；
- Pin / Unpin；
- Remove Recent。

### 节流保存

- recent workspace updated_at；
- last session；
- recent task updated_at。

避免频繁磁盘写入。

具体 debounce 时间属于实现细节。

---

## 38. 多进程边界

Phase 2.1 V0.1 假设：

> 同一用户同一时间只运行一个 HMBuddy Desktop 实例。

不要求解决多实例 Config 锁、State 合并、跨进程事件和 SQLite 并发。

如果未来出现真实需求，再引入 file lock / SQLite。

---

## 39. JSON 与 SQLite 的选择

Phase 2.1 V0.1 建议继续使用 config.json 和 state.json。

原因：

- 数据量极小；
- 易调试；
- 离线友好；
- 无新增依赖；
- Schema 简单；
- 当前没有复杂查询和并发。

暂不引入 SQLite。

出现以下真实需求时再切换：

- 大量 Task History；
- Chat History；
- Artifact Index；
- 多条件查询；
- 多进程；
- 大规模状态关系。

---

## 40. 测试策略

### T1 Config

必须覆盖：

- defaults；
- JSON load；
- env override；
- invalid JSON；
- validation；
- atomic save；
- secret 不落盘；
- schema_version。

### T2 State

必须覆盖：

- recent workspace；
- pin；
- limit；
- missing path；
- clear；
- corrupt state recovery。

### T3 Recent Task

必须覆盖：

- create / update；
- 排序；
- limit；
- resume target；
- 不保存 Artifact 正文。

### T4 Plugin Management

必须覆盖：

- built-in / external 展示；
- disabled plugin 不进入有效 Registry；
- disabled plugin 仍可 discovery；
- plugin load error 可见；
- external directory add/remove；
- rescan；
- duplicate plugin ID error。

### T5 Config Precedence

至少验证：

Default < User Config < Environment < Runtime Argument。

### T6 Desktop Smoke

至少验证：

1. Home 启动；
2. Recent Workspace 可打开；
3. Missing Workspace 可移除；
4. Settings 可修改 Model；
5. Plugin Manager 可查看当前插件；
6. 禁用一个非关键 External Plugin；
7. Rescan 后状态正确；
8. 重启应用后 Config / Recent 保留。

---

## 41. 验收标准

Phase 2.1 V0.1 完成必须满足：

- AC-01：存在统一 AppConfig，不再由 Desktop 各处直接散读环境变量；
- AC-02：AppConfig 与 AppState 分离；
- AC-03：用户配置默认保存在独立 per-user app data 目录；
- AC-04：Config 写入为 atomic write；
- AC-05：Config 有 schema_version；
- AC-06：State 有 schema_version；
- AC-07：环境变量覆盖 Config 时 UI 可解释来源；
- AC-08：Secret 不以明文写入 config.json；
- AC-09：Home 显示 Recent Workspace；
- AC-10：Recent Workspace 支持 pin / remove / missing；
- AC-11：Home 显示 Recent Task Entry；
- AC-12：Continue Task 只恢复可序列化 UI Context；
- AC-13：Recent Task 不包含 Agent Execution State；
- AC-14：Plugin Manager 直接读取现有 Plugin Runtime 状态；
- AC-15：可查看 Plugin Manifest / Capability / Permission / Source；
- AC-16：Plugin 可 enable / disable；
- AC-17：Disable 不修改 Plugin Manifest；
- AC-18：External Plugin Directory 可配置；
- AC-19：Plugin Rescan 单插件失败不影响应用；
- AC-20：Built-in Plugin 被禁用时有明确影响提示；
- AC-21：LLM 未配置 / Plugin Error / Workspace Missing 都不阻止 HMBuddy 启动；
- AC-22：现有 Phase 1 / 1.1 / 2 回归测试继续通过。

---

## 42. 实施顺序建议

未来真正开发时建议按以下顺序，而不是先画完整页面。

### Step 1 — App Data Path

先确定 config.json、state.json、logs 放在哪里。

### Step 2 — Config Model / ConfigService

先让现有环境变量读取集中化。

### Step 3 — AppState / Recent Workspace

先解决真正最直接的“重新打开应用”。

### Step 4 — Home

有真实 Recent 数据后再做 Home。

### Step 5 — PluginManagementService

把现有 Plugin Runtime 转换成桌面可消费 View Model。

### Step 6 — Plugin Manager UI

再做插件页面。

### Step 7 — Recent Task Contract

建立 RecentTaskEntry，并接当前 Artifact QA / Workspace Session。

### Step 8 — Settings

把 ConfigService 暴露到 UI。

### Step 9 — Recovery / Error / Eval

最后收口异常、迁移和回归。

---

## 43. 与未来阶段的关系

Phase 2.1 完成以后，HMBuddy 应具备：

文件能力 Runtime  
+ Plugin Runtime  
+ Desktop Shell  
+ Config  
+ App State  
+ Recent Entry

此时才真正具备进一步做“长期办公 Agent”的应用基础。

后续阶段可以基于真实使用优先选择：

### 方向 A — Workspace Search

解决：

> “我知道大概是什么文件，但不知道文件名。”

### 方向 B — Multi-Artifact / Compare

解决：

> “同时理解和比较多份材料。”

### 方向 C — Artifact Update

解决：

> “不只是读，还要持续修改同一个成果。”

### 方向 D — Persistent Task Runtime

解决：

> “任务做到一半退出，回来继续执行。”

### 方向 E — Agent Loop

解决：

> “让 Agent 自己选择工具、文件和执行步骤。”

Phase 2.1 本身不提前实现这些能力。

---

## 44. 最终阶段定义

Phase 2 是：

> **HMBuddy 有了桌面入口。**

Phase 2.1 是：

> **HMBuddy 开始成为一个真正可长期使用的桌面应用。**

判断 Phase 2.1 是否成功，不看页面数量，而看以下三个问题是否被稳定解决：

1. **用户不用重新配置。**
2. **用户不用重新寻找上次工作。**
3. **用户知道 HMBuddy 当前有哪些文件能力、哪些可用、哪些不可用。**

只有这三个基础成立以后，继续增加更强 Agent 能力才不会把产品建立在一个“每次启动都失忆、能力状态不可见”的桌面壳之上。
