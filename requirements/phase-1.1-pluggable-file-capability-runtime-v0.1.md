# HMBuddy Phase 1.1 — Pluggable File Capability Runtime 需求规格说明书

**项目阶段：** Phase 1.1 / Architecture Hardening  
**版本：** V0.1  
**阶段主题：** Pluggable File Capability Runtime  
**文档目的：** 在不推翻 Phase 1 Local Office Artifact Runtime、不破坏已完成 Phase 2 Desktop Entry 的前提下，将当前固定的文件 Adapter 路由升级为可发现、可注册、可替换、可扩展的文件能力插件运行时，使文件处理能力成为 HMBuddy 可持续迭代的核心扩展面。

---

## 1. 背景

HMBuddy 的长期定位不是“支持 DOCX / PDF / XLSX / PPTX 四种文件的文档问答工具”，而是：

> **一个以本地工作空间和办公文件为核心、文件处理能力可以持续演化和由用户扩展的内网办公 Agent Harness。**

Phase 1 已完成 Local Office Artifact Runtime，建立了：

- Workspace 文件发现与边界；
- ArtifactRef / Artifact / ArtifactBlock 统一模型；
- DOCX / PDF / XLSX / PPTX 四类 Adapter；
- `read_artifact()` 单一读取入口；
- Artifact → LLM Context；
- Parser / Context / QA Eval 基础。

Phase 2 已在上述 Runtime 之上增加桌面入口，并继续依赖：

```text
Desktop
   ↓
Workspace
   ↓
read_artifact()
   ↓
Artifact
```

当前实现已经证明基础链路可用，但文件能力仍以静态方式绑定：

```python
ADAPTER_CLASSES = (
    DocxAdapter,
    PdfAdapter,
    XlsxAdapter,
    PptxAdapter,
)
```

这意味着：

1. Core 知道有哪些具体格式实现；
2. 新增格式必须修改核心代码；
3. 同一种能力无法存在多个 Provider 并按环境选择；
4. OCR、WPS COM、Office COM、视觉解析、专业文件处理等横向能力缺乏统一挂载位置；
5. 用户自定义“文件处理能力”只能通过修改项目源码实现；
6. 后续 `read / search / compare / update / validate / render` 等能力容易继续堆叠进固定目录和条件分支。

因此，在继续扩展 Artifact Search / Compare / Update / Agent Loop 之前，需要先把文件能力从“内置实现集合”提升为“插件化 Capability Runtime”。

---

## 2. 本阶段核心问题

Phase 1.1 只回答：

> **HMBuddy 能否在 Core 不知道具体文件格式和实现类的前提下，自动发现文件能力插件，将其注册为标准 Capability，并根据文件、能力、环境、权限和优先级选择合适 Provider 执行？**

目标链路：

```text
Application / Desktop / Future Agent
              │
              ▼
        Stable Facade API
        read_artifact(...)
              │
              ▼
       Capability Runtime
              │
      capability request
              │
              ▼
      Capability Registry
              │
        Match / Route
              │
       ┌──────┼───────────┐
       ▼      ▼           ▼
   DOCX     WPS COM      OCR
   Plugin    Plugin      Plugin
       │      │           │
       └──────┴───────────┘
              │
              ▼
         Core Contract
 Artifact / Locator / Result
```

本阶段首先建立插件运行时，不追求增加大量新的文件功能。

---

## 3. 阶段目标

### G1. 建立稳定的 Plugin Contract

Core 必须定义插件可依赖的最小稳定协议，包括：

- Plugin Manifest；
- Capability Definition；
- Capability Request；
- Capability Result；
- Provider Contract；
- Plugin Context；
- Permission Declaration；
- API Version。

插件可以扩展实现，但不得自行改变 Core Contract。

### G2. 建立 Plugin Discovery / Loader / Registry

系统启动时能够：

1. 发现内置插件；
2. 读取 Manifest；
3. 校验插件 ID、版本、API Version、Capabilities 和权限声明；
4. 加载 Provider；
5. 注册到 Capability Registry；
6. 输出可观察的加载结果。

Core 不再通过静态 `ADAPTER_CLASSES` 知道具体实现。

### G3. 由 Capability 驱动，而不是由格式驱动

调用方表达“我要什么能力”，而不是“我要调用哪个 Adapter”。

例如：

