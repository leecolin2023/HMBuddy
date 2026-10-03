# HMBuddy 架构设计总纲 — WorkBuddy-like Product on a Pi-like Minimal Harness

**文档性质：** Canonical Architecture Baseline / 架构原文档  
**文档版本：** V0.2  
**状态：** Active  
**适用范围：** HMBuddy 后续所有产品设计、需求规格说明书、实现方案、重构与评审  
**首次形成基线：** 2026-10-02  
**形成时仓库基线：** `a0f154b74fbba4fb2a2d4e0d871aadb44fa56ead`  
**核心定位：** WorkBuddy-like Office Product on a Pi-like Minimal Harness, with an Artifact-native Office Runtime

---

## 1. 文档目的

本文档是 HMBuddy 的**长期架构总纲**，不是某一个 Phase 的一次性需求说明书。

后续所有 Phase、功能需求、重构、插件设计、Agent 能力、桌面产品功能，都应以本文档为默认架构基线。

本文档解决的核心问题不是：

> HMBuddy 下一阶段具体开发什么功能？

而是：

> **无论后续增加多少 WorkBuddy 式产品能力，HMBuddy 应该始终依赖哪些少量稳定原语？哪些能力必须留在 Kernel，哪些能力应该通过 Tool / Skill / Extension / Capability Plugin 组合出来？**

HMBuddy 的长期目标不是复刻 WorkBuddy 的内部架构，也不是机械复刻 Pi Agent。

目标是：

> **产品能力向 WorkBuddy 学习，Agent Harness 的架构哲学向 Pi Agent 学习，同时保留 HMBuddy 面向 Office 文件场景所必需的 Artifact-native 能力。**

---

# 2. 架构总原则

HMBuddy 同时坚持三条主线。

## 2.1 产品层：向 WorkBuddy 学习

产品最终应逐步具备用户能够感知的：

- Workspace；
- Task；
- Conversation；
- Results / Artifacts；
- Skills；
- Plugins；
- Automation；
- Connectors / MCP；
- Memory；
- Expert / Subagent；
- Settings；
- Approval；
- Resume；
- History。

这些是**产品功能目标**。

但它们不意味着底层必须存在一一对应的：

- TaskEngine；
- PlannerEngine；
- MemoryEngine；
- AutomationEngine；
- MultiAgentEngine；
- WorkflowEngine。

产品功能数量不应线性推高 Kernel 复杂度。

---

## 2.2 Harness 层：向 Pi Agent 学习

HMBuddy 应遵循：

> **Primitives, not features.**

Kernel 只提供少量稳定原语。

高级功能优先通过：

- Tool；
- Skill；
- Extension；
- Capability Plugin；
- 文件 / Session 数据；

组合实现。

在没有真实失败模式证明必要之前，不把以下概念固化为 Core：

- Planner；
- Workflow Graph；
- Todo Engine；
- Multi-Agent；
- MCP Runtime；
- Memory Engine；
- Automation Engine；
- Review Agent；
- Critic Agent；
- Supervisor Agent。

---

## 2.3 Office 领域：保留 Artifact-native 模型

HMBuddy 不能机械照搬 Coding Agent 的：

~~~text
read
write
edit
bash
~~~

Office 文件不是普通文本文件。

DOCX / XLSX / PPTX / PDF 内部存在：

- 标题层级；
- 段落；
- 表格；
- 合并单元格；
- 公式；
- Sheet；
- Slide；
- Shape；
- Page；
- Bounding Box；
- 格式定位；
- Office / WPS 原生对象。

因此 HMBuddy 保留：

~~~text
Artifact
ArtifactRef
ArtifactBlock
ArtifactLocator
ArtifactVersion（未来）
ArtifactPatch（未来）
~~~

作为 Office Agent 的领域核心。

这构成 HMBuddy 相对 Pi Agent 的主要领域差异。

---

# 3. 产品定位

HMBuddy 的产品定位统一为：

> **Local-first, File-centric, Artifact-native Office Agent Harness**

核心特征：

~~~text
Local-first
Offline-friendly
Workspace-native
Artifact-native
Plugin-native
Skill-driven
Human-controllable
Auditable
Enterprise-friendly
~~~

优先面向：

- 企业内网；
- 无互联网或受限联网环境；
- Office / WPS 文件工作流；
- 本地 Workspace；
- 长期维护同一工作成果；
- 可审计文件操作；
- Human-in-the-loop。

