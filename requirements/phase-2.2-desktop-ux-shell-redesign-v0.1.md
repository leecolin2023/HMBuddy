# HMBuddy Phase 2.2 — Desktop UX Shell Redesign 需求规格说明书

**项目阶段：** Phase 2.2 / Desktop UX Shell Redesign  
**版本：** V0.1  
**状态：** Draft / Architecture-aligned  
**架构基线：** requirements/hmbuddy-architecture-baseline.md V0.2  
**前置阶段：** Phase 2 / Phase 2.1 / Phase 2.1.1  
**阶段性质：** Product Layer / Desktop Presentation 重构，不新增 Agent Kernel Primitive  
**文档目的：** 将 HMBuddy 当前偏管理工具式的桌面界面，重构为 Conversation-first 的现代 Office Agent Shell：左侧负责工作导航，中间负责对话与现有文档问答，右侧按需打开 Artifact Preview；同时保持 Workspace、Artifact、File Capability Runtime、Plugin Runtime、Config、State 等既有核心能力不变。

---

# 1. 背景与真实失败模式

Phase 2 建立了桌面入口，Phase 2.1 建立了 Home、Config、AppState、Recent Workspace、Recent Activity、Plugin Manager 和 Settings，Phase 2.1.1 收口了 Desktop / Application / Runtime 的集成缝隙。

当前功能已经可用，但实际使用出现了新的真实失败模式：

> 当前桌面端整体信息架构和视觉形态仍然更像文件管理工具 / Runtime 管理控制台，而不是用户日常使用的办公 Agent。

当前心理模型接近：

~~~text
Home / Workspace / Plugins / Settings
→ 选择目录
→ 文件表格
→ 读取文件
→ 文件概览
→ 文档问答
~~~

而当前成熟开源 Agent 产品已经逐渐收敛到：

~~~text
Navigation / History
        +
Conversation / Current Work
        +
Contextual Work Pane
~~~

因此 Phase 2.2 不是单纯“美化 Tkinter”，而是修复 Product Layer 的信息架构问题。

---

# 2. Benchmark 设计输入

本阶段参考当前开源 Agent 的实际源码与页面结构，但不机械复制任何单一项目。

- Interpreter Workstation：吸收 Agent / Work First、Runtime 与 Workstation UI 解耦。
- Goose：吸收 New Chat、Session/History、Extensions、Settings 的产品分层。
- AnythingLLM：吸收 Workspace 作为长期工作容器，而不是目录选择按钮。
- OpenHands Agent Canvas：吸收 Conversation 主工作面 + Right Work Pane。
- Agent Zero：吸收 Chat / Task / Project / Plugin 的产品分层与 Plugin Manager。
- Cherry Studio：吸收 Agent Conversation + Right Pane、Office File Preview、成熟 Settings 结构。

共同模式确定为：

~~~text
Left Sidebar
    ↓
Work Navigation

Center
    ↓
Conversation / Current Work

Right Pane
    ↓
Artifact Preview on demand
~~~

---

# 3. Architecture Alignment

## 3.1 Architecture Baseline

本阶段遵循 requirements/hmbuddy-architecture-baseline.md V0.2。

继续坚持：

- 产品能力向 WorkBuddy 学习；
- Agent Harness 采用 Pi 式少量稳定原语；
- Office 领域保持 Artifact-native；
- 产品层可以丰富，Kernel 长期保持小；
- 不因 UI 上出现一个功能名称就新增同名 Core Engine。

## 3.2 Kernel Primitives Used

复用当前已经存在的：

- Workspace；
- Artifact；
- ArtifactRef；
- ArtifactBlock；
- ArtifactLocator；
- File Capability Runtime；
- Plugin Runtime；
- AppConfig；
- AppState；
- Recent Workspace / Recent Activity；
- LLM Client / Artifact QA。

## 3.3 Kernel Primitives NOT Implemented

本阶段明确不实现：

- Session；
- AgentLoop；
- ToolRegistry；
- ExtensionHost。

特别说明：

> Phase 2.2 可以在 UI 中使用“Conversation / 新建会话”作为产品交互语言，但不得因此在 Kernel 中提前实现半套 Session。

