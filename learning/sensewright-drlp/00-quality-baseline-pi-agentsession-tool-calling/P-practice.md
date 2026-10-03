# P — Practice：把 Pi Tool Calling 放进 HMBuddy VNext-01

> 目标：让已经理解 vertical slice 的人知道真正打开 HMBuddy IDE 后怎么做。  
> 状态：Execution-ready engineering walkthrough；Pi upstream mechanism 已有 checked test，HMBuddy VNext runtime 尚待实际实施后回填 test/trace。  
> 原则：不因为文档写得具体，就把未运行代码写成“已验证”。

---

# 1. Real Engineering Scenario

VNext-01 的唯一目标：

> 用户要求读取一个 DOCX；模型通过 Pi AgentLoop 自主选择 read_office_file；HMBuddy Tool 调 Python 读取文件；结果回到 Pi；模型基于结果回答。

验收输入：

~~~text
阅读 evals/fixtures/vnext/sample.docx。
告诉我项目编号、负责人、Runtime，并说明这些信息来自文件内容。
~~~

fixture 三个关键事实：

~~~text
HM-VNEXT-001
林海
Pi + Python
~~~

---

# 2. 系统位置

~~~text
                    Pi owns
┌─────────────────────────────────────────┐
│ AgentSession                            │
│   ↓                                     │
│ Agent / AgentLoop                       │
│   ↓ toolCall                            │
│ Extension Tool Runtime                  │
└───────────────┬─────────────────────────┘
                │ execute()
                ▼
                 HMBuddy owns
┌─────────────────────────────────────────┐
│ read_office_file Tool adapter           │
│   ↓                                     │
│ OfficeBridgeClient                      │
│   ↓ subprocess JSONL                    │
│ Python Office Runtime                   │
│   ↓                                     │
│ DOCX parser                             │
└─────────────────────────────────────────┘
~~~

如果 implementation 开始出现 HMBuddy AgentLoop、ToolRegistry、SessionStore、ModelRuntime，应立即停止评审。

---

# 3. 第一批工程对象

~~~text
packages/hmbuddy-pi/
├─ package.json
├─ tsconfig.json
└─ src/
   ├─ runner.ts
   ├─ extension/
   │  └─ office.ts
   └─ office-bridge/
      ├─ protocol.ts
      └─ client.ts

office-runtime/
├─ pyproject.toml
└─ hmbuddy_office_bridge/
   ├─ __init__.py
   ├─ __main__.py
   ├─ protocol.py
   └─ docx_reader.py

evals/fixtures/vnext/
└─ sample.docx
~~~

---

# 4. runner.ts：只做 Composition Root

职责：

~~~text
cwd
→ ResourceLoader
→ AgentSession
→ event subscription
→ prompt
→ final result
→ dispose
~~~

禁止：

~~~text
runner 先读 DOCX
runner 根据用户文本 if/else 决定调用 Python
runner 把文件内容手工拼进 prompt
~~~

否则最终答案即使正确，核心实验仍失败。

---

# 5. office.ts：最薄的 Pi ↔ HMBuddy 边界

Tool 输入第一版只有：

~~~json
{
  "path": "string"
}
~~~

不提前加 sheet / page / range / query / locator / mode。

Tool contract 要体现 Pi 1.0 正式能力：

~~~text
name
label
description
parameters
outputSchema
annotations
execute
~~~

特别是：

~~~text
readOnlyHint = true
destructiveHint = false
openWorldHint = false
~~~

以及：

~~~text
outputSchema
+
structuredContent
~~~

应同时设计。

职责：

> Extension 只把 Pi Tool Contract 翻译到 HMBuddy Office capability，不自己解析 DOCX。

---

# 6. OfficeBridgeClient：故意保持笨

第一版：

~~~text
one Tool call
→ one Python process
→ one JSON request line
→ one JSON response line
→ exit
~~~

不要提前引入 WorkerPool、ConnectionManager、RetryEngine、CapabilityRouter。

request：

~~~json
{
  "protocol_version": "0.1",
  "request_id": "...",
  "operation": "read",
  "path": "evals/fixtures/vnext/sample.docx"
}
~~~

success response：

~~~json
{
  "protocol_version": "0.1",
  "request_id": "...",
  "ok": true,
  "document": {
    "kind": "docx",
    "source_name": "sample.docx",
    "blocks": [],
    "plain_text": "..."
  }
}
~~~

---

# 7. Python Runtime：只知道 Office

hmbuddy_office_bridge 不理解：

~~~text
Session
AgentLoop
Model
Prompt
Memory
Planner
~~~

main path：

~~~text
read one stdin line
→ parse JSON
→ validate protocol
→ call operation
→ print one JSON line
→ exit
~~~

日志全部 stderr。

---

# 8. Path boundary

概念上：

~~~text
target = canonical resolve(path)
allowed_root = canonical approved root

target must be inside allowed_root
~~~

不能做纯字符串前缀比较。

HMBuddy 实施时建议显式传 approved root，而不是让 process cwd 悄悄兼任安全配置。