HMBuddy 不追求成为通用互联网 Agent 平台。

---

# 4. 架构分层

HMBuddy 目标架构分成四层：

~~~text
┌───────────────────────────────────────────────┐
│ Product Layer                                │
│ WorkBuddy-like UX                            │
│ Home / Workspace / Task / Results / Skills   │
│ Plugins / Automation / Settings / History    │
└───────────────────────┬───────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────┐
│ Minimal Agent Kernel                          │
│ Workspace / Artifact / Session / AgentLoop    │
│ ToolRegistry / ExtensionHost                  │
│ + Policy / Events / Context invariants        │
└───────────────────────┬───────────────────────┘
                        │
             ┌──────────┼───────────┐
             ▼          ▼           ▼
┌────────────────┐ ┌──────────┐ ┌──────────────┐
│ Tools          │ │ Skills   │ │ Extensions   │
└───────┬────────┘ └──────────┘ └───────┬──────┘
        │                                │
        ▼                                │
┌───────────────────────────────┐        │
│ File Capability Runtime       │        │
│ Capability / Provider /       │        │
│ Plugin / Adapter / COM / OCR  │        │
└───────────────────────────────┘        │
                                         ├─ Approval
                                         ├─ Memory
                                         ├─ MCP
                                         ├─ Plan
                                         ├─ Automation
                                         └─ Subagent
~~~

关键要求：

> **产品层可以很丰富，Kernel 必须长期保持小。**

---

# 5. HMBuddy Kernel：六个核心原语

除非后续有明确工程证据，否则 Kernel 原语控制在以下六类。

---

## 5.1 Workspace

Workspace 表达：

> Agent 被允许持续工作的本地工作环境。

Workspace 不等于“一个文件夹选择器”。

当前阶段主要包含：

- root boundary；
- workspace_id；
- ArtifactRef trust domain；
- file discovery；
- Capability Catalog；
- symlink / path boundary。

未来可自然扩展：

~~~text
Workspace
├─ Files
├─ Artifacts
├─ Sessions
├─ Skills
├─ Local Config
├─ Indexes
└─ History
~~~

但不要求一次性实现这些目录或数据库。

### Workspace Kernel Invariant

Workspace 必须始终负责：

1. 本地访问边界；
2. Artifact 的信任域；
3. 当前任务的工作范围；
4. 文件操作的安全作用域。

任何 Tool / Extension / Plugin 都不能绕过 Workspace Boundary。

---

## 5.2 Artifact

Artifact 表达：

> Agent 正在理解、创建、修改或交付的工作成果。

当前核心：

~~~text
ArtifactRef
Artifact
ArtifactBlock
ArtifactLocator
~~~

未来在真实写能力进入后扩展：

~~~text
ArtifactVersion
ArtifactPatch
ArtifactDiff
ValidationResult
~~~

Artifact 必须保持格式中立的顶层 Contract，同时允许格式特有结构。

### Artifact 原则

禁止把所有 Office 文件过早压成：

~~~text
string
~~~

或：

~~~text
markdown
~~~

Markdown / Text 只是面向 LLM 的一种 Representation，不是 Artifact 本身。

---

## 5.3 Session

Session 表达：

> 一次可持续、可恢复的 Agent 工作上下文。

这是未来 HMBuddy 持久任务能力的核心，而不是重型 Task Engine。

建议最小模型：

~~~text
Session
├─ session_id
├─ workspace_id
├─ title
├─ messages
├─ tool_calls
├─ artifact_refs
├─ metadata
├─ created_at
└─ updated_at
~~~

产品层可以把 Session 呈现为：

~~~text
Task
Conversation
Recent Task
History
Resume
~~~

但 Kernel 不因此必须拥有：

- TaskGraph；
- StepDependency；
- WorkflowStateMachine；
- Planner State；
- Execution DAG。

### 核心映射

> **Product Task = Session + Task Metadata**

只有真实需求证明需要稳定 Step Graph 时，才考虑增加更强 Task Contract。

---

## 5.4 AgentLoop

AgentLoop 是 Agent Kernel 中最小且最关键的执行原语。

基本形式：

~~~text
User / Session Context
        ↓
Model
        ↓
Tool Call?
   ┌────┴─────┐
   │          │
  No         Yes
   │          │
 Finish     Execute Tool
              ↓
          Observation
              ↓
            Session
              ↓
             Model
