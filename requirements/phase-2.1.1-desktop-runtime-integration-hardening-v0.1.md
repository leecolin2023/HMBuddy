# HMBuddy Phase 2.1.1 — Desktop & Runtime Integration Hardening 需求规格说明书

**项目阶段：** Phase 2.1.1 / Integration Hardening  
**版本：** V0.1  
**状态：** Draft  
**架构基线：** `requirements/hmbuddy-architecture-baseline.md` V0.1  
**前置规格：** `phase-2.1-desktop-application-foundation-v0.1.md`  
**实现基线：** `161114c78e631bb5b89208071c5496dc87c7b14e`  
**形成原因：** Phase 2.1 完成后的全项目架构与功能复盘发现，产品层、Application Foundation 与 File Capability Runtime 之间仍存在若干集成缝隙；同时最新 GitHub Actions 中 Windows 与 wheel smoke 通过、Linux pytest 失败，说明跨平台测试契约尚未收口。  
**文档目的：** 修复 Phase 2.1 已实现功能中的集成一致性、真实产品路径和工程验证问题，不新增 Session、AgentLoop、ToolRegistry、ExtensionHost、Skill、MCP、Memory、Automation 等 Agent 能力。

---

# 1. 阶段定位

Phase 2.1 已经完成：

~~~text
Desktop Shell
Home
Workspace
Plugins
Settings

AppConfig
EffectiveConfig
AppState
Recent Workspace
Recent Activity

Plugin Product View
System Status
~~~

同时继续复用：

~~~text
Workspace
Artifact
ArtifactReader
File Capability Runtime
Capability Catalog
LLM Context
~~~

Phase 2.1.1 不新增产品大功能。

本阶段只回答：

> **当前 Desktop、Application Foundation 与 Runtime 是否真正共享同一套能力事实、配置事实、Workspace 身份和错误语义，并且真实用户路径与 CI 均能证明这一点？**

目标是：

> **把 Phase 2.1 从“主体功能完成”提升到“集成边界收口，可以安全进入 Minimal Agent Kernel”。**

---

# 2. Architecture Alignment

## 2.1 Architecture Baseline

~~~text
requirements/hmbuddy-architecture-baseline.md
Version: V0.1
~~~

---

## 2.2 Product Capability

本阶段不增加新的 WorkBuddy-like 产品能力。

只修正已有：

~~~text
Workspace
Recent Activity
Settings
Plugin Manager
LLM QA
File Picker
System Status
~~~

的真实行为。

---

## 2.3 Kernel Primitives Used

复用已有：

~~~text
Workspace
Artifact
~~~

以及 File Capability Runtime。

---

## 2.4 Kernel Primitives NOT Implemented

继续不实现：

~~~text
Session
AgentLoop
ToolRegistry
ExtensionHost
~~~

---

## 2.5 Tools

~~~text
None
~~~

---

## 2.6 Skills

~~~text
None
~~~

---

## 2.7 Extensions

~~~text
None
~~~

---

## 2.8 Capability Plugins

不新增 Capability Contract。

只修复现有 Runtime 与 Product Layer 的一致性。

---

## 2.9 New Core Primitive

~~~text
No
~~~

---

## 2.10 Architecture Deviation

~~~text
None
~~~

如果实现过程中发现必须增加新的 Kernel Primitive，必须停止当前实现并按 Canonical Architecture 的 Architecture Change 流程处理。

---

# 3. 已确认问题总览