```text
artifact.read.full
artifact.read.outline
artifact.search
artifact.compare
artifact.update
artifact.validate
artifact.render
artifact.convert
artifact.ocr
```

Phase 1.1 V0.1 必须实际实现的能力只要求：

```text
artifact.read.full
```

其余 capability namespace 只定义命名规范，不要求实现。

### G4. 将现有四个 Adapter 迁移为 Built-in Plugins

现有：

- DocxAdapter；
- PdfAdapter；
- XlsxAdapter；
- PptxAdapter；

不推翻重写。

它们作为插件内部实现继续使用：

```text
DocxPlugin
   └─ DocxAdapter

PdfPlugin
   └─ PdfAdapter

XlsxPlugin
   └─ XlsxAdapter

PptxPlugin
   └─ PptxAdapter
```

对上层仍保持：

```python
read_artifact(...)
```

兼容。

### G5. 证明“不修改 Core 即可新增文件能力”

新增一个最小 External / Example Plugin，推荐：

```text
Markdown / TXT Reader Plugin
```

验收要求：

> **新增插件时不得修改 Capability Runtime、Registry、Router 和既有 Office Plugin 代码。**

安装 / 放置插件后，Runtime 自动发现并支持：

```text
.md → artifact.read.full
```

这是本阶段证明“真正插件化”的核心验收项。

### G6. 为未来同能力多 Provider 建立路由基础

Registry 必须允许：

```text
artifact.read.full + .docx
```

存在多个 Provider，例如未来：

```text
hmbuddy.docx.ooxml
hmbuddy.wps.com
hmbuddy.office.com
```

V0.1 不要求实现复杂动态择优，但数据模型和路由必须支持：

- priority；
- availability；
- supported environment；
- permissions；
- fallback。

---

## 4. 与 Phase 1 / Phase 2 的关系

### 4.1 不修改 Phase 1 原需求历史

`phase-1-local-office-artifact-runtime-v0.1.md` 保持原样。

原因：

```text
Phase 1 需求
   ↓
Phase 1 实现
   ↓
测试 / baseline
```

已经形成完整工程历史，不应通过修改历史规格来“追认”新架构。

### 4.2 Phase 1.1 是插入式底层架构升级

逻辑演进：

```text
Phase 1
Local Office Artifact Runtime
       ↓
Phase 1.1
Pluggable File Capability Runtime
       ↓
Artifact Search / Compare / Update
       ↓
Agent Runtime
```

### 4.3 不回滚、不重编号已完成的 Phase 2

当前 Phase 2 Desktop Entry 已经存在。

Phase 1.1 实施时必须保持：

```text
desktop/
   ↓
read_artifact()
```

这一调用门面兼容。

桌面层不应感知：

- Plugin Loader；
- Registry；
- Provider；
- Adapter；
- Manifest。

也就是说：

```text
Phase 2 Application Layer
             │
        stable facade
             ▼
       read_artifact()
             │
   Phase 1.1 Runtime replaces
   internal routing only
```

---

## 5. 核心设计原则

### P1. Stable Kernel, Pluggable Capabilities

不是“一切代码皆插件”。

必须保持一个极薄但稳定的 Kernel：

```text
Core
├─ Workspace Boundary
├─ Artifact Contracts
├─ Capability Contracts
├─ Plugin Runtime
├─ Permission / Policy
└─ Trace / Error Boundary
```

变化快、与具体文件处理相关的实现放入插件。

### P2. Capability-first，而不是 Format-first

错误方向：

```text
.docx → DocxAdapter
.xlsx → XlsxAdapter
```

目标方向：

```text
Request:
capability = artifact.read.full
artifact = xxx.docx

Registry:
find providers

Router:
select provider

Provider:
execute
```

文件格式只是 Provider 匹配条件之一，不是架构中心。

### P3. Plugin != Adapter Rename

不能只是：

```text
adapters/docx.py
→
plugins/docx.py
```

否则没有形成插件运行时。

真正插件化至少要求：

- Manifest；
- Discovery；
- Loader；
- Registry；
- Capability Routing；
- API Version；
- Permission Declaration；
- Failure Isolation；
- External Plugin 验收。

### P4. Plugin 可扩展，Core Contract 必须稳定

插件不得向上层返回任意私有对象。

文件读取最终必须返回：

```text
Artifact
```

未来修改、比较、校验等也必须返回对应 Core Contract。