~~~

概念上保持：

~~~python
while session_active:
    response = model(messages, tools)

    if no_tool_call(response):
        finish()

    result = tools.execute(response.tool_call)
    session.append(result)
~~~

未来的：

- Approval；
- Steering；
- Context Injection；
- Compaction；
- Audit；
- Plan；
- Memory；

通过 Hook 进入循环，而不是不断把 AgentLoop 拆成新 Engine。

---

## 5.5 ToolRegistry

Tool 是**模型直接可调用的动作接口**。

Tool 与 Capability 必须严格区分。

### Tool 面向 Agent

例如：

~~~text
list_files
search_files
read_file
create_file
edit_file
validate_file
~~~

### Capability 面向 Runtime

例如：

~~~text
artifact.read.full
artifact.read.range
artifact.create
artifact.patch
artifact.validate
~~~

### Adapter / API / COM 面向实现

例如：

~~~text
python-docx
openpyxl
pdfplumber
WPS COM
Office COM
OCR
~~~

完整关系：

~~~text
Agent
  ↓
Tool
  ↓
Capability Runtime
  ↓
Provider
  ↓
Adapter / API / COM / OCR
~~~

Agent 不应知道具体 Provider。

---

## 5.6 ExtensionHost

ExtensionHost 是 HMBuddy 高级能力扩展面的统一入口。

首版应保持极简。

建议最小 API：

~~~python
register_tool(...)
register_hook(...)
register_skill(...)
~~~

Hook 初始只需要：

~~~text
session_start
before_model
after_model
before_tool
after_tool
session_end
~~~

通过这些 Hook，可以逐步实现：

### Approval

~~~text
before_tool
→ 判断 edit_file / delete / external_send
→ allow / ask / deny
~~~

### Audit

~~~text
after_tool
→ 写审计日志
~~~

### Memory

~~~text
before_model
→ 找相关历史
→ 注入 Context
~~~

### RAG

~~~text
before_model / Tool
→ search
→ inject
~~~

### MCP

~~~text
Extension
→ 动态注册 MCP Tools
~~~

### Plan Mode

~~~text
Extension / Skill
→ 生成和维护 PLAN.md / plan state
~~~

### Subagent

~~~text
Tool / Extension
→ 启动另一个 Session
~~~

---

# 6. Kernel Invariants：不是原语，但必须由 Core 保证

为了适应企业内网场景，HMBuddy 不完全复制 Pi 的最小安全假设。

以下属于 Kernel Invariants。

---

## 6.1 Policy

Core 至少支持：

~~~text
ALLOW
ASK
DENY
~~~

Policy 负责：

- Workspace Boundary；
- filesystem.read；
- filesystem.write；
- process.execute；
- network；
- office.com；
- wps.com；
- destructive operation。

但：

> “ASK 如何展示给用户”属于 Product / Extension 层。

---

## 6.2 Events

Kernel 应提供少量稳定事件。

事件的作用是让：

- UI；
- Audit；
- Approval；
- Metrics；
- Extensions；

不需要侵入 AgentLoop。

事件必须是简单的运行时事件，不建设复杂 Event Bus 平台。

---

## 6.3 Context

Context 负责：

> 当前一次模型调用到底看到什么。

来源可能包括：

- Session messages；
- Workspace 信息；
- Artifact 内容；
- Tool descriptions；
- Skill；
- Extension 注入信息；
- Memory；
- Search Result。

Context 必须继续遵守当前：

- Context Budget；
- Truncation 可观察；
- 不默认暴露绝对路径；
- LLM 不得误认为看到完整内容。

---

# 7. 当前 File Capability Runtime 的定位

Phase 1.1 / 1.1.1 已形成：

~~~text
Manifest
Discovery
Loader
Registry
Router
Permission
Availability
Capability Catalog
Trace
External Plugin
~~~

这一套必须保留。

但它的职责要严格限制为：

> **管理某项文件 / Artifact Capability 由哪个 Provider 实现。**

它不是整个 Agent 的 Plugin Framework。

未来不要把：

- Session；
- Memory；
- Planner；
- MCP；
- Automation；
- Subagent；

全部塞进 `plugin_runtime/`。

---

# 8. Capability Plugin 与 Extension 的区别

这是后续架构必须长期保持的边界。