| 编号 | 优先级 | 问题 | 影响 |
|---|---|---|---|
| INT-001 | P0 | AppRuntime CapabilityCatalog 未传入 Workspace | Plugin Manager 与 Workspace 可能看到两套不同能力事实 |
| INT-002 | P0 | OpenAICompatibleClient 未初始化 BaseLLMClient | 真实文档问答调用 `ask()` 时可能缺失 `context_policy` |
| INT-003 | P1 | EffectiveConfig 用 truthy 判断 User Value | `False` / `0` 无法作为合法显式配置 |
| INT-004 | P1 | bootstrap 的显式 env 未贯穿到 EffectiveConfig | 测试、便携部署和显式环境注入语义不稳定 |
| INT-005 | P1 | Plugin Unavailable 状态未真正落入状态字段 | Product View 状态与规格不一致 |
| INT-006 | P1 | Recent Activity Treeview selection 映射不稳定 | GUI 双击 Recent Activity 可能无法恢复 |
| INT-007 | P1 | RecentWorkspace 使用随机 workspace_id | Application State 与 Core Workspace 存在两套 Workspace 身份 |
| INT-008 | P1 | CI 跨平台测试契约未定义清楚 | Windows 主产品通过但整体 CI 为红 |
| INT-009 | P2 | File Picker 扩展名仍静态硬编码 | 新 Capability Plugin 不能完整进入 Product UX |
| INT-010 | P2 | PluginView 按 Provider 生成行 | 一个多 Provider Plugin 会在 UI 重复多行 |
| INT-011 | P2 | Recent QA Activity 持久化用户问题前 40 字 | 企业内网场景存在不必要的敏感信息落盘 |
| INT-012 | Docs | Canonical Architecture 仍描述 Phase 2.1 为需求阶段 | 架构原文档与真实实现状态漂移 |

---

# 4. INT-001 — Capability Catalog 必须只有一个当前运行时真相

## 4.1 当前问题

Phase 2.1 已经有：

~~~text
AppRuntime
├─ RuntimeAssembly
├─ EffectiveConfig
└─ CapabilityCatalog
~~~

其中 Catalog 来自当前用户配置后的 Effective Registry：

- External Plugin Directories；
- Disabled Plugin IDs；
- Runtime Rescan；
- 当前 Permission / Availability。

但当前 `AppController.open_workspace()` 创建：

~~~python
Workspace(raw_path)
~~~

没有传入：

~~~python
extension_catalog=self.app_runtime.catalog
~~~

Workspace 因此会退回：

~~~text
get_default_catalog()
        ↓
default Runtime
~~~

形成两个能力事实源：

~~~text
Plugin Manager
      ↓
AppRuntime Registry / Catalog

Workspace
      ↓
Default Runtime Registry / Catalog
~~~

这违反：

> **Current Runtime Capability Registry / Catalog 是文件能力的单一真相。**

---

## 4.2 修复要求

Desktop / Application 路径创建 Workspace 时必须显式使用当前 AppRuntime Catalog：

~~~python
Workspace(
    raw_path,
    extension_catalog=self.app_runtime.catalog,
)
~~~

不得依赖全局 Default Catalog。

---

## 4.3 Runtime Rescan

当：

- Plugin Enable / Disable；
- External Plugin Directory 变化；
- Rescan；

导致 AppRuntime 重建时，如果已有 Workspace 打开，必须明确处理 Workspace 与新 Catalog 的关系。

推荐二选一：

### 方案 A

重新创建当前 Workspace：

~~~text
old workspace root
      ↓
new Workspace(root, new catalog)
      ↓
refresh refs
~~~

### 方案 B

Workspace 提供显式：

~~~python
workspace.with_catalog(...)
~~~

V0.1 推荐方案 A，保持 Workspace 不可变倾向。

---

## 4.4 验收

### T-001A External Extension

安装新的：

~~~text
.foo
~~~

Plugin。

不修改 Core：

~~~text
Plugin Manager = Enabled
Workspace = 能发现 .foo
ArtifactReader = 能读取 .foo
~~~

---

### T-001B Disable

禁用唯一 `.foo` Provider 后：

~~~text
Plugin Manager = Disabled
Workspace = 不再把 .foo 作为可读 Artifact 展示
~~~

如通过用户显式文件选择尝试读取，应仍得到：

~~~text
CapabilityDisabledError
~~~

而不是 Unsupported。

---

### T-001C Rescan

当前 Workspace 已打开时执行 Rescan，新能力集合必须立即与 Workspace 文件列表一致。

---

# 5. INT-002 — 真实 LLM QA 路径必须初始化 ContextPolicy

## 5.1 当前问题

`BaseLLMClient.__init__()` 初始化：

~~~python
self.context_policy
~~~

`BaseLLMClient.ask()` 必须使用该字段。

但当前：

~~~python
OpenAICompatibleClient.__init__()
~~~

没有调用：

~~~python
super().__init__()
~~~

因此真实 Desktop QA：

~~~text
OpenAICompatibleClient
→ ask()
→ build_context(... self.context_policy ...)
~~~

可能抛：

