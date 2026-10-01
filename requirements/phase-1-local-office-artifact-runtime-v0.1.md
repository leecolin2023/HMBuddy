# 内网办公 Agent 第一阶段需求规格说明书

**项目阶段：** Phase 1 / Milestone 0  
**版本：** V0.1  
**阶段主题：** Local Office Artifact Runtime  
**文档目的：** 作为第一阶段开发、测试和验收的统一依据，并可直接交给开发 Agent 按阶段实施。

---

## 1. 项目背景

本项目最终目标是构建一个适用于企业内网、可离线运行的办公 Agent。

长期来看，系统可能具备：

- 工作区文件发现；
- Word / PDF / Excel / PowerPoint 理解与修改；
- 多文件比较；
- 持续维护同一工作成果；
- 任务状态保存与恢复；
- 文件变更影响分析；
- Skills；
- Memory；
- Planner；
- 工具调用；
- 任务执行与验证。

但第一阶段不直接实现完整 Agent。

原因是：

如果从一开始同时引入文件搜索、LLM Tool Calling、Planner、RAG、状态管理和文件修改，一旦任务失败，将难以判断问题究竟来自：

- 文件没有被正确解析；
- 文件结构丢失；
- Agent 选择错文件；
- Agent 选择错工具；
- LLM 理解错误；
- Context 组织错误；
- 文件修改逻辑错误；
- Planner 错误。

因此第一阶段只解决一个更基础的问题：

> **本地 Office 文件能否被系统稳定发现、统一读取、保留必要结构，并转化为上层 LLM / Agent 可以可靠消费的 Artifact。**

本阶段不要求 Agent 自主决定读什么。

---

## 2. 第一阶段核心问题

第一阶段只回答：

> **给定一个本地工作目录，系统能否可靠地知道里面有什么，并以统一方式读取 DOCX、PDF、XLSX、PPTX，使上层不再需要关心文件格式差异？**

目标链路为：

```text
Local Workspace
      ↓
发现文件
      ↓
识别文件类型
      ↓
选择对应 Adapter
      ↓
解析文件
      ↓
转换为统一 Artifact
      ↓
交给 LLM
      ↓
回答文件内容与结构问题
```

---

## 3. 阶段目标

本阶段完成后，系统至少应具备以下四项能力。

### G1. Workspace 文件发现

给定一个本地目录，可以：

- 遍历目录；
- 发现支持的办公文件；
- 获取基础文件元数据；
- 忽略临时文件、隐藏文件及不支持文件；
- 为文件生成稳定的 Artifact ID。

### G2. 多格式统一读取

支持：

- DOCX；
- PDF；
- XLSX；
- PPTX。

上层统一通过：

```python
read_artifact(...)
```

读取。

上层不需要直接调用：

```text
read_docx
read_pdf
read_xlsx
read_pptx
```

具体文件类型路由由 Artifact Runtime 内部完成。

### G3. 保留办公文件结构

读取结果不能退化成单纯：

```text
一大段纯文本
```

至少需要保留影响后续理解和修改的基本结构。

例如：

```text
DOCX
├─ heading
├─ paragraph
├─ table
└─ image reference

XLSX
├─ workbook
├─ sheet
├─ range
├─ cell
├─ formula
└─ merged cell

PPTX
├─ slide
├─ textbox
├─ table
└─ image reference

PDF
├─ page
├─ text block
├─ table
└─ image reference
```

### G4. LLM 基于 Artifact 正确理解文件

在用户明确指定文件的情况下：

```text
用户
→ 指定文件
→ read_artifact
→ Artifact
→ LLM
→ 回答问题
```

能够完成：

- 文件内容问答；
- 结构问答；
- 表格内容理解；
- 指定位置内容提取；
- 文件基本摘要。

本阶段不要求 LLM 自己寻找文件。

---

## 4. 非目标

以下能力明确不属于第一阶段。

### 4.1 Agent 自主决策

暂不实现：

- Agent 自己决定应该读哪个文件；
- Tool Calling Loop；
- Planner；
- 多步骤自主规划。

