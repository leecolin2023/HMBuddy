# HMBuddy Architecture Baseline V1.0 — Pi-native Banking Office Agent

**文档性质：** Canonical Architecture Baseline / 架构原文档  
**文档版本：** V1.0  
**状态：** Active  
**生效日期：** 2026-10-03  
**取代版本：** V0.2 — WorkBuddy-like Product on a Pi-like Minimal Harness  
**迁移起点：** HMBuddy `main` @ `4d323326a7a33dc97d1fa0d2bfae4c6d9cb8d90e`  
**上游基线：** Pi / `@earendil-works/pi-coding-agent` 1.0.0（截至 2026-10-03）  
**核心定位：** A banking Office Agent distribution built directly on Pi, extending the upstream harness through Office capabilities, banking skills, enterprise governance, and bank-specific integrations.

---

## 1. 架构重置的原因

HMBuddy V0.2 的核心假设是：

> 学习 Pi 的极简思想，并在 HMBuddy 内自行实现 Workspace、Session、AgentLoop、ToolRegistry、ExtensionHost 等最小 Agent Kernel，再在其上建设 Office Agent。

该假设在当前阶段不再成立。

Pi 已经提供稳定且持续演进的 Agent Harness，包括 Agent / Session、SessionManager、模型运行时、Tool 生命周期、Context / Compaction、Extensions、Skills、ResourceLoader、事件、SDK、RPC、MCP、Codemode 等能力。HMBuddy 如果继续自行实现同类基础设施，将产生三个问题：

1. **重复工程投入**：大量资源用于通用 Agent 基础设施，而不是银行 Office 特性；
2. **持续落后上游**：Pi 的 Session、Context、Extension、Tool 等契约持续演进，自研实现难以同步；
3. **维护成本反转**：HMBuddy 会从银行办公 Agent 项目演变为通用 Agent Framework 维护项目。

因此 V1.0 做出架构重置：

> **HMBuddy 不再建设自己的通用 Agent Kernel。Pi 是 HMBuddy 的 Agent substrate；HMBuddy 只拥有银行 Office 领域能力、企业治理和产品体验。**

本次重置允许大面积放弃现有实现。旧代码不是兼容性负担，只有经 V1.0 重新证明仍有领域价值的能力才迁移。

---

# 2. Canonical Definition

HMBuddy 的长期定义统一为：

> **Pi-native Banking Office Agent**

展开为：

- **Pi-native**：Agent 生命周期、Session、Tool、Context、Model、Extension、Skill 等通用能力直接依赖 Pi；
- **Banking**：适配银行内网、权限、审计、敏感数据、内网模型和内部系统；
- **Office**：重点处理 DOCX / XLSX / PPTX / PDF / OCR / WPS / Office COM 等办公对象；
- **Agent Distribution**：HMBuddy 是一套 Pi 上的产品化发行与领域能力集合，不是一个新的 Agent Framework。

---

# 3. 第一原则

## 3.1 Upstream First

任何通用 Agent 能力，优先使用 Pi 上游实现。

新增代码前必须先回答：

> Pi 是否已经提供该能力、扩展点或等价组合？

如果答案是“是”，HMBuddy 默认不实现第二套。

适用范围包括但不限于：

- Session；
- Agent Loop；
- Tool execution；
- Model abstraction；
- Context / Compaction；
- Skills discovery；
- Extension lifecycle；
- MCP；
- Codemode；
- Session persistence；
- Resource discovery；
- Agent events；
- Prompt / context resource loading。

当 Pi 新增与 HMBuddy 自研能力重叠的功能时，默认方向不是“再做一层适配”，而是：

> **评估是否可以删除 HMBuddy 的重复实现。**

---

## 3.2 No Fork by Default

HMBuddy 默认：

- 不 Fork Pi 作为长期主线；
- 不复制 Pi 源码进入 HMBuddy；
- 不直接修改 Pi 内部实现；
- 不维护 HMBuddy 专属 Pi 分支。

优先使用：

1. Pi TypeScript SDK；
2. Pi Extension API；
3. Pi Skills；
4. Pi Package；
5. Pi RPC / CLI Integration；
6. 上游公开 Contract。