~~~text
AttributeError: context_policy
~~~

Mock LLM 正常，是因为 Mock 构造函数调用了 Base 初始化。

---

## 5.2 修复要求

OpenAICompatibleClient 必须：

~~~python
super().__init__(context_policy=context_policy)
~~~

并允许可选注入：

~~~python
context_policy: ContextPolicy | None = None
~~~

不得在 OpenAICompatibleClient 中重新复制 Context Budget 逻辑。

---

## 5.3 测试要求

不能只测试 MockLLMClient。

新增：

~~~text
Fake OpenAI-compatible HTTP endpoint
~~~

或 monkeypatch `urlopen` 的协议级测试。

验证：

1. `ask()` 可正常运行；
2. 默认 ContextPolicy 生效；
3. 超大 Artifact 有截断；
4. HTTP Payload 中包含 System Prompt + Context + Question；
5. 不访问真实互联网。

---

# 6. INT-003 — EffectiveConfig 必须区分“未配置”与合法 False / 0

## 6.1 当前问题

当前通用 resolve 逻辑使用类似：

~~~python
if user_value:
    USER
else:
    DEFAULT
~~~

这会错误处理：

~~~text
restore_last_workspace = False
recent_workspace_limit = 0
recent_activity_limit = 0
~~~

这些值都是合法配置，不代表“未设置”。

---

## 6.2 修复原则

配置解析必须区分：

~~~text
UNSET
vs
False
vs
0
vs
""
~~~

不能统一用 truthy / falsey 判断。

---

## 6.3 推荐设计

不同类型独立 resolver：

~~~text
resolve_string
resolve_bool
resolve_int
resolve_list
~~~

或者显式 sentinel：

~~~python
UNSET = object()
~~~

避免一个通用 helper 隐含类型语义。

---

## 6.4 验收

必须覆盖：

~~~text
restore_last_workspace=False
recent_workspace_limit=0
recent_activity_limit=0
~~~

最终：

~~~text
EffectiveValue.value = 用户显式值
EffectiveValue.source = User Config
~~~

不能回落 Default。

---

# 7. INT-004 — env 必须沿 Composition Root 完整传递

## 7.1 当前问题

`bootstrap_controller(..., env=...)` 已接收显式 env。

但 AppController 内部重新：

~~~python
resolve_effective_config(self.config)
~~~

可能再次读取 `os.environ`。

因此：

~~~text
bootstrap 指定 env
≠
实际整个 Application Runtime 使用的 env
~~~

---

## 7.2 修复要求

Application Composition Root 必须只解析一次显式 Environment Context。

推荐：

~~~python
AppController(
    ...,
    env=env,
    runtime_overrides=...
)
~~~

或者 bootstrap 直接计算：

~~~text
EffectiveConfig
~~~

并注入 Controller。

优先推荐：

> **EffectiveConfig 在 Composition Root 完成解析，Controller 消费已解析结果。**

这样：

~~~text
Config Resolution
~~~

不会在多个层重复发生。

---

## 7.3 验收

使用：

~~~python
bootstrap_controller(
    env={
        "HMBUDDY_LLM_MODEL": "...",
        "HMBUDDY_PLUGIN_PATH": "...",
    }
)
~~~

即使宿主 `os.environ` 没有这些值，最终：

- Settings Source；
- LLM Client；
- External Plugin Runtime；

都必须使用显式 env。

---

# 8. INT-005 — Plugin Unavailable 必须成为真实状态

## 8.1 当前问题

已定义：

~~~text
Enabled
Disabled
Load Failed
Incompatible
Unavailable
~~~

但当前 loaded Provider 即使：

~~~text
availability_reason != ""
~~~

仍创建：

~~~text
status = Enabled
~~~

UI 只是附加：

~~~text
已启用（不可用：...）
~~~

这使状态 Contract 与实现不一致。

---

## 8.2 修复要求

如果 Provider / Plugin 已成功加载，但当前环境不可执行：

~~~text
status = Unavailable
~~~

例如：

- platform 不匹配；
- Python constraint；
- optional dependency 缺失；
- runtime dependency probe 失败。

---

## 8.3 Plugin-level 聚合

因为 INT-010 要求 PluginView 聚合，最终 Plugin status 应基于 Providers 综合：

### Enabled