### P5. 程序负责确定性路由，LLM 不参与底层插件选择

Phase 1.1 的 Provider 路由属于确定性基础设施。

不得为了“Agent 化”把：

```text
这个 DOCX 应该调用哪个 Reader
```

交给 LLM。

LLM 未来可以决定“需要什么能力”，Runtime 决定“由哪个 Provider 实现”。

### P6. 可替换但不可静默降级

Fallback 可以存在，但必须可观察。

例如：

```text
python-docx Provider failed
        ↓
WPS COM Provider fallback
```

Trace 必须记录：

- 首选 Provider；
- 失败原因；
- fallback Provider；
- 最终结果。

### P7. 用户扩展能力不等于执行任意代码

用户自定义能力分为两层：

1. Declarative Extension / Skill；
2. Executable Plugin。

普通用户优先使用声明式扩展组合已有能力；Executable Plugin 视为受信代码，需要明确权限和安装来源。

---

## 6. 总体架构

```text
┌─────────────────────────────────────────────┐
│ Application Layer                           │
│ CLI / Desktop / Future Agent                │
└─────────────────────┬───────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│ Stable Facade                               │
│ read_artifact() / future capability APIs    │
└─────────────────────┬───────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────┐
│ Capability Runtime                          │
│ execute(CapabilityRequest)                  │
└───────────────┬─────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────┐
│ Capability Registry                         │
│ Provider registration / query / priority    │
└───────────────┬─────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────┐
│ Router / Policy                             │
│ match → permission → availability → select  │
└───────────────┬─────────────────────────────┘
                │
       ┌────────┼──────────────┐
       ▼        ▼              ▼
   DOCX Plugin XLSX Plugin  Other Plugin
       │        │              │
     Adapter  Adapter        Provider
       └────────┴──────────────┘
                │
                ▼
┌─────────────────────────────────────────────┐
│ Core Contracts                              │
│ Artifact / ArtifactRef / Locator / Result   │
└─────────────────────────────────────────────┘
```

---

## 7. 推荐目录结构

Phase 1.1 不要求一次性为“目录美观”完成大规模搬迁，但最终目标结构建议：

```text
hmbuddy/
├─ core/
│  ├─ artifact/
│  │  ├─ model.py
│  │  ├─ locator.py
│  │  └─ errors.py
│  │
│  ├─ workspace/
│  │  └─ workspace.py
│  │
│  ├─ capabilities/
│  │  ├─ contract.py
│  │  ├─ request.py
│  │  └─ result.py
│  │
│  └─ plugins/
│     ├─ manifest.py
│     ├─ loader.py
│     ├─ registry.py
│     ├─ router.py
│     └─ policy.py
│
├─ plugins/
│  ├─ docx/
│  │  ├─ plugin.yaml
│  │  ├─ plugin.py
│  │  └─ adapter.py
│  ├─ pdf/
│  ├─ xlsx/
│  ├─ pptx/
│  └─ markdown/
│
├─ services/
│  └─ artifact_reader.py
│
├─ desktop/
├─ llm/
├─ evals/
└─ tests/
```

允许 Phase 1.1 V0.1 暂时保留当前：

```text
workspace/
adapters/
services/
```

并增加：

```text
plugins/
plugin_runtime/
```

前提是模块职责符合本规格。

---

## 8. Capability 命名规范

Capability 使用稳定、可组合的字符串 ID。

格式：

```text
<domain>.<verb>[.<mode>]
```

文件核心能力预留：

```text
artifact.read.full
artifact.read.outline
artifact.read.range
artifact.search
artifact.create
artifact.update
artifact.patch
artifact.compare
artifact.validate
artifact.render
artifact.convert
artifact.ocr
```

Phase 1.1 V0.1 必须实现：

```text
artifact.read.full
```

禁止插件自创语义重复但名字不同的 Capability，例如同时出现：

```text
docx.read
word.parse
office.load
artifact.open
```

插件如需新增领域能力，必须使用明确 namespace，例如未来：

```text
financial.statement.detect
financial.statement.normalize
contract.clause.extract
```

---

## 9. Plugin Manifest

每个 Executable Plugin 必须声明 Manifest。

推荐首版使用 YAML；如果为了减少运行依赖，也允许 JSON。实现必须统一一种格式。

示例：