Conversation 在本阶段是 Presentation Surface，不是持久 Session Domain。

## 3.4 Tools / Skills / Extensions

本阶段不新增 Agent Tool、Skill Runtime 或 ExtensionHost。

## 3.5 Capability Plugins

复用现有 File Capability Plugins。本阶段不修改 Capability Contract，也不新增 artifact.render.preview 等系统级 Runtime Capability。

Markdown / TXT Preview 只属于 Desktop Presentation Layer。

## 3.6 New Core Primitive

No。

## 3.7 Architecture Deviation

None。

---

# 4. 阶段核心问题

Phase 2.2 只回答：

> HMBuddy 能否从“文件管理器 + 文档概览 + 问答框”的桌面工具，升级为一个符合现代 Agent 产品习惯、能够自然承接未来 Session / AgentLoop 的 Conversation-first Office Agent Shell？

本阶段不回答 Agent 如何自主选择文件、调用工具并持续执行多步骤任务，也不回答 Conversation 如何跨重启持久化恢复。

---

# 5. 阶段目标

## G1. Conversation-first

中间主工作区从“文件概览 / 文档问答 Tab”升级为 Conversation Surface。用户与 HMBuddy 的交互成为应用最主要的视觉对象。

## G2. Sidebar 负责工作导航

左侧 Sidebar 只承担“我要去哪 / 要继续哪个工作环境”。至少包含：

- HMBuddy 品牌区；
- 新建会话；
- 搜索；
- Recent / Pinned Workspaces；
- Plugins；
- Settings；
- 极简 System Status。

## G3. Workspace 从功能页面变为工作上下文

Workspace 不再作为固定一级导航按钮。用户看到具体 Workspace，例如 HMBuddy、Reg2Decision、财务分析、合同资料。

## G4. Artifact Preview 按需出现

右侧 Preview 默认隐藏。只有用户点击 Conversation、Search Result 等上下文中的文件对象时才出现。关闭后 Conversation 恢复全宽。

## G5. 首版 Preview 只支持 Markdown / TXT

V0.1 正式支持：

- .md；
- .markdown；
- .txt。

Markdown 必须渲染为阅读视图；TXT 以只读纯文本展示。

## G6. Desktop UI 迁移到 PySide6

新的 Desktop Product Shell 采用 PySide6，保留 Python-first、Local-first 和现有 Runtime 技术栈。

Phase 2.2 是替换 Presentation Shell，而不是重写 Application / Runtime。

---

# 6. 非目标

本阶段明确不实现：

- 持久 Session；
- Session History / Chat History Database；
- Product Task / Task 状态机；
- AgentLoop；
- ToolRegistry；
- ExtensionHost；
- 语义搜索 / Embedding / RAG；
- 多 Artifact 推理；
- Artifact 写回 / Patch / Diff；
- DOCX / PDF / XLSX / PPTX Rich Preview；
- 双层 Icon Rail + Context Sidebar；
- Plugin Marketplace；
- EXE / MSI / Auto Update；
- 完整 Dark Mode。

---

# 7. 新 Desktop 心理模型

旧模型：

~~~text
Open HMBuddy
→ Home
→ Workspace
→ Select File
→ Read File
→ Overview
→ QA
~~~

新模型：

~~~text
Open HMBuddy
→ Current Work / Conversation
→ Select or Continue Workspace
→ Ask / Inspect
→ Click File
→ Preview on Right
~~~

未来 Session Kernel 实现后继续演进为：

~~~text
Workspace
→ Session
→ Conversation
→ Tools
→ Artifacts
~~~

Phase 2.2 必须为这一未来演进预留结构，但不得提前实现 Session。

---

# 8. 总体信息架构

~~~text
┌─────────────────────────────────────────────────────────────┐
│ HMBuddy                                                     │
├────────────────┬─────────────────────────────┬──────────────┤
│ Sidebar        │ Conversation Surface        │ Preview      │
│                │                             │              │
│ + 新建会话      │ Current Workspace           │ file.md      │
│ 搜索            │                             │              │
│                │ User / HMBuddy              │ Rendered     │
│ 工作区          │ File Cards                  │ Content      │
│ ...            │ QA Result                   │              │
│                │                             │              │
│ 插件            │ Composer                    │              │
│ 设置        ●   │                             │              │
└────────────────┴─────────────────────────────┴──────────────┘
~~~