## 8.1 Capability Plugin

目标：

> 提供某类 Artifact / File Capability 的实现。

例如：

~~~text
DOCX Plugin
PDF Plugin
XLSX Plugin
OCR Plugin
WPS COM Plugin
Financial Workbook Plugin
~~~

注册的是：

~~~text
artifact.read.*
artifact.create
artifact.patch
artifact.render
financial.statement.normalize
~~~

---

## 8.2 Extension

目标：

> 扩展 Agent Harness 的行为。

例如：

~~~text
Approval Extension
Memory Extension
MCP Extension
Automation Extension
Plan Extension
Subagent Extension
Audit Extension
~~~

Extension 可以：

- 注册 Tool；
- 注册 Hook；
- 注册 Skill；
- 增加 Context；
- 可选增加 UI。

---

## 8.3 两者关系

未来可以统一安装模型，但概念不能混。

~~~text
Extension Ecosystem
│
├─ Agent Extensions
│  ├─ approval
│  ├─ memory
│  ├─ mcp
│  └─ automation
│
└─ Capability Plugins
   ├─ docx
   ├─ pdf
   ├─ xlsx
   └─ wps
~~~

---

# 9. Skill：工作方法，不是程序状态机

Skill 解决：

> Agent 应该怎样完成一类工作。

Tool 解决：

> Agent 能做什么动作。

Plugin / Provider 解决：

> 动作具体怎么执行。

三者不能混。

---

## 9.1 推荐 Skill 结构

保持 Markdown-first：

~~~text
skill-name/
├─ SKILL.md
├─ references/
├─ scripts/
└─ templates/
~~~

`SKILL.md` 推荐包含：

~~~text
Name
Description
Trigger
Goal
Inputs
Procedure
Capabilities / Tools
Constraints
Validation
Examples
~~~

---

## 9.2 Progressive Disclosure

模型初始只看到：

~~~text
Skill Name
Description
~~~

需要时再读取：

~~~text
SKILL.md
~~~

只有执行中需要时才加载：

~~~text
references/
templates/
scripts/
~~~

避免所有 Skill 一次性进入 Context。

---

## 9.3 SenseWright 的定位

SenseWright 的：

- DeepRead；
- Review；
- Learning；
- Practice；

未来应优先作为 HMBuddy Skills 接入。

不应重写成：

- Python Workflow；
- Graph；
- Agent 子类；
- Planner 模块。

只有其中某一步确实需要确定性程序时，才配套 Script / Tool。

---

# 10. Planner 不是 Core

产品层可以展示：

~~~text
计划
步骤
执行进度
~~~

但 Kernel 不应默认建立：

~~~text
PlannerService
PlanRepository
PlanStepEngine
PlanExecutor
~~~

首版可以只是：

~~~text
Skill
+
Session metadata
+
PLAN.md
~~~

或模型直接维护简单结构：

~~~text
1. 找材料
2. 阅读
3. 生成
4. 校验
~~~

只有真实使用证明：

> 计划需要稳定结构、重排、暂停、依赖恢复

时，才将 Plan 提升为正式 Contract。

---

# 11. Task 不是 Core Engine

WorkBuddy 式产品一定会有 Task 页面。

但 HMBuddy 必须坚持：

> 产品上的 Task 不等于架构里的重型 TaskEngine。

第一阶段：

~~~text
Task UI
   ↓
Session Index
   ↓
Session Store
~~~

任务状态可以很简单：

~~~text
active
waiting_user
completed
failed
cancelled
~~~

不要提前建设：

- DAG；
- Job Queue；
- Workflow Orchestrator；
- Retry Scheduler；
- Step Database。

如果未来 Automation / Long-running Task 真的出现需要，再演进。

---

# 12. Artifact 写能力的目标架构

要走向 WorkBuddy 产品形态，HMBuddy 最关键的跃迁不是 Multi-Agent，而是：

> **从 read-only Artifact Runtime 进入可验证写入。**

必须优先形成：

~~~text
Artifact
   ↓
ArtifactPatch
   ↓
Capability Provider
   ↓
New Artifact Version
   ↓
Validate
   ↓
ArtifactDiff
~~~

---

## 12.1 不推荐

~~~python
update_docx(file, instruction)
~~~

这种过于黑盒的接口。

---

## 12.2 推荐

