# HMBuddy Phase 1.1.1 — Plugin Runtime Contract Hardening 需求规格说明书

**项目阶段：** Phase 1.1.1 / Architecture Hardening  
**版本：** V0.1  
**阶段主题：** Plugin Runtime Contract Hardening  
**基线提交：** `8c68df15c64277ca0f6315cc5824d55d422d42a3`  
**前置规格：** `phase-1.1-pluggable-file-capability-runtime-v0.1.md`  
**文档目的：** 将 Phase 1.1 最新代码审阅确认的缺陷集中形成修复规格。本文档只收口 Contract、权限、Workspace 解耦、外部插件加载、Context Budget、Locator、Trace 与工程验证，不新增 Artifact Update / Compare / Agent Loop 等业务能力。

---

## 1. 背景

Phase 1.1 已经建立：

```text
read_artifact()
      ↓
CapabilityRuntime
      ↓
CapabilityRegistry
      ↓
CapabilityRouter
      ↓
CapabilityProvider
      ↓
Plugin
      ↓
Adapter / API / COM
      ↓
Artifact
```

主体插件机制已经成立，但完整代码审阅确认：

> **当前“机制层”完成度较高，“治理层”和“Workspace 集成层”仍存在会阻碍后续扩展的缺陷。**

如果直接继续加入 `artifact.update`、WPS/Office COM、Agent Tool Calling，这些问题会从“只读阶段的架构瑕疵”升级为真实文件修改和权限风险。

因此增加 Phase 1.1.1，先完成 Plugin Runtime Contract Hardening。

---

## 2. 阶段目标

本阶段只回答：

> **Plugin Manifest、Provider、Workspace、Permission Policy、Runtime 和 Context 是否形成真正一致、可执行、可验证的契约，使“新增文件处理插件无需修改 Core”同时在路由、Workspace 发现、安全边界和运行权限上成立？**

---

## 3. 缺陷总览

| 编号 | 优先级 | 缺陷 | 核心风险 |
|---|---|---|---|
| BUG-001 | P0 | Permission Policy 只记录、不真正阻断 | 未授权 COM / 网络 / 写操作仍可能执行 |
| BUG-002 | P0 | Workspace 仍硬编码扩展名 | 新插件不能真正新增一种 HMBuddy 原本不认识的文件格式 |
| BUG-003 | P1 | Manifest 不是 Provider 的权威声明 | Provider 可绕过 Manifest 修改 extension / priority / identity |
| BUG-004 | P1 | Loader 校验 Provider 与 Registry 注册 Provider 不是同一批对象 | 第二次 providers() 可绕过 Loader 校验 |
| BUG-005 | P1 | `ArtifactReader(external_plugin_dirs=...)` 参数不生效 | API 表面支持显式插件目录，实际没有加载该目录 |
| BUG-006 | P1 | Context Budget 已实现但主路径默认无限 | 大文档仍可能直接撑爆 LLM Context |
| BUG-007 | P1 | Workspace ArtifactRef 可脱离 Workspace 信任域 | 未来 Agent 使用 Ref 时可能绕过 Workspace 边界 |
| BUG-008 | P1 | Manifest platform / Python runtime 声明没有实际校验 | 当前环境不可用的 Provider 仍会被选中执行 |
| BUG-009 | P1 | ArtifactLocator 只定义未进入 ArtifactBlock | update / patch 前仍缺稳定定位 Contract |
| BUG-010 | P2 | `CapabilityResult.success` 不参与 Runtime 判定 | success=false 仍可能记录为成功 |
| BUG-011 | P2 | Router 静默吞掉 supports/is_available 异常 | Provider bug 被伪装为“不支持” |
| BUG-012 | P2 | fallback 策略不是显式 allowlist | 未来新增领域错误后可能发生错误 fallback |
| BUG-013 | P2 | External Plugin Loader 只适合单文件插件 | 用户插件无法稳定拆成 package / sibling modules |
| BUG-014 | P2 | 静态 `ARTIFACT_TYPES` 与 Registry 架构冲突 | Core 继续保留过时“支持格式事实” |
| BUG-015 | P3 | Trace started_at 时点不准确且 traces 无界增长 | 可观察性失真，长期运行内存增长 |
| BUG-016 | P3 | README / 架构说明与实现版本漂移 | 使用者获得错误架构与测试状态 |
| BUG-017 | P3 | 缺少 CI / install smoke | source tree 可运行不代表安装包可运行 |