默认状态下 Preview 不出现：

~~~text
┌────────────────┬────────────────────────────────────────────┐
│ Sidebar        │ Conversation Surface                       │
└────────────────┴────────────────────────────────────────────┘
~~~

---

# 9. 布局原则

## 9.1 Sidebar

建议 Default 248 px，Min 220 px，Max 320 px。

## 9.2 Conversation

Conversation 获得绝大多数剩余空间，不为 File Metadata / System Status 预留固定大区域。

## 9.3 Preview

建议 Default 400 px，Min 320 px，Max 不超过窗口宽度 50%。Preview 与 Conversation 使用 Splitter，可关闭。

---

# 10. Sidebar 信息架构

建议固定顺序：

~~~text
HMBuddy

[ + 新建会话 ]
[   搜索     ]

工作区
  HMBuddy
  Reg2Decision
  财务分析
  ...

----------------

插件

设置                     ●
~~~

不再固定显示 Home / Workspace 两个一级功能按钮。

---

# 11. 新建会话

V0.1 对用户显示“新建会话”，暂不使用“新建任务”。

本阶段语义仅为：

- 清空当前 Conversation UI；
- 清除临时 QA Transcript；
- 清除 active Artifact；
- 默认保留当前 Workspace；
- 回到 Conversation Zero State。

不得：

- 创建持久 session_id；
- 写入 Session Store；
- 产生 Recent Session；
- 保存 Chat History。

任何实现如果为了“新建会话”增加 Session Domain / Task Domain / Session DB，必须重新评审。

---

# 12. Search

Sidebar 顶部提供 Search，快捷键建议 Ctrl + K。

V0.1 搜索范围：

- Recent Workspace Display Name；
- Workspace Path；
- 当前 Workspace File Name；
- Relative Path；
- Extension；
- 可选 Recent Activity Title。

建议按“工作区 / 文件 / 最近活动”分组展示结果。

Search 不做文件正文检索、Semantic Search、RAG 或 Cross-workspace Content Index。

---

# 13. Workspace Sidebar

Workspace 以具体工作环境名称展示，不以四列表格呈现。

每一行默认只突出 Display Name。Full Path、Last Opened、Missing 等信息通过 Hover / Tooltip / Context Menu 展示。

排序继续复用当前规则：Pinned 优先，其次 Last Opened Desc。

Missing Workspace 保留记录，支持 Relocate / Remove，不导致 Desktop 崩溃。

---

# 14. Conversation Surface

Conversation 至少由：

- Header；
- Message Stream；
- Composer；

组成。

Header 至少显示当前 Workspace 名称，可选当前 Artifact 名称。完整路径不作为大标题，可放 Tooltip 或 Secondary Text。

---

# 15. Conversation Zero State

当前已有 Workspace 时：

~~~text
HMBuddy

当前工作区：HMBuddy

你想查看或分析什么？

[ 选择文件 ]
~~~

没有 Workspace 时：

~~~text
HMBuddy

选择一个工作区开始

[ 打开工作区 ]
~~~

Zero State 不再显示大面积 System Status Dashboard。

---

# 16. Message Stream

V0.1 至少支持四类 Presentation Item：

- User Message；
- HMBuddy Response；
- File Card；
- Status / Error Notice。

暂不要求 Tool Call Card、Approval Card、Plan、Reasoning、Background Task。

---

# 17. Conversation 与现有 Artifact QA

Phase 2.2 不重新实现 LLM Runtime。

现有流程继续复用：

~~~text
Workspace
→ ArtifactRef
→ ArtifactReader
→ Artifact
→ LLM Client
→ Answer
~~~

Conversation 只是新的 Presentation Surface。

连续展示多个 QA 时不得向用户暗示模型已经拥有可靠的多轮 Session Memory。当前进程可保留临时 Transcript，但不持久化，也不默认进入下一轮模型上下文。

---

# 18. Composer

Composer 固定在中间底部，至少提供：

