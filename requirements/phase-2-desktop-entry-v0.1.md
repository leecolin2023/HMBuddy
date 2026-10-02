# 内网办公 Agent 第二阶段需求规格说明书

**项目阶段：** Phase 2 / Milestone 1  
**版本：** V0.1  
**阶段主题：** Desktop Entry & Human-in-the-loop Workspace  
**文档目的：** 在不改变 Phase 1 Artifact Runtime 核心边界的前提下，为 HMBuddy 增加可直接使用的桌面端入口，形成“选择工作区—选择文件—读取—查看—提问”的最小闭环。

---

## 1. 背景

Phase 1 已完成本地 Office Artifact Runtime，系统已经能够：

- 发现本地 Workspace 中的 DOCX / PDF / XLSX / PPTX；
- 统一通过 `read_artifact()` 读取文件；
- 保留标题、段落、表格、页码、Sheet、公式等必要结构；
- 将 Artifact 转换为 LLM Context；
- 在用户明确指定文件后完成内容问答。

但当前主要入口仍是：

```bash
python app.py <path>
```

这适合开发、调试和 Eval，不适合作为日常办公入口。

第二阶段首先解决的不是“让 Agent 更自主”，而是：

> **让已有能力以一个低门槛、可观察、可控制的桌面界面真正进入使用。**

---

## 2. 第二阶段核心问题

本阶段只回答：

> **用户能否从桌面启动 HMBuddy，选择一个本地工作目录，看见可用办公文件，明确选择文件后读取 Artifact，并在同一界面完成查看与问答？**

目标链路：

```text
Desktop Entry
    ↓
选择 Workspace
    ↓
列出 ArtifactRef
    ↓
用户明确选择文件
    ↓
read_artifact()
    ↓
结构摘要 / 内容预览
    ↓
（可选）LLM 问答
```

本阶段仍坚持 Human-in-the-loop：**文件由用户选择，不允许模型自主搜索或选择文件。**

---

## 3. 阶段目标

### G1. 提供可直接启动的桌面入口

至少支持：

```bash
python -m desktop.app
```

安装项目后支持：

```bash
hmbuddy-desktop
```

Windows 仓库目录下支持双击：

```text
start_hmbuddy_desktop.bat
```

桌面层不得要求 Node.js / Electron，不新增网络依赖。

### G2. 可视化 Workspace 文件发现

用户可：

- 选择本地目录；
- 输入目录后回车加载；
- 刷新当前目录；
- 直接选择一个 Office 文件，并自动把其父目录设为 Workspace；
- 查看支持文件的类型、名称、大小、修改时间。

文件发现必须复用 `Workspace.list_artifacts()`，不得在 UI 层重新实现格式判断和递归扫描。

### G3. 可视化读取 Artifact

用户明确选择文件后，可点击“读取选中文件”或双击文件。

读取必须复用：

```python
read_artifact(ref)
```

桌面层只消费统一 Artifact，不直接调用 Docx/Pdf/Xlsx/Pptx Adapter。

界面至少展示：

- 文件名；
- 文件类型；
- 路径；
- Artifact ID；
- block 类型统计；
- Sheet / Page 等通用元数据；
- Adapter；
- 解析耗时；
- 有界长度的内容预览。

### G4. 在已有 LLM 配置下完成文档问答

如果已配置：

- `HMBUDDY_LLM_BASE_URL`
- `HMBUDDY_LLM_MODEL`
- `HMBUDDY_LLM_API_KEY`（可选）

桌面端显示当前模型名称，并允许对当前已读取 Artifact 提问。

问答继续复用 Phase 1：

```python
client.ask(artifact, question)
```

未配置模型时，桌面入口仍应可以正常使用 Workspace 和 Artifact 阅读能力；问答按钮禁用并给出明确提示。

### G5. 保持 UI 响应与错误可见

文件解析和 LLM 请求不得阻塞 Tk 主线程。

解析失败、模型失败等错误必须：

- 不导致程序退出；
- 恢复按钮状态；
- 在状态栏与错误弹窗中给出可读信息；
- 后台保留日志。

---

## 4. 非目标

以下能力不属于 Phase 2 V0.1。

### 4.1 不做 Agent 自主选文件