### 4.2 工作区智能搜索

暂不实现完整：

```text
search_workspace(query)
```

可以预留接口，但不作为本阶段验收项。

### 4.3 文件修改

暂不实现：

- update_docx；
- update_xlsx；
- update_pptx；
- semantic patch；
- 文件自动覆盖。

第一阶段只读。

### 4.4 文件比较

暂不实现：

```text
compare_artifacts()
```

第二阶段再加入。

### 4.5 RAG

暂不实现：

- chunking pipeline；
- embedding；
- vector database；
- reranker；
- hybrid search。

第一阶段直接读取指定文件。

### 4.6 Agent 高级能力

暂不实现：

- Memory；
- MCP；
- Multi-Agent；
- Task State；
- Checkpoint；
- Resume；
- Skills 动态加载；
- Dependency Graph；
- Change Impact；
- 自动长期任务。

---

## 5. 核心设计原则

### P1. LLM 处理语义不确定性，程序处理确定性

例如：

```text
.docx 应该由哪个 parser 读取
```

属于确定性问题，应由程序负责。

未来类似：

```text
这三个文件哪个与当前任务最相关
```

属于语义不确定性，应由 Agent 负责。

### P2. 文件格式差异必须被 Adapter 隔离

上层业务代码不得出现：

```python
if suffix == ".docx":
    ...
elif suffix == ".xlsx":
    ...
```

这类判断只能存在于 Artifact Runtime / Adapter 层。

### P3. Artifact 是统一核心对象

DOCX、PDF、XLSX、PPTX 在进入上层后，都表现为：

```text
Artifact
```

上层代码围绕 Artifact 工作，而不是围绕具体文件格式工作。

### P4. 保留结构，不追求过早统一

统一 Artifact 不等于把所有文件压成同一种纯文本。

应采用：

```text
统一顶层模型
+
格式特有 Structure
```

而不是为了 schema 简洁损失信息。

### P5. 第一阶段只解决读取可靠性

如果 Artifact Runtime 本身还不稳定，不引入 Agent Planner 等上层复杂度。

---

## 6. 总体架构

```text
                  Application
                      │
                      ▼
                 LLM Interface
                      │
                      ▼
               Artifact Service
                      │
                read_artifact()
                      │
              ┌───────┴────────┐
              ▼                ▼
        Workspace          Artifact Model
              │
              ▼
          Adapter Router
              │
    ┌─────────┼─────────┬─────────┐
    ▼         ▼         ▼         ▼
 DOCX       PDF       XLSX      PPTX
Adapter    Adapter    Adapter    Adapter
    │         │         │         │
    └─────────┴─────────┴─────────┘
                      │
                Local Filesystem
```

---

## 7. 推荐工程目录

```text
office-agent/
│
├── app.py
│
├── workspace/
│   ├── __init__.py
│   ├── workspace.py
│   └── artifact.py
│
├── adapters/
│   ├── __init__.py
│   ├── base.py
│   ├── docx.py
│   ├── pdf.py
│   ├── xlsx.py
│   └── pptx.py
│
├── services/
│   ├── __init__.py
│   └── artifact_reader.py
│
├── llm/
│   ├── __init__.py
│   └── client.py
│
├── evals/
│   ├── fixtures/
│   │   ├── sample.docx
│   │   ├── sample.pdf
│   │   ├── sample.xlsx
│   │   └── sample.pptx
│   │
│   ├── test_workspace.py
│   ├── test_artifact_reader.py
│   ├── test_docx.py
│   ├── test_pdf.py
│   ├── test_xlsx.py
│   └── test_pptx.py
│
├── tests/
│
├── README.md
└── pyproject.toml
```

该结构是第一版建议，不要求为了架构美观进一步拆包。

---

## 8. 核心领域对象

### 8.1 Workspace

Workspace 代表当前允许系统操作的本地工作目录。

建议：

```python
class Workspace:
    root_path: Path

    def list_artifacts(self) -> list[ArtifactRef]:
        ...
```