- Add / Select File；
- Text Input；
- Send。

建议形态：

~~~text
[ + ]  输入问题……                                      [Send]
~~~

当前一次 QA 只要求绑定一个 active Artifact。Multi-Artifact 延后。

---

# 19. File Card

选中的 Artifact 或 Response 中可点击的 Artifact 使用 File Card，例如：

~~~text
财务报告.md
Markdown · 26 KB
~~~

点击 File Card 打开右侧 Preview。

---

# 20. Preview Pane

Preview 默认关闭。

至少支持从以下位置打开：

- Conversation File Card；
- Search File Result。

Header 至少显示 File Name、File Type、Close。

Preview 与 Conversation 应允许调整宽度。

---

# 21. Preview 数据访问边界

这是硬性架构要求。

禁止 Desktop 直接通过 path → open() / Path.read_text() 读取 Preview 内容。

正确链路必须保持：

~~~text
Desktop
→ ArtifactRef
→ Workspace Boundary
→ ArtifactReader
→ Capability Runtime
→ Artifact
→ Preview Renderer
~~~

这样 Workspace Security、Provider Selection、Plugin Routing、Encoding Fallback、Provenance 仍然保持唯一真相。

---

# 22. Markdown Preview

支持 .md / .markdown。

数据来源使用 Artifact.content。当前 TextAdapter 已保留原始 Markdown 文本，因此 Desktop 不需要绕过 Artifact Runtime 重读文件。

至少正确展示：

- Heading；
- Paragraph；
- Bullet / Numbered List；
- Bold / Italic；
- Inline Code；
- Code Block；
- Link；
- Blockquote；
- Simple Table，若 Qt Markdown Renderer 支持。

技术上优先使用 Qt 自身 Markdown / Rich Text 渲染能力，不为了 V0.1 引入 Chromium / Node Renderer。

默认不执行 Script、不自动加载远程资源、不因文档内容发起网络请求。

---

# 23. TXT Preview

支持 .txt。

使用只读文本视图，至少支持 Unicode、中文、换行、Select、Copy、Scroll。

文本来源必须是 Artifact.content。

---

# 24. Unsupported Preview

用户点击 .docx / .pdf / .xlsx / .pptx 等当前可读取但尚未支持桌面 Preview 的文件时，应明确显示：

> 当前版本暂不支持此格式的桌面预览。

可以展示文件名、类型、大小等最小元数据。

必须区分“可以读取”和“可以 Preview”。

---

# 25. Preview Renderer 边界

Phase 2.2 可以在 Desktop 内部建立最小 Presentation Registry，例如 MarkdownRenderer / TextRenderer。

它只是 Desktop Presentation Contract，不是 Capability Registry、Plugin Runtime 或 Kernel Primitive。

未来如果 Office Preview 出现多实现、第三方扩展、Selection Reference 等真实需求，再评估独立 Preview Capability。

---

# 26. Plugin Manager 新视觉结构

现有 Plugin Runtime 和 PluginManagement 逻辑继续复用，只重构 Presentation。

Plugin 页面在中间主内容区打开，右侧 Artifact Preview 关闭。

不再使用工程式 Treeview 作为主要 Presentation，优先使用 Card / Rich List Row。

每个 Plugin 至少展示：

- Display Name；
- Description，若存在；
- Status；
- Source；
- Formats；
- Main Capability；
- Enable / Disable。

Plugin Detail 至少展示 Plugin ID、Version、Source、Status、Capabilities、Accepted Extensions、Declared Permission、Effective Permission、Provider、Load Error。

Directory、Manifest Path、API Version、Provider ID、Priority 等信息放到 Advanced。

---

# 27. Settings 新视觉结构

Settings 在中间主内容区打开，采用左侧分类导航 + 右侧内容区，不再把所有 LabelFrame 纵向堆叠。

V0.1 分类建议：

- General；
- Models；
- File Processing；
- Plugins；
- Advanced。

General：Restore Last Workspace、Recent Workspace Limit、Recent Activity Limit。

Models：Base URL、Model、API Key Source / Status。

File Processing：OCR Model Directory、文件能力基础状态。