---

## 4. BUG-001 — Permission Policy 必须真正阻断未授权能力

### 4.1 当前问题

默认 Policy 只授予：

```text
filesystem.read
```

但 `.doc` 等插件声明：

```text
filesystem.read
office.com
wps.com
```

当前 Runtime 主要将：

```text
declared_permissions ∩ granted_permissions
```

写入 `PluginContext`，但 Provider / Adapter 如果不主动调用 `policy.require()`，仍可直接：

```python
win32.DispatchEx("Word.Application")
```

因此权限目前只是“可观察”，不是“强约束”。

### 4.2 修复要求

Provider 增加执行所需权限声明，例如：

```python
required_permissions = {
    "filesystem.read",
    "office.com",
}
```

Runtime 必须在 `provider.execute()` 前执行权限校验。

未授权必须抛：

```text
PluginPermissionError
```

并禁止实际进入 COM / network / write。

### 4.3 动态权限

对于 XLS 这类“xlrd 优先，COM fallback”的能力：

```text
xlrd 成功
→ 只需 filesystem.read

准备 COM fallback
→ context.require_permission("office.com")
```

PluginContext 应提供等价受控接口。

### 4.4 验收

默认仅授权 `filesystem.read` 时：

- DOCX/PDF/XLSX/PPTX 正常；
- .doc 不得实际启动 Word/WPS；
- COM fallback 必须先报 Permission；
- mock `win32.DispatchEx` 不得被调用。

---

## 5. BUG-002 — Workspace 支持格式必须从 Capability Catalog 派生

### 5.1 当前问题

当前 `Workspace` 仍有静态：

```python
CORE_SUPPORTED_EXTENSIONS = {
    ".docx": ...,
    ".pdf": ...,
    ".xlsx": ...,
    ".pptx": ...,
    ".xls": ...,
    ".doc": ...,
    ".txt": ...,
    ".md": ...,
    ...
}
```

安装一个全新 `.foo` / `.dwg` 插件后，Registry 可以识别 Provider，但 `Workspace.list_artifacts()` 不会展示该文件。

所以“新增文件能力不改 Core”目前只在 Reader 层成立。

### 5.2 修复目标

Workspace 不再维护“支持格式的权威表”。

推荐新增轻量：

```text
CapabilityCatalog
```

至少支持：

```python
can_handle_extension(ext, capability)
artifact_extensions()
providers_for(ext, capability)
```

Workspace 只负责本地文件边界和基础发现，当前 Runtime 能否处理由 Catalog 决定。

### 5.3 真正的外部插件验收

不能继续用本来就已支持的 `.md` 作为唯一 AC。

必须新增 Core 从未出现过的 extension，例如：

```text
.foo
.mdx
.xyzdoc
```

验收：

```text
安装 external plugin
       ↓
不修改 Workspace / Core
       ↓
Workspace 自动显示 .foo
       ↓
read_artifact()
       ↓
Artifact
```

---

## 6. BUG-003 — Manifest 必须成为 Plugin Governance 的唯一权威源

### 6.1 当前问题

Manifest 已声明：

- plugin id；
- version；
- extensions；
- capabilities；
- priority；
- permissions；
- platforms。

但 Provider 类也可以自行定义：

```python
plugin_id
plugin_version
extensions
priority
```

当前 Runtime 路由主要相信 Provider 字段。

因此插件可能声明：

```text
Manifest:
  extension=.md
  priority=50
```

实际代码却：

```text
Provider:
  extension=.docx
  priority=9999
  plugin_id=hmbuddy.docx.core
```

### 6.2 修复要求

Manifest 必须是唯一权威源。

推荐 Loader 强制注入：

```python
provider.plugin_id = manifest.id
provider.plugin_version = manifest.version
provider.priority = capability_declaration.priority
provider.extensions = tuple(manifest.extensions)
provider.declared_permissions = tuple(manifest.permissions)
```

Provider 只负责：

- supports；
- availability；
- execute。

### 6.3 验收反例

构造 Manifest / Provider 冲突：

```text
Manifest:
id=test.foo
accepts=[".foo"]
priority=10

Provider:
plugin_id=hmbuddy.docx.core
extensions=[".docx"]
priority=9999
```

最终必须：

- 只处理 .foo；
- priority=10；
- provenance plugin_id=test.foo；
- 不得抢占 .docx。