~~~text
ArtifactPatch
├─ artifact_id
├─ base_version
├─ operations
│  ├─ replace(locator)
│  ├─ insert(locator)
│  ├─ delete(locator)
│  ├─ update_cell(locator)
│  └─ ...
└─ metadata
~~~

当前 Phase 1.1.1 已引入 `ArtifactLocator`，未来写能力应直接复用，而不是另起一套定位模型。

---

# 13. WorkBuddy 产品功能如何映射到极简 Kernel

这是后续所有产品需求设计时必须优先参考的映射表。

| 产品功能 | 优先映射到 HMBuddy 原语 |
|---|---|
| Workspace | Workspace |
| Task | Session + metadata |
| Conversation | Session.messages |
| Results | Session.artifacts |
| Files | Workspace + Artifact |
| Resume | Reload Session |
| History | Session Store / Session Index |
| Planner | Skill / Extension |
| Tool Calling | AgentLoop + ToolRegistry |
| Skill | Markdown Skill |
| Plugins | Extension / Capability Plugin |
| Office 能力 | Capability Plugin |
| Approval | Policy + before_tool Hook |
| Diff | Artifact Tool / ArtifactDiff |
| Version | ArtifactVersion |
| Automation | Scheduler Extension → Start Session |
| Memory | before_model Context Extension |
| MCP | Extension → Register Tools |
| Expert | Session Profile + Skill |
| Multi-Agent | Tool / Extension → Spawn Session |
| RAG | Search Tool / Context Extension |
| Audit | Events / after_tool Hook |

核心判断标准：

> **新增产品功能时，优先寻找“现有原语的组合”，而不是新增 Kernel 模块。**

---

# 14. Tool 设计原则

HMBuddy 面向模型暴露的 Tool 数量必须保持少而稳定。

第一批 Office Primitive Tools 推荐：

~~~text
list_files
search_files
read_file
create_file
edit_file
validate_file
~~~

未来可以按真实需求加入：

~~~text
compare_files
move_file
copy_file
render_file
~~~

但不要把所有底层 Capability 直接暴露给模型。

例如：

~~~text
artifact.read.full
artifact.read.range
artifact.read.outline
~~~

可以由一个：

~~~text
read_file
~~~

Tool 根据参数内部选择。

---

# 15. 模型与程序的职责边界

继续坚持：

> LLM 负责语义不确定性，程序负责确定性约束。

---

## 15.1 LLM 负责

- 判断用户意图；
- 决定下一步需要什么 Tool；
- 决定阅读哪些材料；
- 综合多文件信息；
- 生成内容；
- 判断是否需要调用 Skill；
- 根据 Tool Result 调整下一步行动。

---

## 15.2 程序负责

- Workspace 边界；
- Plugin Discovery；
- Capability Routing；
- Permission；
- 文件定位；
- Patch 执行；
- Hash / Version；
- Validation；
- Session 持久化；
- Tool schema；
- Audit；
- Retry policy；
- Context budget。

---

# 16. Computer Use 的位置

HMBuddy 不采用“所有办公操作都 Computer Use”的架构。

优先级：

~~~text
Native File Structure
        ↓
Official / Local API
        ↓
Office / WPS COM
        ↓
MCP / Connector
        ↓
UI Automation
        ↓
Vision Computer Use
~~~

Computer Use 主要用于：

- 老 OA；
- 无开放 API 的客户端；
- 特殊企业系统；
- 必须通过 GUI 操作的流程。

文件处理本身优先走 Artifact / Capability Runtime。

---

# 17. MCP 的定位

MCP 不进入 Kernel。

MCP 解决：

> Agent 如何访问 Workspace 之外的系统。

例如未来：

~~~text
OA
邮件
知识库
信贷系统
内部搜索
数据库
审批系统
~~~

实现方式：

~~~text
MCP Extension
      ↓
discover tools
      ↓
register_tool(...)
      ↓
ToolRegistry
~~~

Kernel 只看到 Tool，不知道它来自 MCP。

---

# 18. Automation 的定位

Automation 不进入 AgentLoop Core。

本质是：

~~~text
Scheduler
    ↓
Create / Resume Session
    ↓
AgentLoop
~~~

例如：

~~~text
每天 08:30
    ↓
新建 Session
    ↓
执行日报 Skill
    ↓
生成 Artifact
~~~

因此 Automation 应优先作为 Extension。

---

# 19. Memory 的定位