至少一个 Provider 当前可用。

### Unavailable

Plugin 成功加载，但没有任何 Provider 当前可用。

### Disabled

配置禁用。

### Incompatible

Manifest / API / runtime contract 不兼容。

### Load Failed

代码加载失败。

---

# 9. INT-006 — Recent Activity 选择必须使用稳定映射

## 9.1 当前问题

Recent Workspace Treeview 明确指定：

~~~python
iid=str(index)
~~~

Recent Activity Treeview 未指定 iid。

但打开逻辑使用：

~~~python
entries[int(selected[0])]
~~~

Tk 自动 iid 可能是：

~~~text
I001
I002
~~~

因此真实 GUI 路径可能无法恢复活动。

---

## 9.2 修复要求

禁止 UI 依赖“Treeview iid 恰好等于 list index”的隐式约定。

推荐：

~~~text
iid = entry.entry_id
~~~

并维护：

~~~python
activity_by_id
~~~

或通过 Presenter / ViewModel 显式映射。

Recent Workspace 同样建议逐步使用：

~~~text
workspace_id
~~~

而不是 index。

---

## 9.3 验收

至少新增轻量 GUI / Widget-level Test：

~~~text
render activity
select row
invoke open_selected_activity
→ 正确打开 workspace/artifact
~~~

不需要引入完整 UI 自动化框架。

---

# 10. INT-007 — Workspace Identity 必须统一

## 10.1 当前问题

Core Workspace 使用稳定：

~~~text
make_workspace_id(root)
~~~

但 RecentWorkspace 目前使用随机：

~~~text
uuid
~~~

因此同一个真实 Workspace 同时存在：

~~~text
Core Workspace ID
Recent Workspace ID
~~~

未来 Session 需要：

~~~text
session.workspace_id
~~~

时会产生身份歧义。

---

## 10.2 修复要求

RecentWorkspace 必须使用与 Core Workspace 相同的稳定 Workspace ID。

推荐直接复用：

~~~python
make_workspace_id(Path)
~~~

禁止在 Application 层复制第二套 hash 算法。

---

## 10.3 兼容已有 State

读取旧 state.json 时：

- 如果 workspace_id 缺失；
- 或明显是旧随机 ID；

允许在下次加载 / 保存时根据 path 重新计算。

不要求保留旧随机 ID 语义。

---

## 10.4 验收

同一路径：

~~~text
Workspace.workspace_id
=
RecentWorkspace.workspace_id
~~~

跨重启保持一致。

---

# 11. INT-008 — 正式定义 CI 平台契约

## 11.1 当前事实

基线提交 `161114c` 的 GitHub Actions：

~~~text
Windows Python 3.10  PASS
Windows Python 3.12  PASS
Wheel install smoke  PASS

Ubuntu Python 3.10   FAIL
Ubuntu Python 3.12   FAIL
~~~

Linux 失败主要包括：

1. 测试使用 Windows 路径语义；
2. `.doc` 已声明 Windows-only，但旧 eval 仍期待进入 COM / Parse 路径。

---

## 11.2 产品平台定位

HMBuddy V0.x 正式定义：

> **Windows-first Product, Cross-platform Core where applicable.**

原因：

- 目标企业桌面环境以 Windows 为主；
- WPS / Office COM 属于核心企业办公能力之一；
- Tk Desktop 当前主要面向 Windows；
- Artifact / Plugin Runtime 中大量能力本身仍具备跨平台价值。

---

## 11.3 CI 分层

### Windows Full Suite

~~~text
Python 3.10
Python 3.12
~~~

执行全部：

~~~text
tests
evals
desktop smoke
legacy office contract
~~~

---

### Linux Cross-platform Suite

执行：

- Artifact model；
- DOCX；
- PDF；
- XLSX；
- PPTX；
- Text；
- Plugin Runtime；
- Config / State；
- non-COM Desktop Controller；
- wheel install。

明确跳过或按平台重写：

- .doc COM execution；
- Windows path identity tests；
- Windows-specific UI/COM assumptions。

---

## 11.4 测试必须平台中立

如果测试要验证：

> Windows path comparison case-insensitive

应：

- 在 Windows 执行；
- 或 mock / unit-test Windows-specific normalizer。

不能在 Linux 使用：

