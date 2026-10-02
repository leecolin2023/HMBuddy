# HMBuddy — Local Office Artifact Runtime + Desktop Entry

HMBuddy 是一个面向企业内网、可离线运行的办公助手项目。

当前已完成两个阶段：

- **Phase 1：Local Office Artifact Runtime**  
  稳定发现并统一读取 DOCX / PDF / XLSX / PPTX，保留必要结构并转成 Artifact。
- **Phase 1.1：Pluggable File Capability Runtime**  
  文件能力从静态 Adapter 集合升级为可发现、可注册、可替换的插件运行时。
- **Phase 1.1.1：Plugin Runtime Contract Hardening**  
  收口 1.1 审阅发现的 17 项缺陷：权限强阻断、Capability Catalog、Manifest 权威、
  Workspace 信任域、可用性路由、ArtifactLocator、Context 默认预算、外部插件
  package 支持、CI 安装态验证。
- **Phase 2：Desktop Entry & Human-in-the-loop Workspace**  
  在 Phase 1 运行时之上增加桌面入口，让用户可以选择工作区、选择文件、读取结构摘要，并在已配置模型时直接问答。

规格说明：
[Phase 1](./requirements/phase-1-local-office-artifact-runtime-v0.1.md) ·
[Phase 1.1](./requirements/phase-1.1-pluggable-file-capability-runtime-v0.1.md) ·
[Phase 1.1.1](./requirements/phase-1.1.1-plugin-runtime-contract-hardening-v0.1.md) ·
[Phase 2](./requirements/phase-2-desktop-entry-v0.1.md)
历史文件提取工具 fce 的核心能力已拆解融入 `adapters/`（见"能力来源"）：
支持格式扩展到 XLS / DOC / TXT / MD / CSV 等，PDF 增加矢量表格引擎（合并单元格、
跨页续表）与可选 OCR，详见下文。

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

### 可选依赖组（fce 能力融入后新增）

```bash
pip install -e ".[legacy]"   # .xls/.doc 遗留格式（xlrd + pywin32；缺省时适配器给出明确报错）
pip install -e ".[ocr]"      # 扫描件 OCR（paddleocr/paddlex/pypdfium2；默认关闭）
```

OCR 模型只从**本地目录**解析（`HMBUDDY_MODEL_DIR` / `FCE_MODEL_DIR` 环境变量，或项目根 `./models/`），**绝不隐式下载**（沿用 fce/AGENTS.md 边界）。代码中开启方式：

```python
from adapters.base import OcrOptions
from services.artifact_reader import read_artifact

artifact = read_artifact(
    "扫描件.pdf",
    ocr_options=OcrOptions(enable_ocr=True, enable_table_ocr=True),
)
```

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
python -m pytest -q                                            # 全部 Eval（数量以 baseline 为准）

python app.py evals/fixtures/sample.docx --no-llm
python app.py evals/fixtures/sample_table.pdf --show-context   # 矢量表格 + 跨页续表
python app.py evals/fixtures/sample.xls --no-llm               # 遗留 .xls
python app.py evals/fixtures --scan                            # 扫描目录
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
                 │ （OCR 经 OcrOptions 传入，   │
                 │   默认关闭）                 │
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
          │ Adapter Router (adapters/)        │
          │ DOCX DOC PDF XLSX XLS PPTX TXT... │
          └─────────────────┬─────────────────┘
                            │
                    Local Filesystem
```

Phase 2 的设计原则是：**Desktop 只是薄应用层，不复制 Phase 1 Runtime。**

### 插件化文件能力运行时（Phase 1.1）

文件能力不再由核心代码静态绑定（`ADAPTER_CLASSES` 已移除），而是通过插件运行时装配（规格：[requirements/phase-1.1-pluggable-file-capability-runtime-v0.1.md](./requirements/phase-1.1-pluggable-file-capability-runtime-v0.1.md)）：

```text
read_artifact()            ← Stable Facade（Phase 1/2 调用方式不变）
      ↓