---

## 7. BUG-004 — Loader 校验与 Registry 注册必须使用同一批 Provider 实例

### 7.1 当前问题

Loader：

```python
provider_list = list(instance.providers())
```

完成校验。

但 Assembly 后续再次：

```python
for provider in loaded.plugin.providers():
    registry.register(provider)
```

若第三方实现：

```python
def providers(self):
    return [NewProvider()]
```

第二次返回的 Provider 没经过完整 Loader 校验。

### 7.2 修复要求

`LoadedPlugin` 必须保存已校验 Provider：

```python
@dataclass
class LoadedPlugin:
    plugin: object
    discovered: DiscoveredPlugin
    providers: list[CapabilityProvider]
```

Registry 只能注册：

```python
loaded.providers
```

禁止再次调用 `plugin.providers()`。

### 7.3 验收

构造每次调用 `providers()` 都返回新对象的插件：

- Loader 只调用一次；
- Registry 对象 identity 与 Loader validated provider 相同。

---

## 8. BUG-005 — external_plugin_dirs 参数必须真实生效

### 8.1 当前问题

`ArtifactReader.__init__` 接收：

```python
external_plugin_dirs
```

但当前只触发：

```python
get_default_runtime(force_reload=True)
```

传入目录本身没有进入 Runtime Assembly。

### 8.2 修复要求

显式目录存在时：

```python
assembly = assemble_runtime(
    external_plugin_dirs=external_plugin_dirs,
)
```

否则才使用默认全局 Runtime。

### 8.3 验收

必须直接：

```python
reader = ArtifactReader(
    external_plugin_dirs=[container]
)
artifact = reader.read_artifact(target)
```

禁止通过：

- 手工覆盖 `reader.runtime`；
- monkeypatch 全局 Runtime；
- 环境变量兜底。

---

## 9. BUG-006 — Context Budget 必须成为默认 LLM 主路径行为

### 9.1 当前问题

已经有：

```python
build_context(
    max_chars=...,
    max_blocks=...,
    max_table_rows=...
)
```

但默认 `max_chars=None`、`max_blocks=None`，LLM 主路径仍会把大 Artifact 全量发送。

### 9.2 修复要求

引入：

```python
@dataclass
class ContextPolicy:
    max_chars: int
    max_blocks: int
    max_table_rows: int
```

LLM Client 默认必须通过 ContextPolicy 构造 Context。

具体默认值可配置，不在本规格锁死。

发生截断时：

- Context 中保留 `[Context Truncated]`；
- warnings 可查询；
- System Prompt 要求不得声称完整审阅全部内容。

### 9.3 验收

构造超大 Artifact，直接走：

```python
client.ask(...)
```

无需调用方额外设置 max_chars，也必须产生有界 Context。

---

## 10. BUG-007 — ArtifactRef 必须保留 Workspace 信任域

### 10.1 当前问题

当前 ArtifactRef 主要保存：

```python
path: str
```

安全路径：

```python
read_artifact(ref, workspace=workspace)
```

会重新校验。

但：

```python
ref = workspace.list_artifacts()[0]
read_artifact(ref)
```

可以脱离原 Workspace。

### 10.2 推荐模型

```text
ArtifactRef
├─ artifact_id
├─ workspace_id
├─ relative_path
├─ name
├─ extension
└─ ...
```

绝对路径只能作为 Runtime 内部派生信息，不作为信任依据。

### 10.3 Phase 1.1.1 最低要求

如果暂不引入 WorkspaceRegistry：

> 来自 Workspace 的 ArtifactRef 在未提供原 Workspace 时，`read_artifact(ref)` 必须拒绝执行。

### 10.4 验收

Workspace symlink 指向外部文件，以及 Workspace Ref 脱离 Workspace 后直接读取，都不得绕过边界。

---

## 11. BUG-008 — platform / python_requires / dependency availability 必须参与路由

### 11.1 当前问题

Manifest 已有：

```text
platforms
runtime.python
```

但没有真实校验。

`CapabilityProviderBase.is_available()` 默认始终 True。

例如 `.doc` 实际依赖 Windows COM，却可能在非 Windows 环境被 Router 选中后才失败。

### 11.2 修复要求

Availability 至少包含：

```text
Manifest platform
+
Python version
+
Provider dependency probe
```

不满足时：