~~~text
D:/ws/a
D:/ws/A
~~~

然后要求 Windows 行为。

---

## 11.5 验收

最终 GitHub Actions：

~~~text
all jobs green
~~~

baseline 中必须记录 CI run。

---

# 12. INT-009 — File Picker 必须来自 Capability Catalog

## 12.1 当前问题

Home / Workspace 的文件选择器仍硬编码：

~~~text
*.docx
*.pdf
*.xlsx
*.xls
*.pptx
*.doc
*.txt
*.md
*.csv
~~~

这与：

~~~text
CapabilityCatalog
~~~

动态扩展模型不一致。

---

## 12.2 修复要求

Product Layer 应从当前：

~~~text
self.app_runtime.catalog.artifact_extensions()
~~~

动态生成：

~~~text
支持的文件
~~~

filter。

必须保留：

~~~text
所有文件 (*.*)
~~~

作为用户显式兜底。

---

## 12.3 验收

安装 `.foo` Plugin 后：

~~~text
Plugin Manager
Workspace Discovery
File Picker
~~~

三处都识别 `.foo`。

---

# 13. INT-010 — Plugin Product View 必须按 Plugin 聚合，而不是按 Provider 重复行

## 13.1 当前问题

当前 loaded plugin：

~~~python
for provider in loaded.providers:
    views.append(PluginView(...))
~~~

一个 Plugin 如果包含多个 Provider，会产生多行相同 plugin_id。

当前内置插件大部分是一插件一 Provider，因此暂时不明显。

后续：

~~~text
artifact.read.full
artifact.read.range
artifact.create
artifact.patch
artifact.validate
~~~

进入后问题会立即放大。

---

## 13.2 修复要求

Plugin Manager 的一等对象必须是：

~~~text
Plugin
~~~

建议：

~~~text
PluginView
├─ plugin_id
├─ name
├─ version
├─ source
├─ status
├─ extensions
├─ capabilities
├─ declared_permissions
├─ effective_permissions
├─ providers
│  ├─ provider_id
│  ├─ capabilities
│  ├─ priority
│  └─ availability
└─ errors
~~~

UI 主表：

> 一 Plugin 一行。

Provider 信息放详情区域。

---

## 13.3 聚合规则

集合字段：

~~~text
extensions = union
capabilities = union
permissions = union
~~~

Provider 顺序保持 Registry / Manifest 的确定性排序。

---

# 14. INT-011 — Recent QA Activity 不默认持久化问题正文

## 14.1 当前问题

当前：

~~~python
title=f"问答：{question[:40]}"
~~~

会将用户问题前 40 字写入：

~~~text
state.json
~~~

企业内网问题文本可能直接包含：

- 客户名；
- 金额；
- 项目名；
- 风险事项；
- 内部制度信息。

Recent Activity 的导航价值并不依赖问题正文。

---

## 14.2 修复要求

默认标题改为不包含问题内容，例如：

~~~text
文档问答 · <artifact name>
~~~

或：

~~~text
问答 · <artifact name>
~~~

V0.1 不增加“保存问题标题”配置项。

---

## 14.3 验收

State JSON 中不得出现测试问题文本。

---

# 15. INT-012 — Canonical Architecture 必须在实现完成后升级至 V0.2

本项在 Phase 2.1.1 实现完成后执行。

不在规格提交阶段提前修改架构事实。

---

## 15.1 更新内容

`hmbuddy-architecture-baseline.md`：

~~~text
V0.1
→
V0.2
~~~

属于：

> Compatible Evolution / Clarification

---

## 15.2 至少更新

### Current State

Phase 2.1：

~~~text
需求阶段
→
已完成
~~~

### Recent

~~~text
Recent Task
→
Recent Activity
~~~

### Roadmap

~~~text
Stage A Desktop Application Foundation
→ Completed

Next
→ Minimal Agent Kernel
~~~

### Phase 2.1.1

记录 Integration Hardening 已完成，不改变六个 Kernel Primitive。

---

# 16. 额外实现约束

## C1. 不新增 Agent Kernel

禁止新增：

~~~text
Session
AgentLoop
ToolRegistry
ExtensionHost
TaskEngine
Planner
WorkflowGraph
~~~

---

## C2. 不重写 File Capability Runtime

Phase 2.1.1 只修 Application / Runtime Integration。