CapabilityRuntime.execute(CapabilityRequest)
      ↓
CapabilityRegistry         ← 内置插件 + HMBUDDY_PLUGIN_PATH 外部插件自动发现注册
      ↓
Router（确定性规则：capability → supports → availability → 权限 → priority → tie-break）
      ↓
CapabilityProvider（插件）
      ↓
Adapter / API / COM（插件内部实现技术）
      ↓
Artifact（Core Contract，provenance 增加 plugin_id / provider_id / plugin_version）
```

- 插件以 `plugin.json` Manifest 声明 id/版本/api_version/能力/权限（规格第 9 节允许 JSON 以减少运行依赖）；
- 新增文件能力**不需要修改 Core**：把插件目录放入 `HMBUDDY_PLUGIN_PATH` 即被自动发现（`plugins/examples/markdown_reader` 是可运行的最小示例）；
- 单插件加载失败被隔离记录，不影响其他插件；fallback 全程可观察（trace 记录 `fallback_from`）；
- 权限是 Runtime Policy 而非 OS 沙箱：默认只授予 `filesystem.read`，声明与授权可列出观察；
- Context Hardening：全局字符/块预算、XLSX 解析期截断可见、PDF 页级 OCR 标记、绝对路径默认不进入 LLM Context。

### 契约加固（Phase 1.1.1）

在 1.1 机制层之上收口治理层与 Workspace 集成层（规格：[requirements/phase-1.1.1-plugin-runtime-contract-hardening-v0.1.md](./requirements/phase-1.1.1-plugin-runtime-contract-hardening-v0.1.md)）：

- **权限强阻断（BUG-001）**：Provider 声明 `required_permissions`，Runtime 在 execute 前强校验；`context.require_permission()` 提供动态权限接口（XLS 的 xlrd 路径只需 `filesystem.read`，COM fallback 前必须申请 `office.com`）；默认 Policy 下 `.doc` 不会实际启动 Word/WPS。
- **Capability Catalog（BUG-002）**：Workspace 支持格式从 Registry 派生，安装全新扩展名（如 `.foo`）的插件后 Workspace 自动发现并可读取，全程不改 Core。
- **Manifest 权威（BUG-003/004）**：plugin_id/version/priority/extensions/permissions 由 Loader 从 Manifest 强制注入 Provider；Registry 只注册 Loader 校验过的同一批 Provider 实例。
- **Ref 信任域（BUG-007）**：Workspace 生成的 ArtifactRef 携带 `workspace_id`，脱离原 Workspace 读取会被拒绝。
- **可用性路由（BUG-008）**：Manifest platforms / python_requires / 依赖探针真实参与路由，不满足的 Provider 报 `ProviderNotAvailableError` 并给出原因。
- **ArtifactLocator（BUG-009）**：`ArtifactBlock.locator` 进入核心契约，四种格式按 scheme 生成稳定定位；`location` 仅为兼容保留。
- **其他**：`success=False` 强制转为失败（BUG-010）、选择阶段异常可诊断（BUG-011）、fallback 显式 allowlist（BUG-012）、外部插件支持标准 package 与相对 import（BUG-013）、删除静态 `ARTIFACT_TYPES`（BUG-014）、trace 时间正确且有界（BUG-015）、GitHub Actions 覆盖 3.10/3.12 × Windows/Linux + wheel 安装态 smoke（BUG-017）。

例如：

- 文件列表来自 `Workspace.list_artifacts()`；
- 文件读取来自 `read_artifact()`；
- 问答来自 `client.ask(artifact, question)`；
- UI 不直接调用具体格式 Adapter，也不感知插件体系。

Phase 1 的设计原则（规格第 5 节）：

- **P2 格式隔离**：`if suffix == ".docx"` 这类判断只存在于 Adapter 层，上层（含 Context 渲染）只面向 `block_type` 工作；
- **P3 Artifact 是统一核心对象**：所有格式进入上层后都是 `Artifact`；
- **P4 保留结构不过早统一**：统一顶层模型 + 格式特有的 Block 结构。

### 能力来源（fce 拆解融入）

| fce 原有能力 | 现位置 |
|---|---|
| 矢量线表格引擎（连通分量、union-find 合并单元格、表头识别、重复表头面板拆分、跨页续表链接） | `adapters/pdf_tables.py`（几何采集层改用 pdfplumber 原语，算法保真移植） |
| 表格契约（rowspan/colspan/bbox/置信度/续表链） | `adapters/tables.py` |
| OCR 管线（懒加载 PaddleOCR、超大图分片、后处理规范化、SLANet 表格结构识别） | `adapters/ocr/` |
| 多编码纯文本解析 | `adapters/text.py` |
| .xls（xlrd/COM）、.doc（Word/WPS COM） | `adapters/xls.py`、`adapters/doc_legacy.py` |
| DOCX 嵌套表格、单元格文本/数值规范化 | `adapters/docx.py`、`adapters/textnorm.py` |

未移植：excel/json/markdown 输出器、GUI、doctor、benchmark（输出与工具类，超出 adapters 只读范围，按真实需要再引入）。fce/ 目录已从工作区移除，融入的代码保留了原实现的行为与边界注释。

---

## 5. 目录结构

```text
app.py                       Phase 1 CLI 演示入口
desktop/                     Phase 2 桌面应用层
  __init__.py
  app.py                     Tkinter 页面、事件、后台线程
  presenter.py               Artifact → UI 文本格式化