Memory 不应一开始成为独立大型系统。

优先模型：

~~~text
before_model Hook
      ↓
retrieve relevant memory
      ↓
inject Context
~~~

Memory 的存储实现可以变化：

- Session summary；
- Local database；
- vector search；
- enterprise knowledge store。

AgentLoop 无需知道。

---

# 20. Multi-Agent 的定位

Multi-Agent 不是近期目标。

如果未来真实需求出现：

~~~text
主 Agent
   ↓
delegate()
   ↓
启动另一 Session
   ↓
返回结果
~~~

即可先实现。

不要提前建设：

- Supervisor Framework；
- Agent Network；
- A2A Platform；
- Agent Team Manager。

单 Agent 的：

~~~text
找材料
读材料
修改文件
验证成果
恢复 Session
~~~

闭环未完成前，不进入 Multi-Agent。

---

# 21. 产品 UI 与 Kernel 的关系

Product Layer 可以向 WorkBuddy 学习。

推荐未来 UI：

~~~text
Home
├─ Recent Workspaces
├─ Recent Tasks / Sessions
├─ System Status
└─ Quick Actions

Workspace
├─ Files
├─ Sessions / Tasks
├─ Artifacts / Results
└─ Skills

Task
├─ Conversation
├─ Tool Activity
├─ Artifacts
├─ Changes
└─ Approval

Plugins
Settings
Skills
Automation
~~~

但 UI 不得反向要求 Kernel 为每个页面增加独立 Engine。

---

# 22. 当前已完成能力与目标架构的映射

截至本文档 V0.1，HMBuddy 已经完成：

## Phase 1 / 1.1 / 1.1.1

~~~text
Workspace
Artifact
ArtifactBlock
ArtifactLocator
File Capability Runtime
Manifest
Discovery
Loader
Registry
Router
Policy
Availability
Capability Catalog
Trace
DOCX/PDF/XLSX/PPTX/XLS/DOC/TEXT
OCR
PDF Table
Context Budget
CI
~~~

这些全部保留。

---

## Phase 2

已经具备：

~~~text
Desktop Entry
Workspace selection
File list
Artifact preview
Document Q&A
Background task execution
~~~

---

## Phase 2.1

**已完成**（V0.2 起为真实实现状态）。

已交付：

~~~text
Home
Config（AppConfig / EffectiveConfig）
State（AppState）
Recent Workspace
Recent Activity（不建立 Task 域）
Plugin Manager
Settings
Desktop Shell 四页导航
~~~

实施约束已验证：

> Recent Activity 只做 UI 导航历史，不演变成 Task Engine；
> 未来 Minimal Agent Kernel 建立 Session 后，Agent 相关入口迁移为 Session Index（Product Task = Session + metadata）。

---

# 23. 推荐演进路线

本文档不锁死具体 Phase 编号，但推荐以下能力顺序。

---

## Stage A — Desktop Application Foundation

**已完成**（Phase 2.1 + Phase 2.1.1 Integration Hardening）。

已交付：

~~~text
Config
App State
Home
Recent Workspace
Recent Activity
Plugin Manager
Settings
~~~

目标达成：

> HMBuddy 已成为可持续使用、可配置、可恢复基本工作上下文的本地桌面应用（仍非 Agent Runtime）。

---

## Stage B — Minimal Agent Kernel

新增最小：

~~~text
Session
SessionStore
AgentLoop
Tool
ToolRegistry
ExtensionHost
Hooks
~~~

不加入：

- Planner；
- MCP；
- Memory；
- Multi-Agent；
- Workflow Graph。

---

## Stage C — Office Primitive Tools

建立少量：

~~~text
list_files
search_files
read_file
create_file
edit_file
validate_file
~~~

Tool 内部调用现有 Capability Runtime。

---

## Stage D — End-to-End Office Task

只用一个真实场景证明架构：

> 根据 Workspace 中多份材料生成一份 Office 文档，用户提出修改意见后继续修改同一成果，最终校验并交付。

链路：

~~~text
User Goal
   ↓
Session
   ↓
Workspace Search
   ↓
Partial Read
   ↓
AgentLoop
   ↓
Skill
   ↓
Create Artifact
   ↓
Validate
   ↓
User Feedback
   ↓
Artifact Patch
   ↓
New Version
   ↓
Diff
   ↓
Complete
~~~

完成这条链，才算真正进入 Office Agent。