只有公开扩展面无法满足一个**经过真实场景证明的银行级要求**时，才允许提出 Fork / Patch Pi 的架构变更。

Fork Pi 属于高门槛 Architecture Change，必须有 ADR。

---

## 3.3 Thin Integration

HMBuddy 与 Pi 的耦合必须集中在极薄的一层。

禁止出现 Office、Bank Skill、业务代码到处直接依赖 Pi 内部 API 的情况。

目标依赖方向：

~~~text
Pi
 ↓
HMBuddy Pi Integration
 ↓
HMBuddy Domain
 ↓
Office Runtime / Bank Integration
~~~

Pi breaking change 应尽可能只影响 integration layer。

---

## 3.4 Domain over Framework

HMBuddy 的工程资源优先投入以下领域：

- Office 结构化读取；
- Office 高质量生成和修改；
- Artifact 定位；
- Patch；
- Version；
- Diff；
- Validation；
- WPS / Office COM；
- OCR；
- 财务报表；
- 制度 / 公文 / 授信等银行 Skills；
- 内网治理；
- 内部系统集成。

不再以“通用 Agent 功能完整度”为项目目标。

---

## 3.5 Migration by Capability, Not by Directory

V0.2 代码不做整体搬迁。

禁止：

~~~text
cp -r workspace/
cp -r plugin_runtime/
cp -r desktop/
~~~

进入 VNext。

迁移单位必须是“经过重新证明的能力”。

例如：

- PDF 跨页表格解析有价值 → 可迁移算法与测试；
- ArtifactLocator 有真实 Office 编辑价值 → 重新纳入；
- 通用 Plugin Runtime 与 Pi Extensions 重叠 → 不迁移；
- 自研 LLM Client 与 Pi Model Runtime 重叠 → 不迁移。

---

# 4. Ownership Boundary

V1.0 最重要的架构约束不是模块数量，而是所有权。

## 4.1 Pi Owns

以下能力默认属于 Pi，上游为事实来源：

~~~text
Agent lifecycle
Agent loop
Session
Session persistence / SessionManager
Conversation context
Context reconstruction
Compaction
Model runtime
Provider abstraction
Tool registration and execution
Tool lifecycle events
Resource discovery
Extensions
Skills discovery
Prompt resources
MCP
Codemode
Agent events
CLI / TUI base behavior
SDK / RPC integration contracts
~~~

HMBuddy 不建设平行实现。

---

## 4.2 HMBuddy Owns

以下是 HMBuddy 应长期拥有的差异化资产：

~~~text
Office Artifact domain
DOCX / XLSX / PPTX / PDF capabilities
OCR
WPS / Office COM integration
Artifact Locator / Patch / Version / Diff
Office validation
Banking skills
Banking policy
Audit requirements
Sensitive-data handling
Bank internal integrations
Bank-specific product UX
Office-specific eval corpus
~~~

---

## 4.3 Do Not Own

以下能力除非有新的 ADR，否则 HMBuddy 明确不拥有：

~~~text
Generic Agent Kernel
Generic Session Framework
Generic Tool Registry
Generic Model Runtime
Generic Context Manager
Generic Plugin Framework
Generic Skill Runtime
Generic MCP Runtime
Generic Planner
Generic Memory Framework
Generic Multi-Agent Framework
Generic Workflow / DAG Engine
Generic Task Engine
~~~

---

# 5. Target Architecture

~~~text
                         HMBuddy
                            │
                ┌───────────┴───────────┐
                │                       │
        Banking Product Layer      Banking Skills
                │                       │
                └───────────┬───────────┘
                            │
                  HMBuddy Pi Integration
                            │
╔═══════════════════════════╪═══════════════════════════╗
║                           PI                          ║
║                                                       ║
║ Agent / Session / Context / Model Runtime             ║
║ Tools / Extensions / Skills / Resources               ║
║ Compaction / Events / MCP / Codemode / RPC / SDK      ║
╚═══════════════════════════╪═══════════════════════════╝
                            │
                    Office Tool Bridge
                            │
                ┌───────────┴───────────┐
                │                       │
        Python Office Runtime      Bank Integrations
                │                       │
  DOCX / XLSX / PPTX / PDF      OA / WPS / Internal API
  OCR / COM / Patch / Diff
  Validation / Rendering