workspace/                   Workspace、ArtifactRef、Artifact/ArtifactBlock、错误类型
plugin_runtime/              Phase 1.1 插件运行时内核
  contracts.py               CapabilityRequest/Result、ArtifactLocator、Provider/Plugin 协议
  manifest.py                plugin.json 解析与校验
  discovery.py / loader.py   内置 + 外部插件发现与加载（故障隔离）
  registry.py / router.py    能力注册、确定性路由（priority + tie-break）
  policy.py / runtime.py     权限策略、execute + trace + fallback
plugins/                     文件能力插件（plugin.json + plugin.py）
  docx/ doc_legacy/ pdf/ xlsx/ xls/ pptx/ text/
  examples/markdown_reader/  外部插件最小示例（HMBUDDY_PLUGIN_PATH 引入）
adapters/                    具体解析实现（由插件包装使用，不再被 Core 静态引用）
  adapters/pdf_tables.py     PDF 矢量线表格引擎
  adapters/ocr/              PaddleOCR / SLANet 表格结构识别（懒加载、默认关闭）
services/                    Stable Facade：read_artifact() 单一入口
llm/                         artifact_to_context() + OpenAI 兼容客户端
evals/                       Parser / 表格 / 文本 / OCR / Context / QA / 插件化 Eval + baseline
evals/fixtures/              8 个标准测试样例（已提交，生成脚本 generate_fixtures.py）
tests/                       领域模型 / 错误 / Workspace / 插件运行时 / 桌面 presenter 单元测试
requirements/                分阶段需求规格说明书
start_hmbuddy_desktop.bat    Windows 双击启动入口
```

---

## 6. Phase 1 核心能力

给定一个本地工作目录，系统可以：

1. **发现**目录中的 DOCX / PDF / XLSX / XLS / PPTX / DOC / TXT / MD / CSV 等格式（过滤临时、隐藏、不支持文件）；
2. 统一通过 `read_artifact()` 读取任意支持格式，格式路由在内部完成；
3. **保留结构**（标题层级、表格网格与合并单元格、单元格公式、页码/页归属、幻灯片顺序、跨页续表），而不是把文件压成一大段纯文本；
4. 将 Artifact 渲染成对 LLM 友好的 Context；
5. 在用户明确指定文件的前提下完成内容问答（可选：对无文本层扫描件执行 OCR）。

关键接口：

```python
from workspace.workspace import Workspace
from services.artifact_reader import read_artifact
from llm.context import artifact_to_context