```yaml
id: hmbuddy.docx.core
name: DOCX Core Plugin
version: 0.1.0
api_version: 1

entrypoint:
  module: plugins.docx.plugin
  class: DocxPlugin

accepts:
  extensions:
    - .docx

capabilities:
  - id: artifact.read.full
    priority: 100

permissions:
  - filesystem.read

runtime:
  python: ">=3.10"
  platforms:
    - windows
    - linux
    - darwin
```

### FR-M01 Plugin ID

必须全局唯一。

推荐：

```text
hmbuddy.<name>
user.<name>
org.<name>
```

### FR-M02 Version

插件必须具有 SemVer 风格版本：

```text
major.minor.patch
```

### FR-M03 API Version

Manifest 必须声明：

```text
api_version
```

Runtime 不得加载不兼容 API Version 的插件。

### FR-M04 Capability Declaration

Manifest 必须明确插件提供的 Capability。

不得在加载后偷偷注册 Manifest 未声明能力。

### FR-M05 Permission Declaration

Executable Plugin 必须预声明权限。

首版至少定义：

```text
filesystem.read
filesystem.write
network
process.execute
office.com
wps.com
```

Phase 1.1 Built-in Reader 只应需要：

```text
filesystem.read
```

---

## 10. Plugin Contract

建议基础协议：

```python
class CapabilityProvider(Protocol):
    provider_id: str
    plugin_id: str

    def supports(self, request: CapabilityRequest) -> bool:
        ...

    def is_available(self, context: PluginContext) -> bool:
        ...

    def execute(
        self,
        request: CapabilityRequest,
        context: PluginContext,
    ) -> CapabilityResult:
        ...
```

Plugin 对象负责：

```python
class Plugin(Protocol):
    manifest: PluginManifest

    def providers(self) -> list[CapabilityProvider]:
        ...
```

Core 只通过 Contract 与插件交互。

---

## 11. CapabilityRequest

建议：

```python
@dataclass
class CapabilityRequest:
    capability: str
    artifact_ref: ArtifactRef | None = None
    locator: ArtifactLocator | None = None
    options: dict = field(default_factory=dict)
```

对于 Phase 1.1：

```python
CapabilityRequest(
    capability="artifact.read.full",
    artifact_ref=ref,
)
```

禁止把 Adapter 实例、python-docx Document 等实现对象放入 Request。

---

## 12. CapabilityResult

统一包装执行结果。

建议：

```python
@dataclass
class CapabilityResult:
    success: bool
    value: object | None
    provider_id: str
    plugin_id: str
    warnings: list[str]
    metadata: dict
```

对于：

```text
artifact.read.full
```

`value` 必须是：

```text
Artifact
```

不得直接返回：

- python-docx Document；
- openpyxl Workbook；
- pdfplumber PDF；
- python-pptx Presentation。

---

## 13. ArtifactLocator

Phase 1 当前的：

```text
b0001
b0002
```

只是本次解析顺序 ID，不应承担未来稳定编辑定位职责。

Phase 1.1 必须引入或预留：

```text
ArtifactLocator
```

建议：

```python
@dataclass
class ArtifactLocator:
    scheme: str
    data: dict
```

示例：

DOCX：

```json
{
  "scheme": "docx",
  "data": {
    "paragraph_index": 12
  }
}
```

XLSX：

```json
{
  "scheme": "xlsx",
  "data": {
    "sheet": "资产负债表",
    "range": "B13:D20"
  }
}
```

PPTX：

```json
{
  "scheme": "pptx",
  "data": {
    "slide": 3,
    "shape_id": 7
  }
}
```

PDF：

```json
{
  "scheme": "pdf",
  "data": {
    "page": 12,
    "bbox": [20, 100, 500, 240]
  }
}
```

### Phase 1.1 的要求

本阶段不要求解决跨版本 Stable Locator 的全部问题，但：

1. Core Contract 中不得把 `block_id` 宣称为永久定位 ID；
2. 插件应允许为 Block 提供格式特有 Locator；
3. Locator 的解释归对应插件所有；
4. Core 只保存和传递 Locator，不硬编码格式语义。

---

## 14. Plugin Discovery

### FR-D01 Built-in Plugin Discovery

Runtime 必须能够发现 HMBuddy 自带插件。

不得依赖：

```python
from plugins.docx import DocxPlugin
from plugins.pdf import PdfPlugin
...
```

然后手工逐个注册。

### FR-D02 External Plugin Discovery