~~~

---

# 6. Runtime Split

## 6.1 TypeScript Host

V1.0 默认采用：

> **TypeScript as the Pi-native host.**

原因不是语言偏好，而是 Pi 的一等集成接口是 TypeScript SDK。

TypeScript Host 负责：

- 创建 / 管理 Pi AgentSession；
- 装配模型与 Session；
- 注册 HMBuddy Extensions；
- 注册 Office Tools；
- 加载 HMBuddy Skills；
- 订阅 Pi lifecycle events；
- 处理银行级 Approval / Audit / Policy；
- 连接 Product UI。

HMBuddy 不在 TypeScript Host 中重新实现 AgentLoop。

---

## 6.2 Python Office Runtime

Python 继续承担最适合 Python 生态的 Office 工程能力：

- python-docx；
- openpyxl；
- PDF parsing；
- OCR；
- win32com；
- WPS / Office COM；
- 表格处理；
- 文档结构识别；
- Office 文件验证。

Python Runtime 不理解：

- Session；
- AgentLoop；
- Prompt；
- Model；
- Memory；
- Planner。

它只理解 Office Domain。

---

## 6.3 Process Boundary

TypeScript Host 与 Python Office Runtime 通过稳定的 Office Capability Protocol 通信。

首选实现：

> **local subprocess + stdio JSONL / JSON-RPC-like protocol**

原因：

- 无需额外端口；
- 适合企业内网和离线环境；
- Python 与 TypeScript 生命周期解耦；
- 易于调试；
- 易于独立测试；
- 后续可替换为 named pipe / local socket 而不影响上层 Tool Contract。

初始协议只需要：

~~~text
capabilities
inspect
read
search
create
patch
validate
compare
render
~~~

具体 transport 不是领域 Contract。

---

# 7. Office Domain Model

Artifact 不再属于“通用 Agent Kernel”。

V1.0 将其重新定义为：

> **Office Domain Model**

推荐逐步形成：

~~~text
Artifact
ArtifactBlock
ArtifactLocator
ArtifactVersion
ArtifactPatch
ArtifactDiff
ValidationResult
~~~

原则：

1. Artifact 保留 Office 原生结构；
2. 不把 DOCX / XLSX / PPTX 过早压成纯 Markdown；
3. Tool Result 可以生成面向模型的 representation；
4. Office Runtime 内部保留更丰富的结构事实；
5. Locator / Patch / Diff 必须服务真实编辑场景，不提前设计万能 DSL。

---

# 8. Agent-facing Office Tools

模型看到的 Office Tools 必须少而稳定。

推荐初始 Tool 面：

~~~text
read_office_file
search_office_content
create_office_file
edit_office_file
validate_office_file
compare_office_files
~~~

不要直接暴露：

~~~text
read_docx
read_xlsx
read_pdf
read_pptx
docx_replace_paragraph
xlsx_write_cell
...
~~~

格式差异由 Office Runtime 吸收。

关系：

~~~text
Pi Agent
  ↓
Pi Tool
  ↓
HMBuddy Office Bridge
  ↓
Office Capability
  ↓
Python implementation
~~~

---

# 9. Skills

HMBuddy 不实现自己的 Skill Runtime。

Bank Skills 直接遵循 Pi / Agent Skills 生态的 Skill 形式。

例如：

~~~text
skills/
├─ financial-analysis/
│  └─ SKILL.md
├─ regulation-review/
│  └─ SKILL.md
├─ document-drafting/
│  └─ SKILL.md
└─ sensewright/
   ├─ deep-read/
   ├─ review/
   ├─ learning/
   └─ practice/
~~~

Skill 负责：

> Agent 应该如何完成一类工作。

Tool 负责：

> Agent 能做什么动作。

Office Runtime 负责：