```text
ProviderNotAvailableError
```

不得进入 execute。

Legacy DOC Manifest 必须修正为真实支持平台。

### 11.3 验收

Mock Linux / Python 不兼容 / dependency 缺失：

- Provider 不进入 execute；
- Trace/diagnostic 可看到不可用原因。

---

## 12. BUG-009 — ArtifactLocator 必须进入 ArtifactBlock Contract

### 12.1 当前问题

已经定义 `ArtifactLocator`，但 ArtifactBlock 仍只有：

```text
block_id
block_type
text
location
metadata
```

格式定位仍散落在普通 dict 中。

### 12.2 修复要求

ArtifactBlock 增加：

```python
locator: ArtifactLocator | None
```

格式插件负责生成：

- DOCX：稳定 paragraph id / paraId；无法获得时 index + signature；
- XLSX：sheet + cell/range；
- PPTX：slide + shape_id；
- PDF：page + bbox。

现有 `location` 暂时保留用于 UI 和兼容测试。

---

## 13. BUG-010 — CapabilityResult.success 必须有真实语义

### 13.1 当前问题

Provider 只要正常 return，Runtime 就可能记为 `status=ok`，即使：

```python
CapabilityResult(success=False)
```

### 13.2 修复要求

推荐二选一：

1. 删除 `success`，失败统一抛领域异常；
2. 保留 `success`，Runtime 对 false 强制转换为 ProviderExecutionError。

不得出现：

```text
success=false
trace.status=ok
```

---

## 14. BUG-011 — Router 不得静默吞 supports / is_available 异常

### 14.1 当前问题

当前类似：

```python
try:
    supported = provider.supports(...)
except Exception:
    supported = False
```

Provider bug 会被伪装成“不支持”。

### 14.2 修复要求

Selection diagnostics 必须记录：

- plugin_id；
- provider_id；
- selection stage；
- exception type；
- message。

如果其他 Provider 可继续，则可以继续路由；如果所有 Provider 都因选择阶段异常失败，不得返回普通 CapabilityNotFound。

---

## 15. BUG-012 — Fallback 必须使用显式错误 Allowlist

### 15.1 当前问题

代码虽有 `FALLABLE_ERRORS`，实际逻辑仍对较宽的领域异常家族进行 fallback。

### 15.2 修复要求

集中定义显式 allowlist。

可考虑：

```text
ProviderExecutionError
ArtifactParseError
```

EncryptedArtifactError 是否可 fallback 必须显式决定并测试。

必须禁止：

- WorkspaceBoundaryError；
- ArtifactNotFoundError；
- PluginPermissionError；
- UserCancelled；
- PolicyViolation；
- InvalidRequest；
- CapabilityNotFoundError。

---

## 16. BUG-013 — External Plugin Loader 必须支持标准 Package

### 16.1 当前问题

当前外部插件主要适合：

```text
plugin.py
```

真实插件很快会变成：

```text
my_plugin/
├─ plugin.json
└─ hmbuddy_plugin/
   ├─ __init__.py
   ├─ plugin.py
   ├─ parser.py
   └─ utils.py
```

并需要相对 import。

### 16.2 修复要求

定义本地 External Plugin Package Contract。

Manifest 可声明：

```json
"entrypoint": {
  "module": "hmbuddy_plugin.plugin",
  "class": "MyPlugin"
}
```

Loader 必须：

- 支持 package relative import；
- 避免跨插件 module name 冲突；
- 不长期污染全局 sys.path。

本阶段不要求 wheel marketplace。

---

## 17. BUG-014 — 删除或降级静态 ARTIFACT_TYPES

### 17.1 当前问题

`workspace/artifact.py` 仍保留仅含少数格式的：

```python
ARTIFACT_TYPES
```

它已经不是系统真实能力集合。

### 17.2 修复要求

如果无必要，直接删除。

如果 UI / 测试需要当前类型列表，应从 Capability Catalog 动态派生。

不得继续维护第二份静态“支持格式真相”。

---

## 18. BUG-015 — Trace 时间与生命周期收口

### 18.1 started_at

Provider 执行前同时记录：

```python
started_at = datetime.now(timezone.utc)
started_perf = time.perf_counter()
```

Trace 不得在执行完成后才生成开始时间。

### 18.2 traces 无界增长

当前 Runtime 内存 trace 改为：