#### 职责

Workspace 只负责：

- 工作目录边界；
- 文件发现；
- 文件基础元数据；
- ArtifactRef 生成。

不负责解析文件内容。

### 8.2 ArtifactRef

用于表达“存在一个文件”，但尚未读取其正文。

建议结构：

```python
@dataclass
class ArtifactRef:
    artifact_id: str
    name: str
    path: str
    extension: str
    size: int
    modified_at: datetime
    artifact_type: str
```

### 8.3 Artifact

核心统一对象。

建议第一版：

```python
@dataclass
class Artifact:
    artifact_id: str
    name: str
    path: str
    artifact_type: str

    metadata: dict

    content: str

    blocks: list["ArtifactBlock"]

    provenance: dict
```

### 8.4 ArtifactBlock

所有文件内部内容最终转换为 Block。

基础结构：

```python
@dataclass
class ArtifactBlock:
    block_id: str
    block_type: str
    text: str | None

    location: dict
    metadata: dict
```

例如：

#### Word Heading

```json
{
  "block_id": "b001",
  "block_type": "heading",
  "text": "一、项目背景",
  "location": {
    "paragraph_index": 3
  },
  "metadata": {
    "level": 1
  }
}
```

#### Excel Cell Range

```json
{
  "block_id": "b021",
  "block_type": "table",
  "location": {
    "sheet": "资产负债表",
    "range": "A1:F30"
  }
}
```

---

## 9. Workspace 功能需求

### FR-W01 扫描 Workspace

接口：

```python
workspace.list_artifacts()
```

必须：

- 遍历 Workspace；
- 支持递归目录；
- 返回支持格式；
- 返回基础 metadata。

### FR-W02 支持格式

第一阶段支持：

```text
.docx
.pdf
.xlsx
.pptx
```

可以额外支持：

```text
.txt
.md
```

但不作为核心验收项。

### FR-W03 忽略临时文件

例如：

```text
~$xxx.docx
.DS_Store
隐藏文件
临时缓存文件
```

不得被识别为有效 Artifact。

### FR-W04 Workspace 边界

Artifact Runtime 默认不得读取 Workspace 根目录之外的文件。

这是未来权限控制的基础。

第一阶段至少进行路径检查，防止：

```text
../
```

越界访问。

---

## 10. Artifact Reader 功能需求

### FR-A01 单一入口

统一提供：

```python
read_artifact(path_or_ref)
```

禁止上层直接依赖具体 Adapter。

### FR-A02 自动 Adapter 路由

内部：

```text
.docx → DocxAdapter
.pdf  → PdfAdapter
.xlsx → XlsxAdapter
.pptx → PptxAdapter
```

### FR-A03 Reader 输出一致

所有 Adapter 必须返回：

```text
Artifact
```

不得各自返回完全不同的数据格式。

### FR-A04 保留 provenance

每个 Artifact 至少保留：

```text
原文件路径
文件类型
读取时间
文件修改时间
parser / adapter
```

为未来：

```text
版本
引用
Diff
审计
```

提供基础。

---

## 11. DOCX Adapter 要求

第一阶段至少读取：

- Paragraph；
- Heading；
- Table；
- Section 顺序；
- 基础列表；
- 图片位置引用。

最低要求：

```text
原始阅读顺序不能明显错乱。
```

### Table

表格不得只被压成一句文本。

应至少记录：

```text
rows
columns
cell text
table position
```

### Heading

必须保留：

```text
heading level
```

因为未来：

```text
语义定位
章节修改
Diff
```

都会依赖 Heading。

---

## 12. PDF Adapter 要求

PDF 第一阶段优先处理：

> **存在文本层的 PDF。**

至少保留：

```text
page number
text blocks
table（能力允许时）
```

第一阶段不强制 OCR。

处理策略：

```text
有文本层
→ 直接解析

无文本层
→ 标记 requires_ocr=true
```

暂不自动执行复杂 OCR Pipeline。

---

## 13. XLSX Adapter 要求

