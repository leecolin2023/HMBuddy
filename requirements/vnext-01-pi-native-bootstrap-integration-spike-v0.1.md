# HMBuddy VNext-01 — Pi-native Bootstrap & Office Integration Spike V0.1

**文档性质：** VNext Requirement Specification / Integration Spike  
**版本：** V0.1  
**状态：** Proposed for Implementation  
**日期：** 2026-10-03  
**Architecture Baseline：** HMBuddy Architecture Baseline V1.0 — Pi-native Banking Office Agent  
**Pi Baseline：** `@earendil-works/pi-coding-agent@1.0.0`  
**目标平台：** Windows-first；核心边界尽量跨平台  
**核心验收链：**

~~~text
User Prompt
   ↓
Pi AgentSession
   ↓
HMBuddy Pi Extension
   ↓
read_office_file Tool
   ↓
TypeScript Office Bridge
   ↓
Python subprocess
   ↓
DOCX structured read result
   ↓
Pi Observation
   ↓
Assistant final answer
~~~

---

# 1. 背景

HMBuddy 已在 Architecture Baseline V1.0 中完成根本性架构重置：

> 不再自研通用 Agent Kernel；Pi 负责 Agent / Session / Context / Model / Tool / Extension / Skill 等通用 Agent Runtime，HMBuddy 只建设 Office 能力、银行 Skills、企业治理与内部系统集成。

因此 VNext 的第一步不应该继续旧路线中的：

- SessionStore；
- AgentLoop；
- ToolRegistry；
- ExtensionHost；
- HMBuddy Model Runtime；
- HMBuddy Plugin Runtime；
- Desktop Conversation Runtime。

第一步必须用最小真实场景回答一个更基础的问题：

> **Pi 能否作为 HMBuddy 的实际 Agent substrate，并自然调用一个与 Pi 进程解耦的 Python Office 能力？**

如果这条链路不能稳定成立，V1.0 的架构假设需要立即修正。

如果成立，后续 HMBuddy 才有依据继续投入：

- DOCX / XLSX / PPTX / PDF；
- Artifact / Patch / Diff / Validation；
- Banking Skills；
- Approval / Audit；
- Dedicated UI。

所以本阶段是一个 **Architecture Integration Spike**，不是产品功能阶段。

---

# 2. Stage Goal

本阶段只证明一件事：

> **Pi 1.0 的真实 AgentLoop 能够自主选择并调用 HMBuddy 注册的 `read_office_file` Tool；该 Tool 通过稳定的进程边界调用 Python DOCX reader，将结构化结果返回 Pi；Pi 根据 Tool Result 完成最终回答。**

必须是 Agent 自主 Tool Calling，而不是宿主程序先读文件再把内容手工塞入 Prompt。

成功路径：

~~~text
用户：
“阅读 fixtures/sample.docx，告诉我项目编号和负责人。”

        ↓

Pi model decides:
call read_office_file(path="fixtures/sample.docx")

        ↓

HMBuddy Pi Extension
        ↓
OfficeBridge
        ↓
python -m hmbuddy_office_bridge
        ↓
DOCX Reader
        ↓
structured JSON
        ↓
Pi Tool Result
        ↓
model continues
        ↓

“项目编号是 HM-001，负责人是……”
~~~

---

# 3. Non-goals

本阶段明确 **不做**：

## 3.1 不重建 Pi 能力

不实现：

~~~text
AgentLoop
Session
SessionStore
ToolRegistry
ModelRegistry
ContextManager
Compaction
ExtensionHost
SkillLoader
MCP Runtime
Planner
Memory
TaskEngine
Workflow / DAG
Multi-Agent
~~~

---

## 3.2 不做完整 Office Runtime

只支持：

~~~text
DOCX read
~~~

不支持：

- XLSX；
- PDF；
- PPTX；
- OCR；
- DOC；
- XLS；
- WPS COM；
- Office COM。

---

## 3.3 不做写能力

不实现：

- create；
- patch；
- version；
- diff；
- validate；
- overwrite；
- save-as。

本阶段是严格 read-only。