Plugins：External Plugin Directories、Plugin Manager 跳转、Rescan 状态。

Advanced：Config Path、State Path、Log Path、Environment Overrides、Runtime Source。

---

# 28. Effective Config Source

Phase 2.1 已建立的配置来源可解释性必须保留。

例如：

~~~text
Model
deepseek-v4                         Environment
~~~

Hover / Detail 可显示：

~~~text
Overridden by HMBUDDY_LLM_MODEL
~~~

不得回退成“用户修改了 UI 但不知道为什么不生效”的黑盒。

---

# 29. System Status

正常状态只使用低权重 Status Dot，例如 ● Ready，位于 Sidebar 底部。

需要时再展开 LLM、Plugins、OCR、Config 等详细状态。

错误优先使用 Banner / Inline Notice / Toast，不再把状态长期占据首页大区域。

---

# 30. Error Presentation

至少统一：

- Workspace Missing：Sidebar Row 标记 Missing，支持 Relocate / Remove；
- Artifact Read Error：Conversation / Preview 内联显示简短原因；
- Preview Unsupported：明确区分 Read 支持与 Preview 不支持；
- LLM Not Configured：Composer 提示并可跳转 Settings → Models；
- Plugin Error：Status Dot Warning，Plugin Page 查看详情；
- Config Error：应用仍进入 Shell，Settings → Advanced 查看错误。

---

# 31. 视觉设计原则

Phase 2.2 的视觉方向定义为：Calm Enterprise Agent。

原则：

- 中性背景；
- 单一 Accent；
- 低对比 Border；
- 中等圆角；
- 极少 Shadow；
- 清晰 Typography；
- 8px spacing rhythm；
- System Font；
- 状态优先 Badge / Dot；
- 只有真正结构化数据才使用 Table；
- Navigation / Recent / Plugin 优先 Row / Card；
- 避免 Frame 套 Frame。

Windows 字体建议 Microsoft YaHei UI / Segoe UI / System UI fallback。

---

# 32. Desktop Technology

Phase 2.2 新 Presentation Layer 采用 PySide6。

主要保留并复用：