Excel 不允许简单转成：

```text
整张表 CSV 文本
```

至少保留：

```text
Workbook
  ↓
Sheet
  ↓
Used Range
  ↓
Cell
```

单元格至少记录：

```text
value
formula
row
column
```

如果存在：

```text
merged cells
```

需要保留 merged range 信息。

建议读取结果支持：

```python
artifact.metadata["sheets"]
```

以及：

```text
blocks:
sheet/table/range
```

---

## 14. PPTX Adapter 要求

至少读取：

```text
slide index
slide title
textbox
table
image reference
```

保证：

```text
内容与 slide 顺序一致
```

不要求第一阶段识别复杂视觉布局语义。

例如暂不需要判断：

```text
左侧是问题
右侧是解决方案
```

但必须知道：

```text
这些内容位于第几页。
```

---

## 15. read_artifact 输出模式

为了给后续扩展留下空间，建议第一版接口设计为：

```python
read_artifact(
    artifact,
    mode="full"
)
```

第一阶段只实现：

```text
full
```

但接口预留未来：

```text
metadata
outline
range
sheet
slide
page
search
```

暂时不要提前实现这些模式。

---

## 16. LLM Interface

本阶段 LLM 不允许决定工具。

流程固定：

```text
用户选择 Artifact
        ↓
read_artifact
        ↓
Artifact
        ↓
构造 Context
        ↓
LLM
        ↓
回答
```

例如：

```python
artifact = read_artifact("资产池方案.docx")

answer = llm.ask(
    artifact=artifact,
    question="这份方案包含哪些主要流程？"
)
```

---

## 17. LLM Context 构造

不得简单：

```python
prompt += str(artifact)
```

建议建立：

```python
artifact_to_context(artifact)
```

转换为模型友好的结构。

例如：

```text
[Document]
Name: 资产池需求方案.docx
Type: DOCX

[Heading 1]
一、项目背景

[Paragraph]
......

[Heading 1]
二、业务流程

[Table]
| 阶段 | 操作 | 责任主体 |
...
```

Excel：

```text
[Workbook]
财务报表.xlsx

[Sheet]
资产负债表

[Range A1:F20]
...
```

目标：

> Artifact 内部模型面向程序，Context Representation 面向 LLM。

两者不要混为一个对象。

---

## 18. 错误处理

第一阶段必须显式处理：

### ER-01 不支持格式

返回：

```text
UnsupportedArtifactType
```

不能静默失败。

### ER-02 文件损坏

返回：

```text
ArtifactParseError
```

并记录：

```text
path
adapter
error
```

### ER-03 密码保护

如果检测到：

```text
encrypted / protected
```

明确返回错误状态。

### ER-04 超大文件

第一阶段可以配置阈值。

例如：

```text
50 MB
```

超过阈值不强行加载，返回：

```text
ArtifactTooLarge
```

未来再实现分段读取。

### ER-05 Workspace 越界

路径不允许逃逸 Workspace。

---

## 19. 测试要求

本项目从第一阶段开始建立 Eval，不等 Agent 做完以后再补。

至少准备：

```text
1 个标准 DOCX
1 个复杂 DOCX
1 个标准 PDF
1 个标准 XLSX
1 个多 Sheet XLSX
1 个标准 PPTX
```

建议尽早加入真实办公文件脱敏样例。

---

## 20. Parser 测试

### TC-DOCX-01

输入：

```text
包含三级标题、正文、表格的 DOCX
```

检查：

- 标题顺序；
- heading level；
- paragraph 数量；
- table 内容；
- block 顺序。

### TC-PDF-01

检查：

- page 数；
- page text；
- page attribution；
- 文本顺序。

### TC-XLSX-01

检查：

- sheet 数；
- sheet 名；
- formula；
- value；
- merged cells；
- used range。

### TC-PPTX-01

检查：

- slide 数；
- title；
- textbox；
- table；
- slide attribution。

---

## 21. LLM 理解 Eval

Parser 正确并不代表最终效果正确。

还需要建立端到端测试。