---

## 3.4 不冻结最终 Artifact Contract

本阶段返回一个最小 `OfficeReadResult`。

不因为 Legacy 中已经存在：

~~~text
Artifact
ArtifactBlock
ArtifactLocator
~~~

就直接复制旧 Contract。

Artifact VNext 的正式 Contract 必须由后续多个 Office 用例共同驱动。

---

## 3.5 不做常驻 Python Runtime

本阶段采用：

~~~text
one tool call
→ one Python subprocess
→ one JSON request
→ one JSON response
→ process exit
~~~

不实现：

- daemon；
- worker pool；
- socket server；
- named pipe；
- long-lived JSON-RPC server；
- process supervisor。

只有性能数据证明进程启动成本成为真实失败模式后才升级。

---

## 3.6 不做独立 GUI

本阶段使用：

- Pi 原生 TUI；或
- 一个最小 TypeScript SDK runner。

不迁移 PySide6 Desktop。

---

# 4. Architecture Alignment

## 4.1 Baseline

本规格严格依赖：

> **HMBuddy Architecture Baseline V1.0 — Pi-native Banking Office Agent**

不修改 V1.0 Ownership Boundary。

---

## 4.2 Pi Public Contracts Used

本阶段只允许依赖 Pi 公开接口：

### TypeScript SDK

~~~text
createAgentSession()
SessionManager.inMemory()
DefaultResourceLoader
AgentSession.subscribe()
AgentSession.prompt()
~~~

### Extension API

~~~text
ExtensionAPI
pi.registerTool()
tool lifecycle
Tool Result
~~~

### Pi Resource Loading

通过：

~~~text
DefaultResourceLoader.additionalExtensionPaths
~~~

加载 HMBuddy Extension。

不 import Pi 的：

- private source path；
- internal session implementation；
- internal loop implementation；
- unexported Tool Registry；
- experimental plugin API。

---

## 4.3 Why SDK, not Pi RPC

V1.0 明确把 TypeScript 定义为默认 Pi-native Host。

本阶段选择：

> **in-process Pi TypeScript SDK**

而不是：

~~~text
HMBuddy host
↓
Pi RPC subprocess
~~~

原因：

1. SDK 是 Pi 对 Node/Bun 的一等集成接口；
2. 可直接访问 Session / ResourceLoader / extensions / tool events；
3. HMBuddy 未来需要长期跟进 Pi，SDK 能最大程度减少自建协议层；
4. Python 已经承担一个明确进程边界，不需要再增加第二个 Pi process boundary。

RPC 保留为未来：

- 非 TypeScript GUI；
- 强进程隔离；
- 外部客户端；

的可选方案。

---

## 4.4 Why Extension, not custom Agent framework

`read_office_file` 属于：

> executable Agent behavior

所以进入：

~~~text
Pi Extension
  ↓
pi.registerTool()
~~~

不进入：

- HMBuddy Plugin Runtime；
- HMBuddy ToolRegistry；
- HMBuddy AgentLoop。

---

## 4.5 HMBuddy-owned Domain

本阶段新增的长期 Ownership 只有：

~~~text
Office Bridge
DOCX read implementation
OfficeReadResult
Office-specific tests
~~~

---

## 4.6 Legacy Migration

本阶段默认：

> **零 Legacy runtime 代码迁移。**

禁止直接迁移：

~~~text
workspace/
plugin_runtime/
llm/
application/
desktop/
services/
~~~

Legacy 中的 DOCX parsing 代码可以作为**行为参考**，但 VNext-01 首选重新写一个最小 DOCX reader。

只有当新实现遇到一个 Legacy 已经解决、且仍有价值的具体 failure mode 时，才按能力提取旧算法。

---

## 4.7 Architecture Change Threshold

本阶段：

- 不 Fork Pi；
- 不修改 Pi；
- 不新增 HMBuddy Agent Kernel；
- 不新增平行 Extension System；
- 不新增 Session Framework。

因此**不触发新的 Architecture Change**。

---

# 5. Target Runtime

## 5.1 Logical Architecture