Phase 1.1 至少支持一种外部插件发现方式。

推荐首版：

```text
<HMBUDDY_PLUGIN_DIR>/
  my_plugin/
    plugin.yaml
    plugin.py
```

可以通过环境变量指定：

```text
HMBUDDY_PLUGIN_PATH
```

未来可以再演进 Python entry points / wheel 安装。

### FR-D03 Discovery 不等于 Load

发现阶段先读取和校验 Manifest。

Manifest 无效时：

- 不执行插件代码；
- 记录明确错误；
- 不影响其他插件加载。

---

## 15. Plugin Loader

### FR-L01 API Version 校验

不兼容：

```text
api_version
```

直接拒绝加载。

### FR-L02 Entrypoint 校验

Entrypoint 不存在、类不符合 Contract 时：

- 标记该插件 load_failed；
- 记录错误；
- Runtime 继续加载其他插件。

### FR-L03 Failure Isolation

单插件加载失败不得导致 HMBuddy 整体无法启动。

### FR-L04 Duplicate Plugin ID

发现重复 `plugin_id` 时不得静默覆盖。

首版策略：

> 拒绝重复 ID，并记录冲突来源。

未来再考虑版本选择。

---

## 16. Capability Registry

Registry 至少提供：

```python
register(provider)
list_capabilities()
list_providers(capability)
resolve(request)
```

内部索引至少支持：

```text
capability
plugin_id
provider_id
priority
extensions
availability
permissions
```

不得把：

```text
.docx → DocxAdapter
```

作为唯一索引模型。

---

## 17. Provider Routing

V0.1 路由采用确定性规则：

```text
1. capability 匹配
2. Provider supports(request)
3. 当前运行环境可用
4. 权限允许
5. priority 从高到低
6. provider_id 稳定排序作为最终 tie-break
```

### FR-R01 多 Provider

同一个 Request 可以存在多个候选 Provider。

### FR-R02 Priority

默认 Provider 可以声明优先级。

例如未来：

```text
DOCX Native Reader       priority=100
WPS COM Reader           priority=80
Vision Reader            priority=10
```

具体优先顺序未来可按真实效果调整。

### FR-R03 Fallback

如果首选 Provider 在“允许 fallback 的错误类型”下失败，可以尝试下一个 Provider。

V0.1 可先只实现路由，不强制实现自动 fallback；但接口与 Trace 必须预留。

禁止对以下错误静默 fallback：

- WorkspaceBoundaryError；
- PermissionDenied；
- 用户明确取消；
- 文件不存在。

---

## 18. Permission / Policy

### 18.1 Built-in Plugin

内置只读 Parser 默认允许：

```text
filesystem.read
```

但仍必须通过 Workspace 边界读取。

插件权限不能绕过 Workspace。

### 18.2 External Executable Plugin

外部插件属于受信代码扩展。

Runtime 至少需要做到：

- Manifest 显示声明权限；
- 未声明权限不得通过 Runtime API 获得该能力；
- Plugin 元数据可以在 Desktop / CLI 中查看；
- 默认不赋予网络、进程执行、文件写权限。

V0.1 不要求实现 OS 级 Sandbox，但文档必须明确：

> Plugin permission 是 HMBuddy Runtime Policy，不等价于操作系统安全沙箱。

### 18.3 Declarative User Extension

普通用户后续自定义业务处理能力，优先通过：

```text
Skill / YAML / JSON Workflow
```

组合已有 Capability。

Phase 1.1 不要求实现完整 Skill Runtime，但架构上不得把“用户自定义能力”唯一设计成 Python 插件。

---

## 19. Workspace 安全边界

Plugin Runtime 不得削弱 Phase 1 Workspace Boundary。

### FR-S01 ArtifactRef 必须重新解析

Provider 执行文件能力前，应通过 Workspace / Runtime 获得已校验路径，而不是直接信任外部传入绝对路径。

### FR-S02 Symlink

Phase 1.1 应补充 symbolic link / junction 的边界测试。

位于 Workspace 内的链接若指向 Workspace 外：

```text
workspace/a.docx
    → D:/outside/secret.docx
```

不得因插件化而绕过边界。

### FR-S03 LLM Metadata Separation

Runtime 元数据与 LLM-visible 元数据分离。

绝对文件路径默认不应自动进入 LLM Context。

---

## 20. Built-in Plugin 迁移