例如 DOCX：

```text
问题：
“文档第二章主要解决什么问题？”
```

Excel：

```text
问题：
“2025 年营业收入是多少？”
```

PPT：

```text
问题：
“第 5 页提出了哪三个问题？”
```

PDF：

```text
问题：
“报告对主要风险的结论是什么？”
```

---

## 22. 第一阶段验收指标

本阶段不需要复杂 Benchmark，但至少记录以下指标。

### A. 文件发现成功率

支持格式文件：

```text
发现率 = 100%
```

### B. Parser 成功率

Eval fixtures：

```text
无异常读取 = 100%
```

### C. 结构保真

人工检查：

```text
标题
段落
表格
Sheet
Slide
Page
```

不能出现明显顺序错误或结构丢失。

### D. 基础事实问答

基于标准测试文件：

```text
明确事实类问题正确率目标 ≥ 95%
```

错误必须能区分：

```text
Parser Error
Context Error
LLM Error
```

---

## 23. Logging

每次读取至少记录：

```text
artifact_id
path
type
adapter
file_size
parse_duration
parse_status
error
```

未来 Agent Debug 会高度依赖这些信息。

不要等 Agent 出现问题后才增加日志。

---

## 24. 第一阶段实施顺序

开发 Agent 应严格按照以下顺序推进。

### Step 1 — 建立项目骨架

完成：

```text
workspace/
adapters/
services/
llm/
evals/
```

暂不写复杂实现。

### Step 2 — Artifact Domain Model

先定义：

```text
ArtifactRef
Artifact
ArtifactBlock
Workspace
```

并写单元测试。

如果领域模型尚不稳定，不开始四种 Adapter。

### Step 3 — Workspace Scanner

实现：

```python
list_artifacts()
```

验收：

```text
能够正确列出一个测试目录中的 DOCX/PDF/XLSX/PPTX。
```

### Step 4 — Base Adapter Interface

建立：

```python
class ArtifactAdapter:
    def supports(...)
    def read(...)
```

确定所有 Adapter 的公共契约。

### Step 5 — DOCX Adapter

先只做 DOCX。

原因：

- Office 知识工作典型；
- 同时包含标题、正文、表格；
- 足够验证 Artifact 模型。

DOCX 未稳定前，不同时开发四种格式。

### Step 6 — ArtifactReader

实现：

```python
read_artifact()
```

做到：

```text
path
→ router
→ adapter
→ Artifact
```

### Step 7 — PDF Adapter

先支持文本 PDF。

OCR 留待后续。

### Step 8 — XLSX Adapter

重点验证：

```text
Sheet / Cell / Formula / Range
```

### Step 9 — PPTX Adapter

完成 slide-level 结构读取。

### Step 10 — Artifact → LLM Context

实现：

```python
artifact_to_context()
```

确保不同文件进入 LLM 后具有可理解结构。

### Step 11 — LLM QA

用户手工指定文件：

```text
文件
+
问题
↓
答案
```

不加入自动找文件。

### Step 12 — 建立第一轮 Eval

完成：

```text
Parser Eval
+
LLM QA Eval
```

记录 baseline。

---

## 25. 每一步开发 Agent 的工作方式

开发 Agent 每完成一个 Step，应输出：

```text
1. 本步解决的问题
2. 修改的文件
3. 核心设计
4. 测试
5. 测试结果
6. 当前已知限制
7. 是否满足进入下一步的条件
```

不得直接连续实现多个阶段而不验证。

---

## 26. 禁止的开发行为

第一阶段明确禁止：

### 禁止 1

因为“以后可能需要”而提前增加：

```text
Planner
Memory
MCP
RAG
Vector DB
Multi-Agent
```

### 禁止 2

为了统一 schema 把：

```text
Excel
Word
PPT
```

全部粗暴转成 Markdown 字符串。

### 禁止 3

四种文件解析逻辑散落到业务代码。

### 禁止 4

一开始直接使用 LLM 自动 Tool Calling。

### 禁止 5