~~~text
┌────────────────────────────────────────────┐
│ Pi                                        │
│ AgentSession / Model / Agent Loop          │
└──────────────────┬─────────────────────────┘
                   │ Tool Call
                   ▼
┌────────────────────────────────────────────┐
│ packages/hmbuddy-pi                       │
│ HMBuddy Office Extension                  │
│ read_office_file                          │
└──────────────────┬─────────────────────────┘
                   │ OfficeBridge.read()
                   ▼
┌────────────────────────────────────────────┐
│ TypeScript Subprocess Bridge              │
│ child_process.spawn()                     │
└──────────────────┬─────────────────────────┘
                   │ stdin/stdout JSONL
                   ▼
┌────────────────────────────────────────────┐
│ office-runtime                            │
│ Python hmbuddy_office_bridge              │
│ DOCX reader                               │
└──────────────────┬─────────────────────────┘
                   │
                   ▼
              Local DOCX File
~~~

---

# 6. Proposed Repository Shape

VNext-01 只新增最少目录：

~~~text
HMBuddy/
│
├─ packages/
│  └─ hmbuddy-pi/
│     ├─ package.json
│     ├─ tsconfig.json
│     ├─ src/
│     │  ├─ runner.ts
│     │  ├─ extension/
│     │  │  └─ office.ts
│     │  └─ office-bridge/
│     │     ├─ client.ts
│     │     └─ protocol.ts
│     └─ tests/
│
├─ office-runtime/
│  ├─ pyproject.toml
│  ├─ hmbuddy_office_bridge/
│  │  ├─ __init__.py
│  │  ├─ __main__.py
│  │  ├─ protocol.py
│  │  └─ docx_reader.py
│  └─ tests/
│
├─ evals/
│  └─ fixtures/
│     └─ vnext/
│        └─ sample.docx
│
└─ requirements/
   └─ vnext-01-pi-native-bootstrap-integration-spike-v0.1.md
~~~

这不是最终 monorepo 结构，只是 Spike 的最小可执行布局。

---

# 7. Dependency Strategy

## 7.1 Pi

必须精确锁定：

~~~json
"@earendil-works/pi-coding-agent": "1.0.0"
~~~

禁止：

~~~json
"@earendil-works/pi-coding-agent": "latest"
~~~

也不在 Spike 第一版使用：

~~~json
"^1.0.0"
~~~

因为第一目标是建立可复现基线。

---

## 7.2 Node

Pi 1.0.0 当前要求：

~~~text
Node >= 22.19.0
~~~

HMBuddy VNext-01 必须与该要求一致，不额外降低版本兼容。

---

## 7.3 Python

建议：

~~~text
Python >= 3.10
python-docx
~~~

VNext-01 不引入 Legacy 的完整依赖集合。

---

# 8. Pi Host

## 8.1 runner.ts

`runner.ts` 只负责 Composition Root：

1. 决定 `cwd`；
2. 创建 `DefaultResourceLoader`；
3. 加载 HMBuddy Office Extension；
4. 创建 `AgentSession`；
5. 订阅必要事件；
6. 接收用户 Prompt；
7. 等待 Agent settled；
8. 输出最终回答；
9. dispose。

禁止在 runner 中：

- 读 DOCX；
- 路由 Office 格式；
- 自己决定是否调用 Tool；
- 自己维护 conversation history；
- 自己实现 tool loop。

---

## 8.2 Session Policy in Spike

为了避免把“持久 Session”问题带进第一条链：

~~~text
SessionManager.inMemory()
~~~

VNext-01 使用内存 Session。

这不是未来产品结论。

它只是把本阶段变量限制为：

> Pi Agent ↔ HMBuddy Tool ↔ Python Office Runtime

持久化 Session 在后续专门验证。

---

## 8.3 Tool Set

本阶段应尽量关闭与验收目标无关的高能力 built-in tools。

目标状态：

~~~text
active tools:
- read_office_file
- only the minimum Pi built-ins needed for the selected test harness
~~~

尤其不依赖：

- bash；
- edit；
- write；

来完成验收场景。