不实现：

- “帮我找刚才那份报告”后自动遍历并决定文件；
- Semantic Workspace Search；
- Planner 自主选择文件。

### 4.2 不做 Tool Calling / Agent Loop

不实现：

- 工具自动调用；
- 多步自主规划；
- ReAct / Plan-and-Execute；
- 自主任务循环。

### 4.3 不做 Office 文件修改

不实现：

- update_docx；
- update_xlsx；
- update_pptx；
- 自动覆盖原文件；
- 版本回滚。

### 4.4 不做完整桌面产品工程

本阶段不要求：

- 安装包 / MSI；
- 自动更新；
- 系统托盘；
- 开机自启；
- 多窗口；
- 账号体系；
- 权限中心；
- 前端主题系统。

这些应在入口实际使用后，根据失败模式决定是否进入后续阶段。

---

## 5. 架构原则

### P1. Desktop 是薄壳，不复制 Runtime

```text
desktop/
   ↓
workspace/ + services/ + llm/
   ↓
adapters/
```

UI 不拥有第二套文件扫描、解析或模型调用逻辑。

### P2. Human-in-the-loop 优先

当前产品价值不是“替用户偷偷做决定”，而是：

- 降低使用门槛；
- 让文件选择可见；
- 让解析结果可见；
- 让失败可定位；
- 为后续 Agent 化收集真实交互数据。

### P3. 无新增运行时依赖

V0.1 使用 Python 标准库 Tkinter。

理由：

- Windows Python 常规安装可直接使用；
- 适合内网离线部署；
- 不引入 Node / WebView / Electron；
- 当前页面复杂度不需要前端框架。

如果未来出现复杂富文本编辑、拖拽编排、多窗格任务工作台等真实需求，再评估 PySide / Web 技术栈。

### P4. CLI 保留

`app.py` 继续作为：

- 最小调试入口；
- Eval 辅助入口；
- 无 GUI 环境入口。

桌面端不是替换 Runtime 和 CLI，而是新的 Application Layer。

---

## 6. 模块设计

新增：

```text
desktop/
├─ __init__.py
├─ app.py
└─ presenter.py
```

职责：

| 模块 | 职责 |
|---|---|
| `desktop.app` | Tkinter 生命周期、用户事件、后台线程、状态管理 |
| `desktop.presenter` | 将 Artifact / ArtifactRef 转成 UI 文本，禁止依赖 Tkinter |
| `workspace` | 目录边界与文件发现，沿用 Phase 1 |
| `services.artifact_reader` | 统一读取，沿用 Phase 1 |
| `llm.client` | 模型客户端与问答，沿用 Phase 1 |

---

## 7. 页面结构

### 7.1 顶部

展示：

- HMBuddy；
- “本地办公助手 · Phase 2 Desktop Entry”；
- 当前模型状态。

### 7.2 工作区区域

包含：

- 工作区路径输入框；
- 选择目录；
- 选择文件；
- 刷新。

### 7.3 左侧文件列表

列：

- 类型；
- 文件名；
- 大小；
- 修改时间。

行为：

- 单击：选择；
- 双击：读取；
- 重新加载 Workspace 后刷新列表。

### 7.4 右侧文件概览

展示 Artifact 结构摘要和有限内容预览。

### 7.5 右侧文档问答

包含：

- 单行问题输入；
- 提问按钮；
- 回答区域。

提问只针对当前已读取 Artifact。

### 7.6 底部状态栏

展示：

- 当前 Workspace；
- 当前选择；
- 正在读取；
- 正在问答；
- 完成 / 失败状态。

---

## 8. 状态模型

最小状态：

```text
workspace: Workspace | None
refs: list[ArtifactRef]
current_artifact: Artifact | None
llm_client: BaseLLMClient | None
busy: bool
```

状态约束：

1. 未加载 Workspace：无文件可选；
2. 已加载 Workspace：可选文件；
3. 选中文件但未读取：可点击“读取”；
4. Artifact 读取成功：显示概览；
5. Artifact 已读取且 LLM 已配置：可提问；
6. 后台任务执行中：刷新 / 读取 / 提问按钮避免重复触发。

---

## 9. 错误处理