- `deque(maxlen=N)`；或
- 默认只写结构化日志，内存仅保留最近 N 条。

N 可配置。

---

## 19. BUG-016 — README / 架构说明与实现同步

README 当前存在阶段、架构图和测试数量漂移。

修复要求：

- 明确 Phase 1 / Phase 1.1 / Phase 2；
- 架构图以 Capability Runtime 为中心；
- 不再把 Adapter Router 描述为系统级路由；
- 测试数量只在一个明显位置引用当前 baseline，避免多处硬编码漂移；
- Phase 1.1.1 完成后加入对应规格链接和 baseline。

---

## 20. BUG-017 — 增加 CI 与安装态 Smoke Test

### 20.1 风险

Editable source tree 可运行，不代表：

```bash
pip install .
```

或 wheel 安装后 Built-in plugin manifest 仍能被发现。

尤其当前 Discovery 依赖 package layout 和 `plugin.json`。

### 20.2 修复要求

增加 GitHub Actions，至少覆盖：

```text
Python 3.10
Python 3.12
```

Windows 至少一组；Linux 至少一组基础测试。

执行：

```bash
pip install -e ".[dev]"
python -m pytest -q
```

再增加安装态 smoke：

```bash
python -m build
pip install dist/*.whl
```

验证：

- Built-in plugin manifests 被打包；
- Registry 可发现 Built-in Plugins；
- `read_artifact()` 可读 sample；
- CLI / desktop entry point 可 import。

---

## 21. 本阶段非目标

Phase 1.1.1 不实现：

- artifact.update；
- artifact.patch；
- artifact.compare；
- artifact.search；
- Planner；
- Agent Loop；
- Multi-Agent；
- Plugin Marketplace；
- OS 级 Sandbox；
- 在线插件下载安装；
- 完整 Workspace 持久化数据库。

本阶段只修 Contract 与运行时边界。

---

## 22. 推荐模块边界

在不大规模搬目录的前提下，可补充：

```text
plugin_runtime/
├─ contracts.py
├─ manifest.py
├─ discovery.py
├─ loader.py
├─ registry.py
├─ router.py
├─ policy.py
├─ runtime.py
├─ availability.py      # 可选
└─ catalog.py           # 可选：向 Workspace 提供能力视图
```

Workspace 不直接依赖插件实现，只消费轻量 Capability Catalog。

---

## 23. 测试策略

### T1 Permission Enforcement

Mock COM Dispatch，默认 Policy 下必须从未调用。

### T2 New Extension Plugin

创建 `.foo` external plugin，验证：

```text
Workspace → ArtifactRef → read_artifact
```

全链路，不改 Core。

### T3 Manifest Authority

Manifest / Provider 冲突时，Manifest 必须生效。

### T4 Provider Single Materialization

`providers()` 每次返回新对象时，Loader 仍只调用一次。

### T5 external_plugin_dirs

直接通过 ArtifactReader 参数加载，不使用 runtime monkeypatch。

### T6 Default Context Budget

从真实 LLM client 构造路径验证默认有界。

### T7 ArtifactRef Trust Boundary

Workspace Ref 脱离 Workspace 时拒绝。

### T8 Availability

Mock platform / Python / dependency availability。

### T9 ArtifactLocator

DOCX / PDF / XLSX / PPTX 均生成标准 Locator。

### T10 Result State

success=false 不得产生 ok Trace。

### T11 Selection Diagnostics

supports / availability 异常必须可诊断。

### T12 Fallback Allowlist

逐个领域错误验证 fallback 与 no-fallback。

### T13 External Package Plugin

插件内部相对 import 必须正常。

### T14 Install Smoke

wheel 安装后 Built-in Plugin Discovery 正常。

---

## 24. 验收标准

### AC-H01 Permission 是强约束

未授权 COM / network / write 不得实际执行。

### AC-H02 新 extension 无需修改 Core

新增 `.foo` 插件后 Workspace 自动发现并可读取。

### AC-H03 Manifest 权威

Provider 无法绕过 Manifest 修改 plugin id / version / extension / priority / permissions。

### AC-H04 Provider 只校验一次

Registry 注册对象必须与 Loader validated provider 为同一对象。

### AC-H05 external_plugin_dirs 真实生效

ArtifactReader 参数链可以直接加载指定插件。

### AC-H06 LLM 主路径默认有 Context Budget

调用方不配置时也不得无限上下文。