迁移原则：

> **先套插件边界，再优化 Adapter；不要同时重写解析逻辑。**

### Step 1

保留当前：

```text
adapters/docx.py
adapters/pdf.py
adapters/xlsx.py
adapters/pptx.py
```

### Step 2

建立 Built-in Plugin wrapper：

```text
plugins/docx
plugins/pdf
plugins/xlsx
plugins/pptx
```

Provider 内部调用现有 Adapter。

### Step 3

`ArtifactReader._route()` 不再直接遍历 Adapter。

改为：

```text
ArtifactReader
    ↓
CapabilityRuntime
    ↓
Registry
    ↓
Provider
```

### Step 4

待测试全部通过后，再决定是否把 Adapter 代码移动进对应 Plugin 包。

禁止为了目录整洁在第一步就大规模移动文件。

---

## 21. Stable Facade

现有公开调用：

```python
read_artifact(...)
```

必须保持。

建议内部改造：

```python
def read_artifact(...):
    request = CapabilityRequest(
        capability="artifact.read.full",
        artifact_ref=...,
        options=...,
    )
    result = default_runtime.execute(request)
    return cast(Artifact, result.value)
```

Phase 2 Desktop 不需要修改业务逻辑。

---

## 22. Example External Plugin

本阶段必须提供一个最小插件证明扩展性。

建议：

```text
plugins/examples/markdown_reader/
```

或者测试时动态创建临时 external plugin。

Manifest：

```yaml
id: example.markdown.reader
name: Markdown Reader
version: 0.1.0
api_version: 1

accepts:
  extensions:
    - .md

capabilities:
  - id: artifact.read.full
    priority: 100

permissions:
  - filesystem.read
```

验收：

```text
不修改 Core
不修改 Registry
不修改 Router
不修改 Office Plugins
       ↓
放入插件
       ↓
Runtime discover
       ↓
Workspace 发现 .md
       ↓
read_artifact()
       ↓
Artifact
```

如果必须修改核心代码才能支持 Markdown，则 Phase 1.1 插件化验收失败。

---

## 23. Error Model

在现有 `ArtifactRuntimeError` 基础上增加插件运行时错误。

建议：

```text
PluginRuntimeError
├─ PluginManifestError
├─ PluginCompatibilityError
├─ PluginLoadError
├─ DuplicatePluginError
├─ CapabilityNotFoundError
├─ ProviderNotAvailableError
├─ PluginPermissionError
└─ ProviderExecutionError
```

### ER-P01 Capability 不存在

例如：

```text
artifact.ocr
```

没有任何 Provider：

```text
CapabilityNotFoundError
```

### ER-P02 有 Provider 但当前不可用

例如 WPS COM Plugin 已安装，但当前机器无 WPS：

```text
ProviderNotAvailableError
```

### ER-P03 Provider 内部异常

不得把所有异常吞成：

```text
Unknown Error
```

应保留：

- plugin_id；
- provider_id；
- capability；
- cause。

---

## 24. Trace / Observability

每次 Capability 执行至少记录：

```text
request_id
capability
artifact_id
plugin_id
provider_id
started_at
duration_ms
status
warnings
error_type
fallback_from
```

Phase 1 现有 Artifact provenance 应增加：

```text
plugin_id
provider_id
plugin_version
```

同时保留：

```text
adapter
parser_library
```

用于解析实现诊断。

---

## 25. Context Hardening

Phase 1.1 同时收口上一阶段已经暴露的几个 Runtime 问题，但不扩大为 RAG 项目。

### FR-C01 Global Context Budget

`artifact_to_context()` 不再只有 table row limit。

至少支持：

- max_chars 或等价全局预算；
- max_blocks；
- max_table_rows。

发生截断必须显式返回或标记：

```text
truncated=true
omitted_blocks=N
reason=...
```

### FR-C02 XLSX 截断可见

当前 Adapter 的：

```text
rows_truncated
columns_truncated
cells_truncated
```

必须进入 Context / warning。

模型不得在静默截断情况下误以为看到了整表。

### FR-C03 PDF Page-level OCR Flag

扫描 / 无文本页需要 page-level 标记。

### FR-C04 Runtime Path 不默认暴露给 LLM

`artifact.path` 保留在 Runtime，但 LLM Context 默认显示：

- name；
- artifact_id；
- relative path（如确有需要）。

不得默认发送绝对路径。

