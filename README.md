# HMBuddy — Local Office Artifact Runtime + Desktop Entry

HMBuddy 是一个面向企业内网、可离线运行的办公助手项目。

当前已完成两个阶段：

- **Phase 1：Local Office Artifact Runtime**  
  稳定发现并统一读取 DOCX / PDF / XLSX / PPTX，保留必要结构并转成 Artifact。
- **Phase 2：Desktop Entry & Human-in-the-loop Workspace**  
  在 Phase 1 运行时之上增加桌面入口，让用户可以选择工作区、选择文件、读取结构摘要，并在已配置模型时直接问答。

Phase 2 规格说明：
[requirements/phase-2-desktop-entry-v0.1.md](./requirements/phase-2-desktop-entry-v0.1.md)

---

## 1. 桌面端快速开始

```bash
# Python >= 3.10
pip install -e ".[dev]"

# 启动桌面端
python -m desktop.app

# 安装后也可以直接使用命令
hmbuddy-desktop
```

Windows 用户还可以直接双击仓库根目录：

```text
start_hmbuddy_desktop.bat
```

桌面端采用 Python 标准库 Tkinter，不新增 Electron / Node.js / 第三方 GUI 依赖。

### 桌面端当前支持

1. 选择本地 Workspace；
2. 查看 DOCX / PDF / XLSX / PPTX 文件；
3. 查看文件类型、大小、修改时间；
4. 双击或点击按钮读取文件；
5. 查看 Artifact 结构摘要、解析信息和有限内容预览；
6. 配置模型后，对当前已读取文件直接提问；
7. 文件解析与模型请求在后台线程运行，避免冻结 Tk 主线程。

---

## 2. LLM 配置

HMBuddy 使用 OpenAI 兼容协议，可指向企业内网私有化模型端点。

```bash
# Linux / macOS
export HMBUDDY_LLM_BASE_URL=https://llm.intranet.example.com/v1
export HMBUDDY_LLM_MODEL=your-model
export HMBUDDY_LLM_API_KEY=...
```

Windows PowerShell：

```powershell
$env:HMBUDDY_LLM_BASE_URL="https://llm.intranet.example.com/v1"
$env:HMBUDDY_LLM_MODEL="your-model"
$env:HMBUDDY_LLM_API_KEY="..."
python -m desktop.app
```

如果未配置模型，桌面端仍可正常完成 Workspace 浏览与 Artifact 阅读，只会禁用问答按钮。

---

## 3. Phase 1 CLI 仍然保留

CLI 继续用于调试、Eval 和无 GUI 环境。

```bash
python app.py evals/fixtures/sample.docx --no-llm
python app.py evals/fixtures/sample.xlsx --show-context
python app.py evals/fixtures --scan
```

配置 LLM 后：

```bash
python app.py evals/fixtures/sample.docx
```

---

## 4. 架构

```text
                 ┌──────────────────────────────┐
                 │ Application Layer            │
                 │ desktop/        app.py CLI   │
                 └──────────────┬───────────────┘
                                │
                 ┌──────────────▼───────────────┐
                 │ LLM Interface (llm/)         │
                 │ Artifact → Context → LLM     │
                 └──────────────┬───────────────┘
                                │
                 ┌──────────────▼───────────────┐
                 │ Artifact Service (services/) │
                 │ read_artifact()              │
                 └──────────────┬───────────────┘
                                │
             ┌──────────────────┴──────────────────┐
             │                                     │
┌────────────▼────────────┐           ┌────────────▼────────────┐
│ Workspace (workspace/)  │           │ Artifact Model          │
│ 文件发现 / 边界 / Ref    │           │ Artifact / Block       │
└────────────┬────────────┘           └────────────┬────────────┘
             │                                     │
             └──────────────┬──────────────────────┘
                            │
          ┌─────────────────▼─────────────────┐
          │ Adapter Router                    │
          │ DOCX / PDF / XLSX / PPTX          │
          └─────────────────┬─────────────────┘
                            │
                    Local Filesystem
```

Phase 2 的设计原则是：**Desktop 只是薄应用层，不复制 Phase 1 Runtime。**

例如：

- 文件列表来自 `Workspace.list_artifacts()`；
- 文件读取来自 `read_artifact()`；
- 问答来自 `client.ask(artifact, question)`；
- UI 不直接调用具体格式 Adapter。

---

## 5. 目录结构

```text
app.py                       Phase 1 CLI 演示入口
desktop/                     Phase 2 桌面应用层
  __init__.py
  app.py                     Tkinter 页面、事件、后台线程
  presenter.py               Artifact → UI 文本格式化
workspace/                   Workspace、ArtifactRef、Artifact/ArtifactBlock、错误类型
adapters/                    DOCX / PDF / XLSX / PPTX 适配器
services/                    ArtifactReader：read_artifact() 单一入口
llm/                         artifact_to_context() + OpenAI 兼容客户端
evals/                       Parser / Context / QA Eval + baseline
tests/                       单元测试
requirements/                分阶段需求规格说明书
start_hmbuddy_desktop.bat    Windows 双击启动入口
```

---

## 6. Phase 1 核心能力

给定一个本地工作目录，系统可以：

1. **发现**目录中的 DOCX / PDF / XLSX / PPTX；
2. 统一通过 `read_artifact()` 读取任意支持格式；
3. **保留结构**，而不是把文件压成一大段纯文本；
4. 将 Artifact 渲染成对 LLM 友好的 Context；
5. 在用户明确指定文件的前提下完成内容问答。

关键接口：

```python
from workspace.workspace import Workspace
from services.artifact_reader import read_artifact
from llm.context import artifact_to_context

refs = Workspace("D:/工作目录").list_artifacts()
artifact = read_artifact("报表.xlsx")
context = artifact_to_context(artifact)
```

Phase 1 规格：
[requirements/phase-1-local-office-artifact-runtime-v0.1.md](./requirements/phase-1-local-office-artifact-runtime-v0.1.md)

---

## 7. 测试

```bash
python -m pytest -q
```

桌面层新增的格式化逻辑放在 `desktop.presenter`，可以在无 GUI 环境下测试。

GUI 最小 Smoke Test：

1. `python -m desktop.app`
2. 选择 `evals/fixtures`
3. 应看到 DOCX / PDF / XLSX / PPTX
4. 双击 `sample.docx`
5. 右侧出现结构摘要
6. 未配置 LLM 时问答按钮保持禁用
7. 配置 LLM 后可以对当前 Artifact 提问

---

## 8. 当前边界

当前仍然是 **Human-in-the-loop**，明确不做：

- Agent 自主选择文件；
- Workspace 语义搜索；
- 多文件自动比较；
- Tool Calling Loop；
- Planner；
- Word / Excel / PPT 写回；
- 自动覆盖原文件；
- 任务持久化与中断恢复。

这些能力是否进入下一阶段，由桌面入口投入真实使用后出现的失败模式决定，而不是为了凑完整 Agent 架构提前实现。