但它仍不是 OS sandbox。

---

# 9. T1 — Python Protocol Test

完全不碰 Pi。

覆盖：

~~~text
valid request
invalid JSON
wrong protocol
file not found
unsupported suffix
path escape
valid DOCX
paragraph
table
stdout purity
error schema
~~~

证明 Python Office Runtime 自己是独立确定 capability。

---

# 10. T2 — TypeScript Bridge Test

不用模型。

验证：

~~~text
request framing
response parse
stderr ignored
extra stdout → INVALID_RESPONSE
request_id mismatch
protocol mismatch
timeout
non-zero exit
~~~

证明 TS ↔ Python process boundary 独立可工作。

---

# 11. T3 — Pi Extension Contract Smoke

创建真实：

~~~text
AgentSession
+
DefaultResourceLoader
+
HMBuddy Extension
+
SessionManager.inMemory()
~~~

但不调用模型。

断言：

~~~text
read_office_file registered
read_office_file active
schema correct
outputSchema correct
annotations correct
no HMBuddy ToolRegistry
dispose clean
~~~

状态只能是 Ready for Live Validation，不能写 Complete。

---

# 12. T4 — 真正的 Agent 验收

真实模型收到用户请求。

trace 至少捕获：

~~~text
tool_execution_start
  toolName = read_office_file

tool_execution_end
  success

message_end
  final assistant response

agent_settled
~~~

最终答案包含：

~~~text
HM-VNEXT-001
林海
Pi + Python
~~~

而 runner 不允许提前执行读取。

只有这一步通过，才证明：

> **Pi 真正拥有 Agent control loop；HMBuddy 只是提供 Office action。**

---

# 13. 主动制造失败一：路径逃逸

输入：

~~~text
../secret.docx
~~~

预期：

~~~text
PATH_NOT_ALLOWED
~~~

排查：

~~~text
Tool args
→ canonical target
→ allowed root comparison
~~~

修复不是放宽全盘读取，而是设置正确 approved root 或让用户选择合法 workspace/file。

回归：

~~~text
inside root → success
../ escape → PATH_NOT_ALLOWED
canonical escape → PATH_NOT_ALLOWED
~~~

教会的是：

> Agent Tool 的 action space 必须有 deterministic resource boundary，不能只靠 Prompt 说“不要乱读”。

---

# 14. 主动制造失败二：Python 卡死

让 fake Python process 不返回。

预期：

~~~text
10s
→ terminate
→ necessary kill
→ PROCESS_TIMEOUT
~~~

排错顺序：

~~~text
child 是否启动
stdin 是否写入
stdout 是否有合法 line
timeout 是否触发
child close 是否 await
active child 是否清理
~~~

第一版不自动 retry，因为没有证据表明 retry 能解决 parser hang。

---

# 15. 实现后应回填的真实 trace

~~~text
[host] session created
[host] active tools = read_office_file
[user] read sample.docx...
[pi] tool_execution_start read_office_file
[bridge] request_id=... op=read source=sample.docx
[python] ok=true duration_ms=...
[pi] tool_execution_end read_office_file ok
[assistant] 项目编号 HM-VNEXT-001...
[pi] agent_settled
~~~

默认 trace 不记录文件全文、敏感 Prompt、机器绝对路径。

---

# 16. 哪些是 Pi 原理，哪些是 HMBuddy 当前选择

## Pi / Agent 原理

~~~text
模型看到 Tool declaration
模型产生 toolCall
Pi runtime 验证并执行
Tool Result 进入后续 context
模型基于 Observation 再决策
没有更多 action 后结束
~~~

## HMBuddy VNext-01 选择

~~~text
TypeScript host
Python Office Runtime
subprocess
JSONL
protocol_version 0.1
10s timeout
DOCX only
MAX_MODEL_CHARS = 20000
approved root
~~~

subprocess 未来可以换 named pipe，而 Agent 原理不变。

---

# 17. Practice 完成判据

真正实施后，陌生读者应该能：

1. 打开 repo 知道第一批文件在哪里；
2. 知道为什么 runner 不能先读 DOCX；
3. 写出一个 Pi Extension Tool；
4. 写出 TS ↔ Python request/response；
5. 跑 T1/T2/T3；
6. 看懂 T4 trace；
7. 故意制造 path escape 或 timeout；
8. 沿边界排错；
9. 分清哪个问题属于 Pi，哪个属于 HMBuddy Office Runtime。

---

# 18. 当前状态

当前已有：

~~~text
D/R: SOURCE-GROUNDED
L: MECHANISM-VALIDATED
P: EXECUTION-READY, HMBUDDY RUNTIME PENDING
~~~

VNext-01 真正跑通后，本文件必须补：

~~~text
实际 commit
实际命令
实际 test result
实际 trace
实际 failure reproduction
~~~

然后才升级：

~~~text
PRACTICE-VALIDATED
QUALITY-BASELINE
~~~

这条纪律比“文件看起来完整”更重要。