### ER-D01 工作区不存在

提示“工作区不可用”，不退出程序。

### ER-D02 文件读取失败

复用 Phase 1 `ArtifactRuntimeError` 体系，错误显示类型和消息。

### ER-D03 LLM 未配置

不视为程序错误。问答能力禁用，其余能力可用。

### ER-D04 LLM 调用失败

捕获 `LLMError`，显示错误并保持当前 Artifact。

### ER-D05 UI 后台任务意外异常

Desktop 层作为最终 UI 边界，捕获异常、写日志、恢复 UI，不让后台异常静默结束。

---

## 10. 并发要求

Tkinter 控件只允许主线程更新。

文件读取与 LLM 调用使用后台 daemon thread：

```text
Main Thread
  ├─ UI event
  ├─ start worker
  └─ root.after(...) 回主线程更新 UI

Worker
  └─ read_artifact / llm.ask
```

本阶段不引入线程池、asyncio 或任务队列。

---

## 11. 安装与启动

### 开发启动

```bash
pip install -e ".[dev]"
python -m desktop.app
```

### 安装后命令

```bash
hmbuddy-desktop
```

### Windows 双击

```text
start_hmbuddy_desktop.bat
```

---

## 12. 测试策略

### T1. Presenter 单元测试

`desktop.presenter` 必须可在无 GUI 环境下测试：

- 文件大小格式化；
- Artifact 摘要包含核心元数据；
- 预览有长度上限。

### T2. 既有 Phase 1 回归

必须继续通过原有：

```bash
python -m pytest -q
```

桌面入口不得改变：

- Workspace 扫描规则；
- Adapter 行为；
- Artifact 数据结构；
- Context 构造；
- LLM 协议。

### T3. GUI Smoke Test

人工最小检查：

1. 启动窗口；
2. 选择 `evals/fixtures`；
3. 应看到 DOCX / PDF / XLSX / PPTX；
4. 双击 `sample.docx`；
5. 文件概览出现结构摘要；
6. 未配置 LLM 时提问按钮不可用；
7. 配置 LLM 后可提问且窗口在等待期间仍可重绘。

---

## 13. 验收标准

Phase 2 V0.1 完成必须同时满足：

- AC-01：`python -m desktop.app` 能启动；
- AC-02：可选择目录并显示四类支持文件；
- AC-03：文件列表来自 `Workspace.list_artifacts()`；
- AC-04：读取来自 `read_artifact()`；
- AC-05：双击或按钮均可读取文件；
- AC-06：显示结构摘要、解析信息和内容预览；
- AC-07：未配置 LLM 不影响本地阅读能力；
- AC-08：配置 LLM 后可对当前 Artifact 提问；
- AC-09：文件读取与 LLM 请求不阻塞 Tk 主线程；
- AC-10：Windows 可通过根目录 `.bat` 启动；
- AC-11：不引入第三方 GUI / Node 依赖；
- AC-12：Phase 1 测试保持通过。

---

## 14. 实施顺序

```text
Step 1  建立 desktop package
Step 2  抽离无 GUI 的 presenter
Step 3  完成 Workspace 选择与文件列表
Step 4  接入 read_artifact
Step 5  接入 LLM 问答
Step 6  后台线程与错误处理
Step 7  增加 CLI entry point / Windows bat
Step 8  补测试、README 与规格说明
```

---

## 15. 本阶段完成后的判断点

Phase 2 的目的不是证明“桌面 GUI 做完了”，而是让真实使用开始发生。

进入下一阶段前重点观察：

- 用户是否经常不知道该选哪个文件；
- 是否频繁需要同时选择多个文件；
- 是否需要搜索文件内容而不是按名称找；
- 是否出现“基于旧成果继续改”的强需求；
- 是否需要真正写回 Word / Excel / PPT；
- 是否出现任务中断恢复需求。

只有这些失败模式稳定出现后，再决定 Phase 3 优先进入：

- Workspace Search；
- Multi-Artifact Context / Compare；
- Artifact Update；
- Persistent Task / Workspace State；
- Tool Calling Agent Loop。

> **原则仍然不变：下一阶段由真实办公失败模式驱动，而不是为了凑齐“Agent 架构图”。**