### AC-H07 Workspace Ref 不能脱离信任域

来源于 Workspace 的 Ref 不得通过省略 Workspace 绕过边界。

### AC-H08 Availability 真实参与路由

不满足 platform / Python / dependency 的 Provider 不执行。

### AC-H09 Locator 进入 Block Contract

ArtifactBlock 有标准 Locator；location 仅作兼容/展示。

### AC-H10 Result 状态一致

success=false 不得记录 Runtime ok。

### AC-H11 Provider 选择异常可诊断

supports / availability 异常不再静默丢失。

### AC-H12 Fallback 行为由明确 allowlist 控制

没有“大类异常默认 fallback”。

### AC-H13 External Plugin 支持 Package

多文件插件与相对 import 正常。

### AC-H14 无第二份支持类型真相

Workspace / Core 不再维护静态 supported-format truth。

### AC-H15 Trace 有界且时间正确

started_at 是真实开始时间；内存 trace 有上限。

### AC-H16 文档同步

README 与实际阶段、架构和 baseline 一致。

### AC-H17 Clean Install 可验证

CI 中 source install + wheel install smoke 均通过。

---

## 25. 推荐实施顺序

### Step 1 — Permission

先完成 BUG-001。

权限未真实执行前，不继续扩充 COM Provider。

### Step 2 — Manifest / Provider Contract

一次处理：

- BUG-003；
- BUG-004；
- BUG-010；
- BUG-011；
- BUG-012。

### Step 3 — Workspace / Registry 解耦

处理：

- BUG-002；
- BUG-007；
- BUG-014。

完成后用全新 `.foo` 插件替代当前 Markdown-only 扩展性验收。

### Step 4 — Runtime Configuration / Availability

处理：

- BUG-005；
- BUG-008。

### Step 5 — Artifact Contract

处理 BUG-009。

必须在进入 Artifact Update 之前完成。

### Step 6 — Context

处理 BUG-006。

### Step 7 — External Plugin Packaging

处理 BUG-013。

### Step 8 — Observability / Docs / CI

处理：

- BUG-015；
- BUG-016；
- BUG-017。

### Step 9 — 全量 Regression

运行 Phase 1 / Phase 1.1 / Phase 2 全部测试，并形成：

```text
evals/baseline-phase1.1.1-v0.1.json
```

---

## 26. 实施约束

### C1. 不重写 Parser

除非与本规格 bug 直接相关，DOCX / PDF / XLSX / PPTX / OCR / PDF table parser 不做功能重写。

### C2. Stable Facade 保持兼容

继续支持：

```python
read_artifact(...)
```

Phase 2 Desktop 不感知 Runtime 内部变化。

### C3. 不用格式特殊判断修架构问题

禁止通过不断增加：

```python
if ext == ...
if plugin_id == ...
```

解决问题。

必须通过 Contract / Catalog / Policy 收口。

### C4. 测试先于修复

每个 BUG 先增加失败测试，再改实现。

---

## 27. 完成后的目标结构

```text
              Application / Agent
                       │
                       ▼
                 Stable Facade
                       │
                       ▼
              Capability Runtime
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       Policy       Registry      Trace
          │            │
          │       Manifest-authoritative
          │            │
          └──────► Router
                       │
               Availability Check
                       │
                       ▼
                Validated Provider
                       │
                       ▼
              Adapter / API / COM
                       │
                       ▼
                    Artifact
                       │
               Artifact Locator
```

Workspace：

```text
Local Files
    ↓
Workspace Boundary / Discovery
    ↓
Capability Catalog
    ↓
Current Runtime can handle?
    ↓
ArtifactRef
```

最终目标：

> **新增文件能力 = 安装 Plugin，而不是修改 HMBuddy Core。**

同时：

> **插件声明什么、在哪个平台能运行、允许访问什么，由 Runtime Contract 强制执行，而不是依赖插件自觉。**

---

## 28. 进入下一阶段的前置条件

Phase 1.1.1 完成后，才建议继续：

```text
artifact.read.outline
artifact.read.range
artifact.search
artifact.compare
artifact.update
artifact.patch
```

尤其在实现 `artifact.update / patch` 之前，必须完成：

- Permission Enforcement；
- Manifest Authority；
- ArtifactLocator；
- Workspace Trust Boundary；
- Fallback Contract。

否则当前只读阶段的边界问题会升级为真实文件写入风险。