> 动作如何可靠落到文件上。

三者长期保持分离。

---

# 10. Banking Governance

Pi 官方明确说明：其 working directory、project trust 和 transcript review 不是完整安全边界；默认工具与扩展拥有启动 Pi 的操作系统用户权限。

因此银行级安全治理属于 HMBuddy 需要补充的领域能力。

V1.0 的最低治理原则：

## 10.1 External Network Default Deny

除：

- 内网模型 endpoint；
- 明确审批的内部系统；
- 允许的 MCP / API；

之外，不默认开放外部网络。

---

## 10.2 Path Scope

HMBuddy 必须对 Pi 可作用的 Office 工作目录做显式边界控制。

`cwd` 是工作上下文，不等于安全边界。

真正的安全应依赖：

- OS account；
- sandbox / container；
- filesystem ACL；
- extension policy；
- process isolation。

---

## 10.3 Approval

对以下动作至少支持 ASK / DENY：

- destructive file mutation；
- overwrite；
- delete；
- external send；
- process execute；
- network access；
- COM automation；
- sensitive-system write。

优先使用 Pi Extension 的 tool lifecycle 事件实现，而不是建立第二个 Tool Runtime。

---

## 10.4 Audit

审计至少记录：

~~~text
session
tool
arguments summary
target resource
decision
result
timestamp
artifact version/diff when applicable
~~~

审计是企业治理能力，不要求侵入 Pi AgentLoop。

---

# 11. Configuration Authority

V0.2 的 AppConfig / EffectiveConfig 不再默认作为 VNext 架构资产。

V1.0 配置分为两类：

## Pi-owned Configuration

由 Pi 负责：

- models；
- providers；
- sessions；
- extensions；
- skills；
- resources；
- MCP；
- Pi runtime settings。

## HMBuddy-owned Configuration

仅保留：

- Office Runtime；
- bank policy；
- internal endpoints；
- audit；
- approved roots；
- product-specific settings。

禁止复制 Pi 配置形成第二份“事实来源”。

---

# 12. Session / Task / Memory / Planner

## 12.1 Session

Pi SessionManager 是唯一 Session Authority。

HMBuddy 不再实现：

~~~text
HMBuddySession
SessionStore
SessionIndex
~~~

除非出现 Pi Session Contract 无法表达且经真实场景证明的需求。

---

## 12.2 Product Task

产品上可以叫：

- Task；
- Conversation；
- History；
- Resume。

但默认映射到 Pi Session / durable primitives。

不要因为 UI 有 Task 就建设 TaskEngine。

---

## 12.3 Memory

优先采用：

- Pi Session；
- Pi Extension；
- Pi ecosystem package；
- 外部企业知识存储。

不提前建立 HMBuddy MemoryEngine。

---

## 12.4 Planner / Todo / Workflow

不是 V1.0 Core。

如果某个 Skill 通过 Markdown / tool state 已能完成，就不建设 PlannerEngine / Workflow DAG。

---

## 12.5 Multi-Agent / Subagent

不进入 HMBuddy Core。

优先跟随 Pi 上游或 Pi package 生态。

---

# 13. Product UI

V1.0 不把 Desktop 作为第一优先级。

开发验证顺序：

~~~text
Pi native CLI/TUI
    ↓
HMBuddy Extensions + Skills + Office Tools
    ↓
real bank-office scenarios
    ↓
only then decide dedicated GUI
~~~

旧 PySide6 Desktop：

> **属于 Legacy Implementation，不构成 VNext 兼容性要求。**

未来如果需要独立 UI：

- TypeScript UI 可直接嵌 Pi SDK；
- 非 TypeScript UI 可通过 Pi RPC；
- Product UI 不能成为第二个 Agent Runtime。

---

# 14. Upstream Compatibility Strategy

“持续跟进 Pi”是 V1.0 的架构能力，不是项目管理口号。

## 14.1 Exact Pin

生产与开发基线使用明确的 Pi release / lockfile。

禁止以 `latest` 作为可复现基线。

---

## 14.2 Compatibility Matrix

至少维护：

