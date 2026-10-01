# HMBuddy — Phase 1: Local Office Artifact Runtime

适用于企业内网、可离线运行的办公 Agent 项目的第一阶段：**把本地 Office 文件稳定地发现、统一读取、保留结构，并转化为上层 LLM 可靠消费的 Artifact**。

需求依据：[requirements/phase-1-local-office-artifact-runtime-v0.1.md](./requirements/phase-1-local-office-artifact-runtime-v0.1.md)

## 它解决什么问题

给定一个本地工作目录，系统可以：

1. **发现**目录中的 DOCX / PDF / XLSX / PPTX（过滤临时、隐藏、不支持文件）；
2. 通过统一入口 `read_artifact()` **读取**任意支持格式，格式路由在内部完成；
3. **保留结构**（标题层级、表格网格、单元格公式、页码/页归属、幻灯片顺序），不把文件压成一坨纯文本；
4. 把 Artifact 渲染成对 LLM 友好的 **Context**，在用户指定文件的前提下完成内容问答。

第一阶段**只读**。不做 Agent 自主决策、文件搜索、文件修改、比较、RAG（见规格第 4 节非目标）。

## 快速开始

```bash
# Python >= 3.10
pip install -e ".[dev]"        # 或 pip install python-docx pdfplumber openpyxl python-pptx pytest fpdf2

# 运行全部测试（83 项：单元测试 + Parser Eval + Context Eval；4 项 LLM Eval 需要环境变量）
python -m pytest -q

# 最小演示：读取文件并打印结构摘要（规格第 30 节的验收形态）
python app.py evals/fixtures/sample.docx --no-llm
python app.py evals/fixtures/sample.xlsx --show-context

# 扫描一个目录
python app.py evals/fixtures --scan
```

### 接入 LLM 问答（OpenAI 兼容协议，可指向内网私有化端点）

```bash
export HMBUDDY_LLM_BASE_URL=https://llm.intranet.example.com/v1
export HMBUDDY_LLM_MODEL=your-model
export HMBUDDY_LLM_API_KEY=...        # 部分内网部署可留空

python app.py evals/fixtures/sample.docx
# 成功读取后进入交互问答：
# > 这份方案主要包含哪些业务流程？
```

未配置环境变量时，`pytest` 中的 4 项真实 LLM 问答 Eval 会自动跳过，其余全部可离线运行。

## 架构

```text
Application (app.py)
      │
 LLM Interface (llm/)            ask(artifact, question) → Context → LLM
      │
 Artifact Service (services/)    read_artifact() 单一入口 + 路由 + 日志 + 错误处理
      │
 ┌────┴─────────────────────────┐
 Workspace (workspace/)        Artifact Model (workspace/artifact.py)
 文件发现 / 边界 / ArtifactRef    Artifact / ArtifactBlock（统一核心对象）
      │
 Adapter Router → DocxAdapter / PdfAdapter / XlsxAdapter / PptxAdapter (adapters/)
      │
 Local Filesystem
```

核心设计原则（规格第 5 节）：

- **P2 格式隔离**：`if suffix == ".docx"` 这类判断只存在于 Adapter 层，上层（含 Context 渲染）只面向 `block_type` 工作；
- **P3 Artifact 是统一核心对象**：四种格式进入上层后都是 `Artifact`；
- **P4 保留结构不过早统一**：统一顶层模型 + 格式特有的 Block 结构（如 XLSX 的 cell_records、PDF 的页归属）。

## 目录结构

```text
app.py                       演示入口（读取摘要 / 目录扫描 / 交互问答）
workspace/                   Workspace 扫描、ArtifactRef、Artifact/ArtifactBlock、错误类型
adapters/                    ArtifactAdapter 基类 + DOCX/PDF/XLSX/PPTX 四个适配器
services/                    ArtifactReader：read_artifact() 单一入口
llm/                         artifact_to_context() + OpenAI 兼容客户端
evals/                       Parser Eval / Context Eval / QA Eval / baseline
evals/fixtures/              6 个标准测试样例（已提交，生成脚本 generate_fixtures.py）
tests/                       领域模型 / 错误类型 / Workspace 单元测试
requirements/                需求规格说明书
```

## 关键接口

```python
from workspace.workspace import Workspace
from services.artifact_reader import read_artifact
from llm.context import artifact_to_context

# 1. 发现（G1）
refs = Workspace("D:/工作目录").list_artifacts()   # -> list[ArtifactRef]

# 2. 读取（G2/G3）：上层不感知格式差异
artifact = read_artifact("报表.xlsx")              # 也接受 ArtifactRef
artifact.blocks            # [ArtifactBlock(block_type="table", location={"sheet": ..., "range": ...}, ...)]
artifact.metadata["sheets"]
artifact.provenance        # adapter / read_at / parse_duration_ms / file_sha256 ...

# 3. 交给 LLM（G4）
context = artifact_to_context(artifact)
```

## 错误类型（规格第 18 节）

| 错误 | 场景 |
|---|---|
| `UnsupportedArtifactTypeError` | 不支持的格式（ER-01） |
| `ArtifactNotFoundError` | 文件不存在 |
| `WorkspaceBoundaryError` | 路径逃逸 Workspace 根目录（ER-05） |
| `ArtifactTooLargeError` | 超过大小阈值，默认 50 MB，可配置（ER-04） |
| `ArtifactParseError` | 文件损坏等解析失败，记录 adapter 与原始错误（ER-02） |
| `EncryptedArtifactError` | 加密 / 密码保护 / OLE 魔数（ER-03） |

每次读取都会通过 logger `hmbuddy.artifact_reader` 记录：path、type、adapter、artifact_id、file_size、parse_duration_ms、parse_status、error（规格第 23 节）。

## Eval 与 Baseline

```bash
python -m pytest -q                                   # 全部 Eval
python -m pytest evals -q                             # 仅 Parser/Context/QA Eval
python evals/fixtures/generate_fixtures.py            # 重新生成测试样例
```

- Parser Eval：6 个样例 100% 无异常读取，结构断言见 `evals/test_docx.py` / `test_pdf.py` / `test_xlsx.py` / `test_pptx.py`；
- Context Eval：问题所需事实必须进入 Context（区分 Parser Error 与 Context Error）；
- QA Eval：配置 LLM 环境变量后运行真实问答（关键词校验）；
- Baseline 记录：[evals/baseline-phase1-v0.1.json](./evals/baseline-phase1-v0.1.json)。

## 已知限制

见 baseline JSON 的 `known_limitations`。要点：openpyxl 生成的公式样例没有计算缓存（value 为 None，真实 Excel 文件不受影响）；PDF 为行级文本块、扫描件只标记 `requires_ocr`；Artifact ID 基于绝对路径，文件移动后 ID 变化。

## 下一步

按规格第 28 节：Phase 1 完成后先观察真实使用中的失败模式，再决定进入 Workspace Discovery / Artifact Compare / Artifact Update / Agent Loop，不为架构美观提前加组件。