没有 Eval 就继续堆功能。

### 禁止 6

为了学习技术而加入与当前真实问题无关的技术。

每增加一个组件必须回答：

> **它解决了当前哪个已经观察到的问题？**

---

## 27. 第一阶段完成定义 Definition of Done

满足以下全部条件才算完成。

- [ ] Workspace 能稳定扫描测试目录；
- [ ] ArtifactRef 模型稳定；
- [ ] DOCX / PDF / XLSX / PPTX 均有独立 Adapter；
- [ ] 上层只使用 `read_artifact()`；
- [ ] 所有格式统一返回 Artifact；
- [ ] Artifact 保留必要结构；
- [ ] PDF page 信息保留；
- [ ] DOCX heading / paragraph / table 保留；
- [ ] XLSX sheet / value / formula 保留；
- [ ] PPTX slide / text / table 保留；
- [ ] 路径不可越过 Workspace；
- [ ] 读取异常有明确错误类型；
- [ ] Artifact 可以转换成 LLM Context；
- [ ] 用户指定文件后 LLM 能进行基础内容问答；
- [ ] Parser Eval 已建立；
- [ ] LLM QA Eval 已建立；
- [ ] 已形成第一版 benchmark / baseline；
- [ ] README 能让新的开发者独立运行项目。

---

## 28. 第一阶段结束后再决定第二阶段

Phase 1 完成后，不自动进入某个既定技术路线。

先根据实际运行观察问题。

如果发现：

> 人工指定文件成本明显很高

进入：

```text
Phase 2 — Workspace Discovery
```

如果发现：

> 多版本文件差异判断成本高

进入：

```text
Artifact Compare
```

如果发现：

> 读取稳定，但修改办公文档困难

进入：

```text
Artifact Update / Semantic Patch
```

如果发现：

> Agent 已经拥有多个工具，选择和执行开始变复杂

才进入：

```text
Agent Loop / Tool Calling
```

后续技术应由真实失败推动，而不是预先按照“完整 Agent 架构图”添加。

---

## 29. 推荐的完整演进路线

当前只实施 Phase 1，下面仅用于明确未来关系：

```text
Phase 1
Local Office Artifact Runtime
读取文件

        ↓

Phase 2
Workspace Discovery
找到正确文件

        ↓

Phase 3
Artifact Compare
理解文件变化

        ↓

Phase 4
Artifact Update
可靠修改文件

        ↓

Phase 5
Agent Loop
自主决定找 / 读 / 比 / 改

        ↓

Phase 6+
根据真实问题逐步引入
Task State / Checkpoint
Skills
Memory
RAG
MCP
Planner
Change Impact
```

---

## 30. 本阶段最终产物

Phase 1 最终应形成：

```text
office-agent/
+
Local Office Artifact Runtime
+
4 类 Office Adapter
+
统一 Artifact Model
+
LLM Context Builder
+
Parser Eval
+
LLM QA Eval
+
README
+
Baseline
```

最终 Demo 不需要复杂 UI。

最小演示即可：

```bash
python app.py ./workspace/资产池需求方案.docx
```

系统：

```text
成功读取：
类型：DOCX
标题：资产池需求方案
Heading：12
Paragraph：86
Table：4
```

随后：

```text
请输入问题：
> 这份方案主要包含哪些业务流程？
```

系统根据 Artifact 内容回答。

---

## 31. 第一阶段最核心的工程命题

整个 Phase 1 最终不是为了证明：

> “我们会用 Python 读取 Office 文件。”

真正要验证的是：

> **Office 文件是否可以被建模成一种稳定的、结构化的、与具体文件格式解耦的 Artifact，使未来 Agent 可以围绕 Artifact 工作，而不是围绕 DOCX / XLSX / PPTX API 工作。**

如果这个基础成立，后续才能逐渐讨论：

```text
发现 Artifact
比较 Artifact
修改 Artifact
维护 Artifact
追踪 Artifact 变化
Agent 自主操作 Artifact
```

这才是第一阶段存在的真正意义。