~~~text
Pinned Pi release      → must pass
Latest stable Pi       → compatibility check
Pi main / preview      → optional early warning
~~~

---

## 14.3 Upstream Radar

每次重要 Pi release 重点检查：

- SDK；
- Session；
- Context / Compaction；
- Tool Contract；
- Extension lifecycle；
- Skills；
- MCP；
- Codemode；
- Security / Trust；
- Windows；
- Durable runtime。

检查结果至少回答：

1. 是否有 breaking change？
2. 是否可以删除 HMBuddy 重复代码？
3. 是否出现新的正式扩展面？
4. HMBuddy integration layer 是否需要调整？
5. Office Domain 是否受影响？

---

## 14.4 Upstream-first Deletion

当上游能力成熟后：

> 删除重复实现优先于维护兼容层。

---

# 15. Legacy Policy

V0.2 及 Phase 1–2.2 进入 Legacy 状态。

旧代码的定位：

> **历史实现、学习样本、算法素材库和 Eval 素材库。**

它们不再自动拥有以下权利：

- API 兼容；
- 目录兼容；
- 数据结构兼容；
- Runtime 兼容；
- UI 兼容；
- Plugin Contract 兼容。

旧实现通过分支：

~~~text
legacy/pre-pi-v0.2
~~~

长期保留。

---

# 16. What May Be Salvaged

## 优先重新评估并可能迁移

~~~text
PDF table reconstruction
OCR pipeline
DOCX parsing details
XLSX structure handling
legacy Office COM integrations
ArtifactBlock ideas
ArtifactLocator ideas
Office fixtures / evals
bank-specific tests
~~~

## 默认不迁移

~~~text
plugin_runtime/
llm/
application/
desktop/
HMBuddy Session design
HMBuddy AgentLoop design
HMBuddy ToolRegistry design
HMBuddy ExtensionHost design
generic AppConfig duplication
generic Workspace abstraction
~~~

迁移必须基于 V1.0 新接口重新实现或提取，而不是原目录复制。

---

# 17. VNext Recommended Repository Shape

目标形态参考：

~~~text
HMBuddy/
│
├─ packages/
│  └─ hmbuddy-pi/
│     ├─ src/
│     │  ├─ extension/
│     │  ├─ tools/
│     │  ├─ policy/
│     │  ├─ audit/
│     │  └─ office-bridge/
│     └─ tests/
│
├─ office-runtime/
│  ├─ pyproject.toml
│  ├─ hmbuddy_office/
│  │  ├─ artifact/
│  │  ├─ docx/
│  │  ├─ xlsx/
│  │  ├─ pptx/
│  │  ├─ pdf/
│  │  ├─ ocr/
│  │  ├─ patch/
│  │  └─ validation/
│  └─ tests/
│
├─ skills/
│  ├─ financial-analysis/
│  ├─ regulation-review/
│  ├─ document-drafting/
│  └─ sensewright/
│
├─ config/
│  └─ bank/
│
├─ evals/
└─ requirements/
~~~

这是方向约束，不要求第一次提交一次性建立全部目录。

---

# 18. Restart Sequence

V1.0 推荐从最小纵向链重新启动。

## Stage 0 — Pi Baseline

目标：

> 证明 Pi 在目标 Windows / 内网模型环境下稳定运行。

只验证：

- Pi install；
- internal model；
- Session；
- Extension；
- Skill；
- Tool；
- Windows / offline constraints。

不迁移旧 HMBuddy Runtime。

---

## Stage 1 — Pi-native HMBuddy Extension

只实现最小 Extension + Tool。

目标：

~~~text
Pi
→ HMBuddy Extension
→ deterministic local tool
→ Pi observation
~~~

---

## Stage 2 — Office Bridge

只接一个能力：

~~~text
read_office_file
~~~

打通：

~~~text
Pi Agent
→ TypeScript Tool
→ Python process
→ Office file
→ structured result
→ Pi
~~~

这一步是新架构成立的第一验收线。

---

## Stage 3 — Office Read Pack

逐步加入：

- DOCX；
- XLSX；
- PDF；
- PPTX；
- OCR。