否则模型可能绕过 `read_office_file`，使 Spike 失去验证意义。

---

# 9. HMBuddy Pi Extension

## 9.1 Extension Responsibility

`office.ts` 只负责：

1. 注册 `read_office_file`；
2. 校验 Tool arguments；
3. 调用 `OfficeBridgeClient`；
4. 把 Office result 转成 Pi Tool Result；
5. 保留 structuredContent；
6. 将 Office Error 映射成可观察 Tool Error。

它不负责：

- 格式解析；
- subprocess 之外的进程平台；
- Session；
- Model；
- Prompt composition。

---

## 9.2 Tool Contract

Tool name：

~~~text
read_office_file
~~~

建议描述：

> Read a supported local Office document through HMBuddy's structured Office runtime. Use this for DOCX content instead of treating the file as plain text.

V0.1 参数：

~~~json
{
  "path": "string"
}
~~~

暂不加入：

- mode；
- pages；
- ranges；
- query；
- sheet；
- locator。

这些由真实需求驱动。

---

## 9.3 Tool Result

成功：

~~~json
{
  "content": [
    {
      "type": "text",
      "text": "Document: sample.docx\n...model-facing representation..."
    }
  ],
  "structuredContent": {
    "protocol_version": "0.1",
    "ok": true,
    "document": {}
  },
  "details": {}
}
~~~

核心原则：

- `content`：给模型；
- `structuredContent`：给程序 / Codemode / future integrations；
- `details`：只保存 Pi rendering / reconstruction 必需信息。

模型文本与结构数据不要混成唯一字符串。

---

# 10. Office Bridge Protocol V0.1

## 10.1 Transport

本阶段采用：

> **one-shot subprocess + line-delimited JSON**

TypeScript：

~~~text
spawn(python, ["-m", "hmbuddy_office_bridge"])
↓
stdin.write(JSON.stringify(request) + "\n")
↓
read exactly one JSON response line from stdout
↓
wait exit
~~~

Python：

~~~text
stdin one line
↓
parse
↓
execute
↓
stdout one JSON line
↓
exit
~~~

### stdout rule

`stdout` 只能输出 protocol JSON。

所有：

- log；
- debug；
- warning；
- traceback；

必须进入 `stderr`。

否则 framing 视为协议失败。

---

## 10.2 Request

V0.1：

~~~json
{
  "protocol_version": "0.1",
  "request_id": "uuid-or-correlation-id",
  "operation": "read",
  "path": "relative/or/absolute/path"
}
~~~

---

## 10.3 Response — Success

~~~json
{
  "protocol_version": "0.1",
  "request_id": "...",
  "ok": true,
  "document": {
    "kind": "docx",
    "source_name": "sample.docx",
    "blocks": [
      {
        "type": "paragraph",
        "text": "项目编号：HM-001"
      },
      {
        "type": "table",
        "rows": [
          ["负责人", "张三"]
        ]
      }
    ],
    "plain_text": "项目编号：HM-001\n负责人：张三"
  }
}
~~~

注意：

> `document` 当前不是正式 Artifact Contract。

它只是 Spike transport DTO。

---

## 10.4 Response — Failure

~~~json
{
  "protocol_version": "0.1",
  "request_id": "...",
  "ok": false,
  "error": {
    "code": "FILE_NOT_FOUND",
    "message": "File does not exist",
    "details": {}
  }
}
~~~

错误码至少：

~~~text
INVALID_REQUEST
UNSUPPORTED_PROTOCOL
FILE_NOT_FOUND
UNSUPPORTED_FORMAT
PATH_NOT_ALLOWED
PARSE_ERROR
INTERNAL_ERROR
~~~

TypeScript Bridge 自身增加：

~~~text
PYTHON_NOT_FOUND
PROCESS_START_FAILED
PROCESS_TIMEOUT
PROCESS_EXIT_FAILED
INVALID_RESPONSE
PROTOCOL_MISMATCH
~~~

---

# 11. DOCX Reader V0.1

Python V0.1 只支持：

- ordinary paragraphs；
- tables；
- document order 尽可能保持；
- unicode text；
- empty paragraph 可跳过。