---

## 26. 非目标

Phase 1.1 明确不实现：

### 26.1 不实现完整 Agent Loop

不实现：

- Planner；
- ReAct；
- Tool Calling Loop；
- Multi-Agent；
- Autonomous Task。

### 26.2 不实现 Artifact Update

本阶段不要求：

- update_docx；
- update_xlsx；
- update_pptx；
- patch；
- version rollback。

但 Plugin Contract 必须允许未来加入：

```text
artifact.update
artifact.patch
```

### 26.3 不实现完整 Plugin Marketplace

不做：

- 在线插件商店；
- 自动下载安装；
- 远程更新；
- 插件评分；
- 云端分发。

内网环境首版只要求本地 Plugin Path。

### 26.4 不实现 OS 级插件沙箱

不要求容器 / WASM / 子进程隔离。

首版重点是 Contract、权限声明、Runtime Policy 和 Failure Isolation。

### 26.5 不为了“万物插件化”拆 Core

以下内容暂不插件化：

- Artifact Core Model；
- Workspace Boundary；
- Plugin Runtime 本身；
- Permission / Policy；
- Trace Contract。

---

## 27. 测试策略

### T1. Manifest Tests

覆盖：

- 合法 Manifest；
- 缺失必填字段；
- 非法 plugin ID；
- 非法 version；
- 不兼容 api_version；
- 未知 permission；
- capability 重复。

### T2. Discovery Tests

覆盖：

- 内置插件发现；
- external plugin path；
- 无效目录；
- 单插件损坏不影响其他插件；
- 重复 plugin_id。

### T3. Registry Tests

覆盖：

- Provider 注册；
- capability 查询；
- 多 Provider；
- priority 排序；
- deterministic tie-break。

### T4. Routing Tests

覆盖：

```text
.docx + artifact.read.full
.pdf  + artifact.read.full
.xlsx + artifact.read.full
.pptx + artifact.read.full
```

路由到正确 Built-in Provider。

### T5. Regression Tests

Phase 1 已有 Parser / Context / Error Tests 必须继续通过。

Phase 2 Desktop Presenter / Runtime Tests 必须继续通过。

### T6. External Plugin Test

测试必须证明：

> 在不修改 Core 和既有插件源码的情况下，新增 Markdown / TXT 插件后可通过统一入口读取。

### T7. Failure Isolation

构造故障插件：

- import error；
- constructor error；
- execute error。

验证其他插件仍然正常工作。

### T8. Permission Tests

覆盖：

- 只读 Provider；
- 未声明权限；
- 写权限请求；
- Workspace 越界。

### T9. Context Hardening

覆盖：

- 大 XLSX 截断 warning；
- global context budget；
- mixed PDF OCR page flag；
- Context 不包含默认绝对路径。

---

## 28. Eval Fixtures

Phase 1 自生成 fixture 继续保留。

Phase 1.1 增加一组 Real-world Regression Fixtures，至少覆盖：

- Microsoft Office 生成 DOCX；
- WPS 生成 DOCX；
- Microsoft Excel 生成 XLSX；
- WPS 表格生成 XLSX；
- PowerPoint / WPS 演示文件；
- 有文本层 PDF；
- 文本 + 扫描页混合 PDF；
- 超过 500 行的 XLSX；
- 含复杂合并单元格的 XLSX；
- 一个 external Markdown fixture。

涉及真实业务数据时必须脱敏或使用人工构造文件。

---

## 29. 验收标准

Phase 1.1 只有同时满足以下条件才算完成。

### AC-01 Core 不硬编码具体 Office Provider

核心 Router / Reader 中不得出现：

```text
DocxAdapter
PdfAdapter
XlsxAdapter
PptxAdapter
```

静态 Provider 列表。

### AC-02 Built-in Plugins 自动注册

启动 Runtime 后可列出：

```text
hmbuddy.docx.core
hmbuddy.pdf.core
hmbuddy.xlsx.core
hmbuddy.pptx.core
```

以及其 Capability。

### AC-03 `read_artifact()` 兼容

Phase 1 / Phase 2 原调用方式继续工作。

### AC-04 不改 Core 新增 Markdown

External Markdown Plugin 安装后：

```python
read_artifact("README.md")
```

或通过 Workspace ArtifactRef 能返回标准 Artifact。

### AC-05 多 Provider Registry