---

## Stage E — Skills

正式接入：

- SenseWright DeepRead；
- Review；
- Learning；
- Practice；
- 公文起草；
- 财务分析；
- 制度分析。

Skill 保持 Markdown-first。

---

## Stage F — Extensions

根据真实需求依次引入：

~~~text
Approval
MCP
Automation
Memory
Plan
Subagent
~~~

不是一次性全部实现。

---

# 24. 架构评审问题

以后每次设计新需求时，必须先回答以下问题。

### Q1

这是**产品功能**，还是新的 **Kernel Primitive**？

默认答案应是产品功能。

---

### Q2

现有：

~~~text
Workspace
Artifact
Session
AgentLoop
Tool
Extension
~~~

能否组合实现？

如果可以，不新增 Core。

---

### Q3

它属于：

- Tool；
- Skill；
- Extension；
- Capability Plugin；

中的哪一类？

---

### Q4

为什么不能通过 Extension Hook 实现？

如果可以，不修改 AgentLoop。

---

### Q5

为什么不能通过 Tool 封装已有 Capability？

如果可以，不把 Capability 直接暴露给 Agent。

---

### Q6

新增抽象是否来自真实失败模式？

不能因为“成熟 Agent 应该有这个模块”就新增。

---

### Q7

是否破坏 Workspace / Policy / Artifact Contract？

如果破坏，需要明确 Architecture Change。

---

# 25. Kernel 变更门槛

以下变更属于高门槛 Architecture Change：

- 新增第七个 Kernel Primitive；
- 修改 Workspace 信任边界；
- 修改 Artifact 顶层 Contract；
- 修改 Session 持久化语义；
- 修改 AgentLoop 基本执行模型；
- 修改 Tool Contract；
- 修改 Extension Hook Contract；
- 将某个 Extension 能力升级为 Core。

任何此类变更必须在对应需求规格说明书中增加：

~~~text
Architecture Change
├─ Problem
├─ Why existing primitives are insufficient
├─ Alternatives
├─ Compatibility impact
├─ Migration
└─ Architecture document update
~~~

不得在实现代码中静默完成。

---

# 26. 后续需求规格说明书的强制结构

从本文档生效后，新的需求规格说明书必须增加：

## Architecture Alignment

至少回答：

~~~text
Architecture Baseline:
  hmbuddy-architecture-vX.Y

Product Capability:
  ...

Kernel Primitives Used:
  ...

Tools:
  ...

Skills:
  ...

Extensions:
  ...

Capability Plugins:
  ...

New Core Primitive:
  No / Yes

Architecture Deviation:
  None / ...
~~~

如果：

~~~text
New Core Primitive = Yes
~~~

必须按上一节执行架构变更评审。

---

# 27. 架构文档自身的迭代规则

本文档不是不可修改的“宪法”。

它必须随着真实工程经验持续演化。

但要区分：

## 27.1 Clarification

例如：

- 补充说明；
- 增加示例；
- 修正文案；
- 细化 Tool / Skill 边界。

更新：

~~~text
V0.1 → V0.2
~~~

可以直接更新 Canonical Document，并在 Change Log 记录。

---

## 27.2 Compatible Evolution

例如：

- 增加新的 Hook；
- ArtifactVersion 正式落地；
- Session metadata 扩展；
- Extension API 增加兼容字段。

更新 Minor Version。

---

## 27.3 Breaking Architecture Change

例如：

- Kernel 从 6 个原语增加到 7 个；
- Session 被 TaskEngine 替代；
- Capability Plugin 与 Extension 合并；
- Artifact Contract 重构；
- Workspace 安全边界变化。

需要：

1. 单独需求 / ADR；
2. 解释为什么原架构不足；
3. 给迁移方案；
4. 更新本文档 Major Version；
5. 明确旧规格受影响范围。

---

# 28. Canonical Document 管理规则

本文档作为**架构原文档**采用：

> **单一 Canonical 文件持续更新 + Git 历史保留演进过程。**

原则：

- 不为每次小改复制多个 architecture-v0.1-final-final2 文件；
- 当前文件始终代表最新有效架构；
- Git Commit 保留历史；
- 文档顶部维护当前版本；
- 文档底部维护 Change Log；
- Breaking Change 可额外增加 ADR。

后续 Phase 规格只引用当前架构版本，不复制整套架构正文。