最低输出 block：

~~~text
paragraph
table
~~~

不要求：

- styles；
- heading semantic；
- nested tables；
- images；
- comments；
- tracked changes；
- headers / footers；
- footnotes；
- shapes；
- exact visual layout。

这些不是 Spike 成败条件。

---

# 12. Path Boundary

即使是 Spike，也不能让 Office Tool 接受任意路径而毫无边界。

V0.1 定义：

~~~text
allowed_root = runner cwd
~~~

Python 与 TypeScript 均应使用 canonical resolved path 检查：

~~~text
target.resolve()
must be inside
allowed_root.resolve()
~~~

不能使用纯字符串前缀比较。

拒绝：

- `../` escape；
- canonical path 越界；
- 非文件；
- 非 `.docx`。

注意：

> 这是 HMBuddy Tool 的资源边界，不把它误称为完整 OS sandbox。

Pi 进程本身的系统权限仍然是更大的安全边界问题。

---

# 13. Timeout and Process Lifecycle

V0.1 推荐：

~~~text
office bridge timeout: 10 s
~~~

超时：

1. terminate Python child；
2. 必要时 kill；
3. 返回 `PROCESS_TIMEOUT`；
4. 不让 Agent run 无限等待。

V0.1 不实现自动 retry。

原因：

> parse failure 的 retry policy 还没有证据，自动重试可能隐藏确定性错误。

---

# 14. Model-facing Representation

Python 返回丰富 DTO 后，TypeScript Tool 负责生成一个有限的模型表示。

规则：

1. 结构数据保留在 `structuredContent`；
2. model-facing text 必须有大小上限；
3. 如果截断，显式告诉模型；
4. 不声称模型看到了完整文件；
5. 默认不把机器绝对路径写入 `content`。

建议 V0.1：

~~~text
MAX_MODEL_CHARS = 20_000
~~~

截断格式：

~~~text
[HMBuddy Office Runtime]
Document: sample.docx
Kind: docx

...

[TRUNCATED: structured document contains more content]
~~~

这只是 Tool representation policy，不建设新的 ContextManager。

---

# 15. Test Fixture

必须新建 VNext 专用 DOCX fixture。

内容应足够判断 Agent 是否真的拿到了结构化结果，例如：

~~~text
HMBuddy Integration Spike

项目编号：HM-VNEXT-001
项目负责人：林海
目标：验证 Pi 调用 Python Office Runtime。

表格：
字段 | 值
环境 | Bank Intranet
Runtime | Pi + Python
状态 | Spike
~~~

用户验收 Prompt：

> 阅读 `evals/fixtures/vnext/sample.docx`。告诉我项目编号、负责人、Runtime，并说明这些信息来自文件内容。

期望事实：

~~~text
HM-VNEXT-001
林海
Pi + Python
~~~

不能依赖文件名猜答案。

---

# 16. Testing Strategy

测试分四层。

## T1 — Python Protocol Unit

验证：

- valid request；
- invalid JSON；
- wrong protocol version；
- file not found；
- unsupported suffix；
- valid DOCX；
- paragraphs；
- tables；
- stdout only JSON；
- error output schema。

不需要 Pi。

---

## T2 — TypeScript Bridge Unit

使用 fake Python executable / fixture process 验证：

- request framing；
- response parsing；
- stderr ignored as protocol；
- invalid stdout；
- timeout；
- nonzero exit；
- request_id correlation；
- protocol mismatch。

不需要模型。

---

## T3 — Pi Extension Contract Smoke

创建：

~~~text
AgentSession
+ DefaultResourceLoader
+ HMBuddy extension
+ in-memory session
~~~

验证：

- Extension 可加载；
- `read_office_file` 已注册；
- Tool metadata/schema 正确；
- 不需要 HMBuddy ToolRegistry；
- session dispose 后 bridge 无悬挂进程。

不要求真实 LLM Tool Call。

---

## T4 — Live End-to-End Agent Eval

需要可用模型配置。

执行真实 Prompt：