除非解决明确 bug，不重构：

- Registry；
- Router；
- Provider；
- Adapter。

---

## C3. 单一能力事实

以下 Product View 必须基于同一个当前 AppRuntime：

~~~text
Plugin Manager
Workspace Discovery
File Picker
ArtifactReader
System Status
~~~

不得分别调用不同 Default Runtime。

---

## C4. 单一 Workspace Identity

所有 Product / Application / Future Session 都必须复用 Core Workspace ID。

---

## C5. 不用测试迁就 Bug

CI 收口时不能简单：

~~~text
skip all Linux
~~~

也不能为了测试通过撤销：

~~~text
.doc Windows-only
~~~

必须让测试契约匹配真实平台边界。

---

# 17. 推荐模块改动范围

预计主要涉及：

~~~text
application/
├─ config.py
├─ state.py
└─ plugins.py

desktop/
├─ controller.py
└─ pages/
   ├─ home.py
   ├─ workspace.py
   └─ plugins.py

llm/
└─ client.py

tests/
evals/
.github/workflows/ci.yml

requirements/
├─ hmbuddy-architecture-baseline.md   # 实现完成后升 V0.2
└─ README.md
~~~

Workspace Core 原则上只复用现有接口，不新增新 Primitive。

---

# 18. 测试策略

## T1 Catalog Single Truth

External `.foo`：

~~~text
enable
→ Plugin Manager / Workspace / Picker 全部出现

disable
→ 三处全部消失或明确 Disabled
~~~

---

## T2 LLM Real Client Ask

构造 Fake OpenAI-compatible endpoint：

~~~text
OpenAICompatibleClient.ask()
→ no AttributeError
→ default ContextPolicy active
~~~

---

## T3 False / Zero Config

验证：

~~~text
False
0
~~~

均保留 User Config Source。

---

## T4 Environment Propagation

显式 bootstrap env 与宿主 os.environ 不一致时，以显式 env 为准。

---

## T5 Plugin Status

Unavailable Plugin：

~~~text
PluginView.status == Unavailable
~~~

---

## T6 Recent Activity UI Mapping

使用 entry_id 选择后能够准确恢复。

---

## T7 Workspace Identity

Core Workspace 与 RecentWorkspace ID 一致且跨重启稳定。

---

## T8 Platform CI Contract

Windows Full Suite + Linux Cross-platform Suite 均绿。

---

## T9 Dynamic Picker

新增扩展名自动进入 picker filter。

---

## T10 Multi-provider Plugin View

构造一个 Plugin：

~~~text
Provider A
Provider B
~~~

Plugin Manager 只展示一行，详情有两个 Provider。

---

## T11 QA Privacy

问题：

~~~text
客户A拟申请3亿元授信，风险如何？
~~~

不得出现在 state.json。

---

## T12 Architecture Guard

继续扫描：

~~~text
application/
desktop/
~~~

禁止新增 Agent Kernel Primitive。

---

# 19. 验收标准

## AC-I01 Runtime Catalog 单一真相

Workspace / Picker / Plugin Manager / ArtifactReader 基于同一 AppRuntime 能力集合。

---

## AC-I02 Rescan 一致

Plugin Rescan 后已打开 Workspace 的可见文件集合同步变化。

---

## AC-I03 Real LLM QA 可运行

OpenAICompatibleClient 的 `ask()` 真实代码路径通过 fake endpoint 集成测试。

---

## AC-I04 Context Budget 保持有效

修复 LLM Client 后不能破坏 Phase 1.1.1 的默认 ContextPolicy。

---

## AC-I05 False / Zero 配置合法

Config Resolution 不使用 truthy 判断决定是否“已配置”。

---

## AC-I06 Explicit Environment 全链路有效

bootstrap 注入 env 后，Config / LLM / Plugins 都使用同一 Environment Context。

---

## AC-I07 Plugin Unavailable 状态真实

Unavailable 不再伪装为 Enabled。

---

## AC-I08 Recent Activity GUI 可恢复

双击 Recent Activity 可稳定进入对应 Workspace / Artifact。

---

## AC-I09 Workspace ID 唯一

Application State 不再维护随机的第二套 Workspace identity。

---

## AC-I10 CI 全绿

GitHub Actions 所有定义 Job 通过。