- application/*；
- desktop/controller.py 中可复用的无头应用动作；
- workspace/*；
- services/*；
- plugin_runtime/*；
- adapters/*；
- plugins/*；
- llm/*。

主要替换：

- Tkinter root / event loop；
- desktop/shell.py Presentation；
- desktop/pages/* Presentation。

Controller 不 import Qt；Runtime 不 import Qt。

Phase 2.2 正式完成后，不长期维护 Tkinter Desktop 和 PySide6 Desktop 两套正式 UI。

---

# 33. 推荐 Presentation 模块边界

实现时建议逐渐形成：

~~~text
desktop/
├─ app.py
├─ controller.py
├─ shell.py
├─ theme/
├─ widgets/
│  ├─ sidebar.py
│  ├─ conversation.py
│  ├─ composer.py
│  ├─ file_card.py
│  ├─ status.py
│  └─ preview/
│     ├─ pane.py
│     ├─ markdown.py
│     └─ text.py
├─ pages/
│  ├─ plugins.py
│  └─ settings.py
└─ presenter.py
~~~

这是职责建议，不要求为了目录漂亮机械拆文件。

---

# 34. Startup Flow

启动流程保持：

~~~text
Resolve Config / State
→ Assemble Plugin Runtime
→ Build Controller
→ Start Qt Application
→ Build Desktop Shell
→ Restore Last Workspace if enabled
→ Render Conversation Zero State
~~~

Config / Plugin / LLM 的部分错误不阻止进入 Shell。

---

# 35. Phase 2.1 Home 的迁移

Phase 2.2 不再保留 Home 作为 Sidebar 一级页面。

- Open Workspace → Conversation Zero State / New Conversation；
- Open File → Composer Add File / Search；
- Recent Workspaces → Sidebar Workspace Section；
- Recent Activity → Search / Optional Zero State；
- System Status → Sidebar Status Dot。

这是能力重新分层，不是删除能力。

---

# 36. Phase 2.1 Workspace Page 的迁移

旧 Workspace 页中的 Workspace Path Entry、File Table、File Overview Tab、QA Tab 不再作为一个完整独立页面保留。

迁移关系：

- Select Workspace → Sidebar / Zero State；
- File List → Search / File Picker；
- Read Artifact → File Card / Preview / QA Flow；
- Artifact Overview → Preview / Metadata；
- QA → Conversation；
- Workspace Status → Conversation Header / Sidebar。

---

# 37. Recent Activity

Phase 2.2 继续兼容 Phase 2.1 的 RecentActivity 数据，但不把它升级为 Session。

可用于 Search Result、Zero State 最近项、Workspace 辅助排序。

未来 Session 实现后，Agent 工作历史进入 Session Index，RecentActivity 不发展成 TaskEngine。

---

# 38. Future Session 插槽

Phase 2.2 的 Shell 必须保证未来加入 Session 时不需要再次推翻布局。

未来左侧可以自然演进为：

~~~text
+ 新建会话

今天
  财务分析
  制度审阅

昨天
  合同修改

工作区
  HMBuddy
  Reg2Decision
~~~

未来中间变成 Session-backed Conversation；未来右侧可继续扩展 Artifact、Files、Browser、Activity、Diff。

本阶段只实现已有 Runtime 真正支撑的部分。

---

# 39. 测试策略

必须覆盖：

## T1 Controller Regression
- 现有 Controller / Application 单测继续通过；
- Qt 不渗入 Runtime 单测。

## T2 Sidebar
- New Conversation；
- Search；
- Workspace Rows；
- Plugin；
- Settings；
- Status Dot。

## T3 Workspace Navigation
- 打开 / 切换 Workspace；
- Missing；
- Pin / Unpin；
- Remove。

## T4 Conversation
- Zero State；
- User Message；
- HMBuddy Response；
- Artifact QA；
- New Conversation 清空临时 Transcript；
- 不创建持久 Session。

## T5 Search
- Workspace Name / Path；
- Current Workspace File Name / Relative Path；
- 不读取文件正文。

## T6 Preview
- Markdown；
- TXT；
- Unsupported Preview；
- Close / Resize / Switch File；
- ArtifactReader 路由；
- Workspace Boundary。

## T7 Plugin Manager
- List / Search / Enabled / Disabled / Error / Detail / Rescan。

## T8 Settings
- Categories / Effective Config Source / Save / Environment Override。

## T9 Error UX
- LLM Missing / Workspace Missing / Preview Unsupported / Plugin Error / Config Error / Artifact Parse Error。

## T10 Qt Smoke
- Application 启动；
- Shell 渲染；
- Sidebar 切换；
- Preview 开关；
- Window Resize；
- 无 Workspace / LLM 时不崩溃。

---

# 40. 验收标准

- **AC-01**：正式 Desktop Presentation Layer 使用 PySide6，不再以 Tkinter 作为正式 UI；
- **AC-02**：Workspace / Artifact / Plugin Runtime / Config / State 未因 UI 重构产生第二套 Domain；
- **AC-03**：未新增 Session / AgentLoop / ToolRegistry / ExtensionHost；
- **AC-04**：默认 Shell 为 Sidebar + Conversation，Preview 默认隐藏；
- **AC-05**：Sidebar 不再固定显示 Home / Workspace 两个一级功能按钮；
- **AC-06**：Sidebar 至少提供 New Conversation、Search、Recent/Pinned Workspaces、Plugins、Settings；
- **AC-07**：Workspace 以具体工作区名称展示，不以四列表格作为主要导航；
- **AC-08**：New Conversation 只清空临时 UI，不创建持久 Session；
- **AC-09**：中间主区域为 Conversation Surface；
- **AC-10**：现有 Artifact QA 可以在 Conversation Surface 完成；
- **AC-11**：Search 可以按名称 / 路径搜索 Recent Workspace 和当前 Workspace 文件；
- **AC-12**：Search 不建立语义索引或正文索引；
- **AC-13**：Conversation / Search 中的 File Card 可以打开右侧 Preview；
- **AC-14**：Preview 可以关闭，关闭后 Conversation 恢复可用宽度；
- **AC-15**：V0.1 Preview 正式支持 .md / .markdown / .txt；
- **AC-16**：Markdown 使用 Artifact.content 渲染为阅读视图；
- **AC-17**：TXT 使用 Artifact.content 只读展示；
- **AC-18**：Desktop Preview 不直接通过 open / Path.read_text 绕过 Artifact Runtime；
- **AC-19**：DOCX / PDF / XLSX / PPTX 等格式显示明确 Unsupported Preview，不影响读取能力；
- **AC-20**：Plugin Manager 使用 Card / Rich Row，并复用现有 Plugin Runtime 真实状态；
- **AC-21**：Settings 使用分类导航 + 内容区；
- **AC-22**：Effective Config Source 可解释性继续保留；
- **AC-23**：正常 System Status 缩成低权重 Status Dot；
- **AC-24**：现有 AppConfig / AppState / Recent Workspace 数据继续兼容；
- **AC-25**：现有 Runtime / Application 回归测试继续通过；
- **AC-26**：新 UI 不要求 EXE / MSI 即可从源码启动；
- **AC-27**：正式完成后不长期维护 Tkinter 与 PySide6 两套正式 Desktop；
- **AC-28**：未来加入 Session 时，Sidebar / Conversation / Preview Shell 不需要结构性推翻。

---

# 41. 实施顺序建议

未来真正开发时建议：

1. Qt Shell Skeleton：QApplication / Main Window / Sidebar / Main Surface / Optional Right Pane；
2. Theme / Layout Tokens：Spacing / Typography / Border / Radius / Width；
3. Existing Controller Bridge：验证 Config / State / Workspace / Plugin / LLM 无需重写；
4. Sidebar / Workspace Navigation；
5. Conversation Surface：迁移现有 Artifact QA；
6. File Card / File Picker；
7. Markdown / TXT Preview；
8. Search；
9. Plugin Manager Redesign；
10. Settings Redesign；
11. Error / Status UX；
12. Regression / Remove Legacy Tk。

---

# 42. 退出条件

Phase 2.2 完成后，HMBuddy 应从：

> 一个可以读取办公文件的桌面管理工具

升级为：

> **一个已经具有现代 Office Agent 产品形态、但仍保持极简 Kernel 边界的本地工作台。**

它应具备：

~~~text
Modern Desktop Shell
+ Conversation-first UX
+ Workspace Navigation
+ Artifact-native File Context
+ On-demand Markdown / TXT Preview
+ Plugin Manager
+ Settings
~~~

但仍然明确没有 Session、AgentLoop、ToolRegistry、ExtensionHost、Persistent Task。

---

# 43. 与下一阶段的关系

Phase 2.2 完成后，再进入 Minimal Agent Kernel。

下一阶段真正新增 Session、AgentLoop、ToolRegistry、最小 ExtensionHost。

届时：

- 新建会话 → 真正 Session Create；
- Sidebar → 增加 Recent Sessions；
- Conversation → Session-backed；
- File Card → 进入 Session Artifact Refs；
- Tool Execution → 进入 Message Stream；
- Preview Shell → 不需要推翻。

Phase 2.2 的长期价值是：

> **先把 Product Shell 放到正确的位置，再让新的 Minimal Agent Kernel 自然长进来，而不是以后每加一个 Agent 能力就重新推翻桌面信息架构。**

---

# 44. 最终阶段定义

Phase 2：HMBuddy 有了桌面入口。

Phase 2.1：HMBuddy 有了可持续使用的 Desktop Application Foundation。

Phase 2.1.1：HMBuddy 收口了 Desktop 与 Runtime 的集成缝隙。

Phase 2.2：

> **HMBuddy 从工程视角的桌面工具升级为 Conversation-first 的现代 Office Agent Shell。**

Phase 2.2 的成功标准不是“PySide6 比 Tkinter 更漂亮”，而是：

1. 用户首先看到工作 / 对话，而不是 Runtime 模块；
2. Workspace 成为具体工作环境，而不是功能菜单；
3. Artifact 成为 Conversation 中可点击、可预览的工作对象；
4. Plugin / Settings 回到正确的管理层级；
5. Shell 能自然承接未来 Session / AgentLoop，而不需要再次重构产品骨架。