~~~text
Pi Agent
→ model chooses read_office_file
→ Python parses DOCX
→ tool_result
→ model final answer
~~~

必须从 Pi event stream 观察到：

1. `read_office_file` tool call；
2. tool success；
3. final assistant answer；
4. answer 包含 fixture 三项关键事实。

### T4 不是普通 CI hard gate

因为它依赖真实模型。

应作为：

~~~text
optional / configured live eval
~~~

但至少在阶段验收时人工或受控环境完整跑通一次。

---

# 17. Architecture Guard Tests

VNext-01 应加入少量静态守护，防止项目重新滑回旧架构。

至少禁止新代码出现：

~~~text
class AgentLoop
class ToolRegistry
class SessionStore
class ExtensionHost
~~~

以及 VNext TS package 直接 import：

~~~text
plugin_runtime
llm
application
desktop
~~~

这不是说这些字符串永远违法，而是通过 guard 明确：

> VNext-01 不允许通过“偷偷复用旧 Framework”完成 Spike。

---

# 18. Observability

不建设新 telemetry platform。

最低可观察信息：

~~~text
request_id
tool_call_id
operation
source_name
duration_ms
python_exit_code
result_status
error_code
truncated
~~~

不要默认记录：

- 完整文档内容；
- Prompt 全文；
- 敏感文件绝对路径。

V0.1 输出可进入 stderr / test capture。

---

# 19. Security Boundary

## 19.1 Pi Reality

Pi 的 working directory / project trust：

> 不是完整 filesystem / process 安全边界。

所以 Spike 不能因为使用了 `cwd` 就声称“银行级隔离已完成”。

---

## 19.2 V0.1 Security Goal

只验证：

- Office Tool path scope；
- read-only；
- no network；
- no write；
- no COM；
- no arbitrary Python operation。

---

## 19.3 Later Governance

以下留给后续 Stage：

- sandbox；
- dedicated OS user；
- network allowlist；
- approval；
- audit persistence；
- sensitive data rules。

---

# 20. Failure Modes

必须明确处理以下失败。

| Failure | Expected behavior |
|---|---|
| Python 未安装 | Tool error: `PYTHON_NOT_FOUND` |
| python-docx 缺失 | `INTERNAL_ERROR` / startup diagnostic，不能假成功 |
| DOCX 不存在 | `FILE_NOT_FOUND` |
| 读取 PDF | `UNSUPPORTED_FORMAT` |
| 路径越界 | `PATH_NOT_ALLOWED` |
| DOCX 损坏 | `PARSE_ERROR` |
| Python 输出额外 stdout 文本 | `INVALID_RESPONSE` |
| response protocol != 0.1 | `PROTOCOL_MISMATCH` |
| subprocess 卡死 | kill + `PROCESS_TIMEOUT` |
| Pi model 不调用 Tool | T4 fail；不能由 runner 代替模型调用来“补成功” |
| 模型调用其他 built-in tool 绕过 Office Tool | T4 fail / test harness 应限制 active tools |
| Tool 成功但模型答案事实错误 | T4 fail，记录 Agent-level failure，而不是 parser success |

---

# 21. Acceptance Criteria

## AC-01 Pi-native

VNext Host 使用官方 Pi SDK 创建真实 `AgentSession`。

---

## AC-02 No custom Agent Kernel

代码中不存在 HMBuddy 自研：

- AgentLoop；
- SessionStore；
- ToolRegistry；
- Model Runtime；
- ExtensionHost。

---

## AC-03 Extension

`read_office_file` 通过 Pi `registerTool()` 注册。

---

## AC-04 Process Boundary

Tool 不 import Python Office parser。

必须通过 subprocess stdio 调用。

---

## AC-05 DOCX Structured Read

Fixture 至少返回：

- paragraph；
- table；
- plain_text representation。

---

## AC-06 Protocol

Request / response 带：

~~~text
protocol_version
request_id
ok
~~~

并对版本 mismatch 明确失败。

---

## AC-07 Path Boundary

`../` 和 canonical escape 均被拒绝。

---

## AC-08 No Legacy Framework Reuse