# 1. 发现（G1）
refs = Workspace("D:/工作目录").list_artifacts()   # -> list[ArtifactRef]

# 2. 读取（G2/G3）：上层不感知格式差异
artifact = read_artifact("报表.xlsx")              # 也接受 ArtifactRef
artifact.blocks            # heading/paragraph/table/text_block/textbox/slide...
artifact.provenance        # adapter / read_at / parse_duration_ms / file_sha256 ...

# 3. 交给 LLM（G4）
context = artifact_to_context(artifact)
```

表格 block 的 metadata 统一携带：`cells`（span 展开网格）、`cells_merged`（合并锚点，rowspan/colspan）、`extraction_method`、`confidence`、`repeated_header_row`、`continuation_id` / `continues_from_previous` / `continued_on_next`（PDF 跨页续表）。

错误类型（规格第 18 节）：

| 错误 | 场景 |
|---|---|
| `UnsupportedArtifactTypeError` | 不支持的格式（ER-01） |
| `ArtifactNotFoundError` | 文件不存在 |
| `WorkspaceBoundaryError` | 路径逃逸 Workspace 根目录（ER-05） |
| `ArtifactTooLargeError` | 超过大小阈值，默认 50 MB，可配置（ER-04） |
| `ArtifactParseError` | 文件损坏等解析失败，记录 adapter 与原始错误（ER-02） |
| `EncryptedArtifactError` | 加密 / 密码保护 / OLE 魔数（ER-03） |

---

## 7. 测试

```bash
python -m pytest -q                                   # 全部 Eval（数量以 baseline 为准）
python evals/fixtures/generate_fixtures.py            # 重新生成测试样例
```

- Parser Eval：8 个样例 100% 无异常读取；
- 表格 Eval：矢量网格重建、表头识别、跨页续表链接、DOCX 合并/嵌套表格；
- OCR Eval：分片/行分组/后处理规则（纯逻辑，无需 paddle 环境）+ 模型缺失降级；
- Context Eval：问题所需事实必须进入 Context（区分 Parser Error 与 Context Error）；
- 插件化 Eval：Manifest 校验（T1）、发现/加载/故障隔离（T2/T7）、Registry priority（T3/AC-05）、路由（T4/AC-01/02）、权限（T8/AC-07）、fallback trace、外部 Markdown 插件验收（T6/AC-04）、Context Hardening（T9）；
- 1.1.1 加固 Eval：权限强阻断、`.foo` 全新扩展名全链路、Manifest 权威、Provider 单次物化、external_plugin_dirs 直连、默认 Context 预算、Ref 信任域、可用性路由、Locator、success 语义、选择诊断、fallback allowlist、package 插件；
- QA Eval：配置 LLM 环境变量后运行真实问答（关键词校验）；
- Baseline：[evals/baseline-phase1.1.1-v0.1.json](./evals/baseline-phase1.1.1-v0.1.json)（当前；历史 phase1.1 / phase1-v0.1 / v0.2 见同目录）。

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

## 8. 当前边界与已知限制

当前仍然是 **Human-in-the-loop**，明确不做：

- Agent 自主选择文件；
- Workspace 语义搜索；
- 多文件自动比较；
- Tool Calling Loop；
- Planner；
- Word / Excel / PPT 写回；
- 自动覆盖原文件；
- 任务持久化与中断恢复。

已知限制（完整清单见 baseline JSON 的 `known_limitations`）：openpyxl 生成的公式样例没有计算缓存；PDF 表格需要几何边框线（无线表格回退 pdfplumber）；.doc 只能取纯文本；OCR 默认关闭且模型需本地放置；CSV 按纯文本读取。

这些能力是否进入下一阶段，由桌面入口投入真实使用后出现的失败模式决定，而不是为了凑完整 Agent 架构提前实现。