只迁移真正需要的旧算法。

---

## Stage 4 — Office Write Lifecycle

建立：

~~~text
Artifact
→ Patch
→ New Version
→ Validate
→ Diff
~~~

这是 HMBuddy 的核心领域竞争力。

---

## Stage 5 — Banking Skills

接入：

- SenseWright；
- 公文；
- 财务分析；
- 制度；
- 授信。

全部优先采用 Pi / Agent Skills 格式。

---

## Stage 6 — Banking Governance

根据真实内网部署补：

- Approval；
- Audit；
- Network policy；
- Path policy；
- Sensitive-data policy；
- internal connector policy。

---

## Stage 7 — Dedicated Product UI

只有真实使用证明 Pi 原生 UI 不够时再建设。

---

# 19. Architecture Change Threshold

以下任何变化必须先更新本 Baseline 或新增 ADR：

1. Fork Pi；
2. 修改 Pi 源码作为 HMBuddy 长期运行方式；
3. 新建 HMBuddy AgentLoop；
4. 新建 HMBuddy Session Framework；
5. 新建平行 Tool Registry；
6. 新建平行 Extension / Plugin Runtime；
7. 将 TypeScript Pi Host 替换为其他主控架构；
8. 将 Python Office Runtime 与 Agent Runtime重新耦合；
9. 将 Office Artifact 提升为通用 Agent Kernel 概念；
10. 引入独立 Planner / TaskEngine / MemoryEngine / Multi-Agent Framework；
11. 修改 Office Capability Protocol 的基本责任边界。

评审必须回答：

- 上游 Pi 为什么不能满足？
- 为什么 Extension / Skill / Tool 不能解决？
- 真实 failure mode 是什么？
- 新复杂度是否长期属于 HMBuddy？
- 对未来 Pi 升级成本有什么影响？
- 能否通过贡献上游而不是 Fork 解决？

---

# 20. Architecture Review Questions

以后每个需求先回答：

### Q1
这是 Agent 基础设施，还是银行 Office 特性？

如果是前者，先找 Pi。

### Q2
Pi 是否已经提供公开 Contract？

如果有，不自研第二套。

### Q3
这是 Instruction、Executable Behavior，还是 Office Capability？

对应优先映射：

~~~text
Instruction      → Skill
Agent behavior   → Pi Extension / Tool
Office operation → Python Office Runtime
~~~

### Q4
这段代码如果 Pi 明天升级，是否会迫使 HMBuddy 大面积修改？

如果会，说明 Pi 耦合扩散了。

### Q5
这段代码是不是 HMBuddy 真正的差异化资产？

如果不是，应优先删除、上移到 Pi、或保持为薄适配。

---

# 21. Canonical Invariants

V1.0 生效后长期保持以下不变量：

1. **Pi owns the generic agent runtime.**
2. **HMBuddy does not build a parallel Agent Kernel.**
3. **No fork by default.**
4. **Pi coupling stays thin and localized.**
5. **TypeScript is the default Pi-native host.**
6. **Python owns Office engineering, not Agent orchestration.**
7. **Artifact is an Office domain model, not a generic Agent primitive.**
8. **Skills use upstream-compatible Agent Skills format.**
9. **Generic extensions use Pi Extension APIs instead of a HMBuddy plugin platform.**
10. **Banking governance is explicit because Pi project trust is not a security boundary.**
11. **Old code may be discarded; only proven domain capability is migrated.**
12. **Upgradeability against Pi is a first-class architecture requirement.**

---

# 22. Final Architecture Statement

HMBuddy V1.0 的核心架构结论是：

> **HMBuddy 不再“像 Pi 一样实现一个 Agent”，而是直接成为 Pi 上的银行 Office Agent。**

工程资源从：

~~~text
Build Agent Infrastructure
~~~

转向：

~~~text
Extend Pi
+
Build Office Capabilities
+
Build Banking Skills
+
Build Enterprise Governance
~~~

这份 V1.0 是后续 VNext 需求、实现、评审和学习目录重构的唯一 Canonical Architecture Baseline。