VNext Spike 不依赖：

~~~text
workspace/
plugin_runtime/
llm/
application/
desktop/
~~~

---

## AC-09 Deterministic Tests

T1–T3 不需要联网和真实模型即可通过。

---

## AC-10 Real Agent Tool Call

至少一次受控 Live Eval 证明：

> Tool 是模型在 Pi AgentLoop 中自主调用的。

不是 host 手工先执行 Tool。

---

## AC-11 Fact Recovery

最终回答正确包含：

~~~text
HM-VNEXT-001
林海
Pi + Python
~~~

---

## AC-12 Upgrade Boundary

所有 Pi-specific imports 集中在：

~~~text
packages/hmbuddy-pi/
~~~

Python Office Runtime 完全不知道 Pi。

---

# 22. Implementation Order

严格按以下顺序：

## Step 1 — Bootstrap TypeScript package

只完成：

- package.json；
- exact Pi 1.0.0；
- TS config；
- minimal `createAgentSession()` smoke。

验收：

> Pi SDK 能运行。

---

## Step 2 — Register deterministic dummy Tool

先实现：

~~~text
hmbuddy_echo
~~~

不接 Python。

验收：

> HMBuddy Extension 被 Pi 正确加载和注册。

完成后 dummy Tool 可以删除。

---

## Step 3 — Python Protocol CLI

先独立实现：

~~~text
echo '{"operation":"read", ...}' | python -m hmbuddy_office_bridge
~~~

得到一行 JSON。

验收：

> Office Runtime 不依赖 Pi 也可以独立测试。

---

## Step 4 — DOCX Reader

加入新 VNext fixture。

完成 T1。

---

## Step 5 — TypeScript OfficeBridgeClient

完成 T2。

---

## Step 6 — read_office_file Tool

完成 T3。

---

## Step 7 — Real Pi Agent Eval

完成 T4 / AC-10 / AC-11。

---

## Step 8 — Spike Review

只在真实结果出来后决定：

- 是否保留 subprocess 模型；
- 是否开始 XLSX / PDF；
- 是否正式设计 Artifact VNext；
- 是否清理 Legacy main code；
- 是否需要 dedicated UI。

---

# 23. Explicit Stop Conditions

如果出现以下任意一种情况，本阶段应停止继续堆功能并重新评审架构：

1. Pi Extension 无法可靠注册 Office Tool；
2. Pi SDK 无法满足目标内网模型；
3. Windows 上 TypeScript ↔ Python subprocess 极不稳定；
4. Pi API 需要大量 private imports 才能完成基础 Tool integration；
5. HMBuddy 必须修改 Pi AgentLoop 才能实现读取 DOCX；
6. path / permission 无法通过 Extension 边界治理；
7. Pi 版本升级导致 Integration Layer 必须大范围侵入 Office Domain。

这些都是 V1.0 可能需要修正的证据，而不是“继续多写代码解决”的理由。

---

# 24. Deliverables

本阶段代码完成时至少交付：

~~~text
packages/hmbuddy-pi/
office-runtime/
evals/fixtures/vnext/sample.docx
tests for T1-T3
one live T4 record / eval result
README quickstart
Pi compatibility record
~~~

并形成：

~~~text
docs/upstream/pi-1.0.0-compatibility.md
~~~

至少记录：

- tested Pi version；
- Node version；
- Python version；
- Windows result；
- extension result；
- tool result；
- known incompatibilities。

---

# 25. What Success Means

VNext-01 成功不意味着：

> HMBuddy 已经是完整 Office Agent。

它只意味着：

> **新的 Ownership Boundary 经真实代码证明成立。**

也就是：

~~~text
Pi really owns the Agent.
HMBuddy really owns the Office capability.
The boundary between them is small and replaceable.
~~~

只要这件事成立，VNext 后续才有资格进入：

~~~text
VNext-02 Office Read Pack
VNext-03 Office Write Lifecycle
VNext-04 Banking Skills
VNext-05 Banking Governance
...
~~~

而不是回到“把通用 Agent Framework 再造一遍”的路线。