测试中为同一 Capability 注册两个 Provider，Registry 能按 priority 稳定解析。

### AC-06 插件故障隔离

一个插件加载失败不影响其他插件正常工作。

### AC-07 Permission 可观察

Runtime 可列出插件声明权限，未授权能力不会静默执行。

### AC-08 原有测试无回归

Phase 1 和 Phase 2 原有测试全部通过。

若测试数量变化，baseline 更新并记录原因。

### AC-09 Context 静默截断问题解决

任何 Runtime 主动截断都必须对上层可观察。

### AC-10 Workspace 边界不因插件化削弱

外部 Provider 不得通过标准 Runtime API 读取 Workspace 外文件。

---

## 30. 推荐实施顺序

### Step 1. 冻结现有 Regression Baseline

记录当前：

- commit SHA；
- pytest 结果；
- Phase 1 / Phase 2 baseline。

### Step 2. 定义 Core Contract

先实现：

- PluginManifest；
- CapabilityRequest；
- CapabilityResult；
- CapabilityProvider；
- PluginContext；
- Runtime Error Types。

Contract 未稳定前不迁移 Adapter。

### Step 3. Registry

实现：

- register；
- query；
- resolve；
- priority；
- duplicate detection。

### Step 4. Loader / Discovery

先实现 Built-in，然后 External Plugin Path。

### Step 5. DocxPlugin 试迁移

只迁移一种格式验证：

```text
read_artifact()
→ Runtime
→ Registry
→ DocxPlugin
→ existing DocxAdapter
→ Artifact
```

Phase 1 DOCX tests 必须保持通过。

### Step 6. 迁移 PDF / XLSX / PPTX

逐个迁移，不同时重写解析器。

### Step 7. External Markdown Plugin

验证不改 Core 的真实扩展。

### Step 8. Permission / Trace / Failure Isolation

补齐受控执行边界。

### Step 9. Context Hardening

处理 global budget、truncation、OCR page flag、path exposure。

### Step 10. 全量 Regression

运行：

```bash
python -m pytest -q
```

并更新 Phase 1.1 baseline。

---

## 31. 迁移完成后的目标调用关系

迁移前：

```text
Desktop / CLI
      ↓
ArtifactReader
      ↓
_route()
      ↓
ADAPTER_CLASSES
      ↓
Adapter
```

迁移后：

```text
Desktop / CLI / Future Agent
            ↓
       read_artifact()
            ↓
     CapabilityRuntime
            ↓
     CapabilityRegistry
            ↓
          Router
            ↓
         Provider
            ↓
          Plugin
            ↓
    Adapter / API / COM
            ↓
         Artifact
```

Adapter 从“系统级扩展机制”降为：

> **某个 Plugin 内部可以选择使用的实现技术。**

---

## 32. 后续演进方向

Phase 1.1 完成后，文件能力可以按相同机制逐步加入：

```text
artifact.read.outline
artifact.read.range
artifact.search
artifact.compare
artifact.update
artifact.validate
artifact.render
artifact.convert
artifact.ocr
```

例如未来：

```text
WPS COM Plugin
├─ artifact.read.full
├─ artifact.update
├─ artifact.render
└─ artifact.convert

OCR Plugin
├─ artifact.ocr
└─ artifact.read.full (scanned PDF fallback)

Financial Workbook Plugin
├─ financial.statement.detect
└─ financial.statement.normalize
```

Agent 层只面向 Capability，不依赖实现技术。

---

## 33. 第一阶段完成后的架构判断标准

Phase 1.1 的成功不是：

> “plugins/ 目录里有很多文件。”

而是同时满足：

1. Core 不知道具体文件实现；
2. Plugin 可以独立声明自己提供什么；
3. Runtime 可以自动发现并注册；
4. 同一 Capability 可以有多个 Provider；
5. Provider 选择规则确定、可观察；
6. 插件失败不会拖垮 Runtime；
7. 权限边界清晰；
8. 新增一种文件处理能力不需要修改 Core；
9. 上层 Desktop / CLI 不需要知道插件体系；
10. Artifact Contract 仍然是文件能力之间的共同语言。

最终形成：

> **Stable Kernel + Pluggable File Capabilities + Stable Artifact Contracts**

这将作为 HMBuddy 后续 Artifact Update、WPS/Office 原生操作、OCR、Skills 和 Agent Runtime 的基础扩展架构。