---

# 29. 架构反模式

以下模式默认禁止。

## 29.1 Product Feature = Core Module

错误：

~~~text
产品新增 Memory
→ 新建 MemoryEngine 进入 Kernel

产品新增 Plan
→ 新建 PlannerEngine 进入 Kernel

产品新增 Automation
→ 新建 AutomationEngine 进入 Kernel
~~~

优先考虑 Extension / Tool / Skill。

---

## 29.2 每种文件一个 Agent Tool

错误：

~~~text
read_docx
read_pdf
read_xlsx
read_pptx
~~~

Agent 应优先看到：

~~~text
read_file
~~~

格式差异由 Capability Runtime 处理。

---

## 29.3 Adapter 直接暴露给 Agent

禁止：

~~~text
Agent → DocxAdapter
~~~

必须：

~~~text
Agent
→ Tool
→ Capability
→ Provider
→ Adapter
~~~

---

## 29.4 Skill 变成 Workflow Engine

Skill 首先是工作方法。

不要一开始编译成复杂 DAG。

---

## 29.5 Multi-Agent 解决单 Agent 没闭环的问题

如果单 Agent 还无法：

- search；
- read；
- create；
- edit；
- validate；
- resume；

则不引入 Multi-Agent。

---

## 29.6 所有办公操作都走 Computer Use

文件能力优先走结构化接口。

Computer Use 是 fallback，而不是主通路。

---

# 30. 架构成功判断标准

长期来看，如果 HMBuddy 新增 WorkBuddy 式产品功能时，大多数改动表现为：

~~~text
新增 Tool
或
新增 Skill
或
新增 Extension
或
新增 Capability Plugin
~~~

而：

~~~text
Kernel 基本不变
~~~

则说明本架构有效。

反之，如果每增加一个产品菜单都需要：

~~~text
新增 Engine
新增 Manager
新增 Runtime
修改 AgentLoop
修改 Workspace
~~~

说明架构正在走向过度平台化，需要重新收敛。

---

# 31. 一句话架构定义

HMBuddy 的长期架构定义为：

> **WorkBuddy-like Office Product on a Pi-like Minimal Harness, with a Local-first and Artifact-native Office Runtime.**

中文表达：

> **产品能力向 WorkBuddy 学习，Agent 内核采用 Pi 式极简原语，Office 文件处理采用 HMBuddy 自己的 Artifact-native Runtime；产品功能通过 Tool、Skill、Extension 和 Capability Plugin 组合演进，而不是不断扩张 Core。**

---

# 32. V0.1 Change Log

## V0.1 — 2026-10-02

首次形成 Canonical Architecture Baseline。

确立：

1. 产品功能向 WorkBuddy 学习；
2. Harness 架构哲学向 Pi Agent 学习；
3. HMBuddy 保留 Artifact-native Office Runtime；
4. Kernel 控制为 Workspace / Artifact / Session / AgentLoop / ToolRegistry / ExtensionHost 六个核心原语；
5. Policy / Events / Context 作为 Kernel Invariants；
6. File Capability Runtime 保留，但限定为文件能力 Provider Runtime；
7. Capability Plugin 与 Agent Extension 分层；
8. Skill 采用 Markdown-first / progressive disclosure；
9. Task 产品概念优先映射为 Session + metadata；
10. Planner / MCP / Memory / Automation / Multi-Agent 默认不进入 Core；
11. Artifact 写能力采用 Patch / Version / Diff 路线；
12. 后续需求规格说明书必须增加 Architecture Alignment；
13. 架构文档采用单一 Canonical 文件持续迭代，重大变更通过版本与 ADR 管理。

---

# 33. V0.2 Change Log

## V0.2 — 2026-10-02

Compatible Evolution / Clarification（Phase 2.1.1 完成后同步真实项目状态）。

更新：

1. **Current State**：Phase 2.1 由"需求阶段"更新为"已完成"；Recent Task 表述统一为 Recent Activity（产品上从未建立 Task 域）。
2. **Roadmap**：Stage A（Desktop Application Foundation）标记为已完成；下一阶段为 Minimal Agent Kernel。
3. **Phase 2.1.1**：记录 Desktop & Runtime Integration Hardening 已完成——Catalog/Config/Workspace 身份/Plugin 状态/LLM ContextPolicy 集成缝隙收口，六个 Kernel Primitive 不变。