---

## AC-I11 Windows-first 契约明确

README / CI / tests 明确：

~~~text
Windows-first Product
Cross-platform Core where applicable
~~~

---

## AC-I12 Dynamic File Picker

文件选择器与 CapabilityCatalog 同步。

---

## AC-I13 Plugin Product View 聚合

一 Plugin 一行，多 Provider 进入详情。

---

## AC-I14 QA Activity 默认不落问题正文

State 中无 Question 内容。

---

## AC-I15 无新增 Kernel Primitive

继续符合 Canonical Architecture V0.1。

---

## AC-I16 Architecture Baseline 更新

实现完成后：

~~~text
hmbuddy-architecture-baseline.md
V0.1 → V0.2
~~~

同步真实项目状态。

---

## AC-I17 Regression

Phase 1 / 1.1 / 1.1.1 / 2 / 2.1 全部有效回归继续通过。

---

# 20. 推荐实施顺序

## Step 1 — P0 Runtime Truth

先处理：

~~~text
INT-001 Catalog Single Truth
INT-002 LLM Client Initialization
~~~

这两个直接影响真实用户功能。

---

## Step 2 — Configuration Contract

处理：

~~~text
INT-003 False / Zero
INT-004 env propagation
~~~

---

## Step 3 — Product State Consistency

处理：

~~~text
INT-006 Recent Activity mapping
INT-007 Workspace ID
INT-011 QA privacy
~~~

---

## Step 4 — Plugin Product Model

处理：

~~~text
INT-005 Unavailable
INT-010 multi-provider aggregation
~~~

---

## Step 5 — Dynamic Product UX

处理：

~~~text
INT-009 File Picker
~~~

---

## Step 6 — CI Contract

处理：

~~~text
INT-008
~~~

将 Windows-first / cross-platform-core 的边界落实进测试矩阵。

---

## Step 7 — Docs

CI 全绿后：

~~~text
Architecture V0.2
README
Requirements Index
baseline-phase2.1.1-v0.1.json
~~~

---

# 21. Baseline 要求

实现完成后新增：

~~~text
evals/baseline-phase2.1.1-v0.1.json
~~~

至少记录：

- base commit；
- Architecture Baseline；
- Windows full test result；
- Linux cross-platform result；
- wheel smoke；
- AC-I01 ~ AC-I17；
- known limitations。

不能只记录本地：

~~~text
pytest passed
~~~

必须记录 GitHub Actions 结果。

---

# 22. Phase 2.1.1 完成后的系统状态

完成后：

~~~text
Desktop Product Shell
        │
        ▼
Application Foundation
        │
        ▼
Single Effective Runtime
        │
  ┌─────┼─────────────┐
  ▼     ▼             ▼
Workspace  Plugin UI  File Picker
  │
  ▼
ArtifactReader
  │
  ▼
Capability Runtime
~~~

关键变化是：

> **所有产品入口看到同一个 Runtime。**

同时：

~~~text
Workspace identity
Config environment
Plugin status
LLM ContextPolicy
~~~

都只有一套明确 Contract。

---

# 23. 进入下一阶段的门槛

Phase 2.1.1 完成且 CI 全绿后，才进入：

> **Minimal Agent Kernel**

下一阶段才允许新增：

~~~text
Session
SessionStore
AgentLoop
Tool
ToolRegistry
ExtensionHost
Hooks
~~~

仍然不默认加入：

~~~text
Planner
Memory
MCP
Automation
Multi-Agent
Workflow Graph
~~~

---

# 24. 阶段成功判断

Phase 2.1.1 成功不是看新增了多少代码。

只看：

1. **Desktop 和 Runtime 不再有两套 Capability 真相。**
2. **真实 LLM QA 路径不是只在 Mock 中成立。**
3. **Config 能准确表达用户显式 False / 0 与显式 env。**
4. **Workspace Identity 为未来 Session 提供唯一锚点。**
5. **Plugin Manager 能承受未来一个插件多个 Provider。**
6. **GitHub Actions 真实为绿，而不是只有本机 baseline 绿。**
7. **修复这些问题时没有提前长出 Agent Kernel。**

完成这些条件后，Phase 2.x 应停止继续扩展产品基础设施，正式进入 Minimal Agent Kernel。
