# L — Learning：让 Pi Tool Calling 真正跑一次

> 目标：不再用“Model → Tool → Observation → Model”这句话假装理解。  
> 执行证据：Pi checked test agent-session-tool-orchestration.test.ts。  
> 说明：这里使用 deterministic assistant responses，因此能真实观察 runtime mechanism；它不是 HMBuddy live-model T4。

---

# 1. 为什么先用 deterministic test

如果一开始接真实模型，会同时混入：

- provider；
- API key；
- 模型是否愿意调用 Tool；
- Tool description 质量；
- sampling；
- provider tool-call dialect。

这会遮住真正要学的机制：

> **当 assistant message 已经包含 toolCall 时，Pi runtime 到底做什么？**

Pi 自己的 test harness 能固定模型响应，让 control flow 可观察。

---

# 2. Ground Object

Pi 的 tool orchestration 测试注册：

~~~text
echo
helper
run_tools
~~~

我们关注顶层链：

~~~text
User "go"
→ assistant toolCall(run_tools)
→ Pi executes run_tools
→ ToolResultMessage
→ assistant "done"
~~~

这是真实 checked test，不是伪代码。

---

# 3. T0 — Session 已存在，Tool loadout 已建立

测试创建 harness 并绑定 extensions。

此时测试会检查 session.getActiveToolNames()。

第一个机制认识：

> **模型是否可能调用某个 Tool，首先取决于 runtime 是否把它放进当前 declared tool set。**

Tool implementation 存在，不等于模型一定看到。

---

# 4. T1 — 用户输入 "go"

测试调用：

~~~text
await harness.session.prompt("go")
~~~

从 AgentSession 角度：

~~~text
"go"
→ input / prompt processing
→ user AgentMessage
→ low-level Agent run
~~~

---

# 5. T2 — 第一次 assistant response 是 Tool Call

test harness 预设：

~~~text
toolCall:
  name = run_tools
  args = {}
stopReason = toolUse
~~~

Pi 没有“猜”模型想干什么。

模型响应本身携带结构化 action request。

---

# 6. T3 — AgentLoop 识别 Tool Call

进入 packages/agent/src/agent-loop.ts。

loop 在 assistant response 后筛：

~~~text
message.content.filter(type == toolCall)
~~~

找到 run_tools，所以不能结束，进入 executeToolCalls(...)。

---

# 7. T4 — Tool execution 不是模型执行

概念上：

~~~text
toolCall(run_tools)
        ↓
runtime validates / resolves
        ↓
ToolDefinition.execute(...)
~~~

最关键的一句：

> **模型拥有动作选择权，但不拥有直接代码执行权。**

模型提交 action intent。

runtime 决定 Tool 是否存在、参数是否合法、lifecycle hook 是否阻断、如何执行、返回什么。

---

# 8. T5 — Tool Result 变成新的 message

run_tools 最终产生 Tool Result。

Pi 不把它直接当“最终 assistant reply”。

agent-loop.ts 把 ToolResultMessage push 回 currentContext.messages。

context 从：

~~~text
System
User("go")
Assistant(toolCall run_tools)
~~~

变成：

~~~text
System
User("go")
Assistant(toolCall run_tools)
ToolResult(...)
~~~

这是 control loop 最关键的状态变化。

---

# 9. T6 — 为什么模型自动再跑一次

刚才出现 Tool Call，且 batch 没有 terminate。

因此：

~~~text
hasMoreToolCalls = true
~~~

内层 loop 继续，runtime 再请求 assistant。

第二次 request 的关键变化：

> **Context 多了真实动作产生的 Observation。**

---

# 10. T7 — 第二次 response = done

test harness 的第二个 assistant response 是 done。

这次不再包含 Tool Call。

如果没有 steering、follow-up、explicit continuation，loop 自然结束。

---

# 11. 状态变化表

| 时刻 | 新增事实 | 谁决定 | 为什么下一步发生 |
|---|---|---|---|
| T0 | Tool 已注册并 active | Extension + Pi runtime | 模型 request 可以声明 Tool |
| T1 | User "go" | User | AgentSession 启动 run |
| T2 | toolCall(run_tools) | Assistant/model | loop 发现 action request |
| T3 | executeToolCalls | Pi runtime | Tool Call 必须验证并执行 |
| T4 | Tool Result | Tool implementation | 动作产生 Observation |
| T5 | Result 加入 context | Pi AgentLoop | 下一次模型必须看到结果 |
| T6 | 第二次模型 request | Pi AgentLoop | hasMoreToolCalls 使 loop 继续 |
| T7 | assistant "done" | Assistant/model | 无更多 action，可结束 |

现在再说 Decide → Act → Observe → Decide，才不是口号。

---

# 12. HMBuddy VNext 插在 T3–T4

Pi 已拥有：

~~~text
Prompt
→ Model Tool Call
→ Tool dispatch
→ Result reinjection
→ Next model request
→ Stop
~~~

HMBuddy 真正新增：

~~~text
Pi dispatch read_office_file
        ↓
HMBuddy TS Extension
        ↓
OfficeBridge
        ↓
Python
        ↓
DOCX
        ↓
OfficeReadResult
        ↓
Tool Result
~~~

所以 HMBuddy 不应该自己实现外层 AgentLoop。

---

# 13. Boundary Variation：Tool 仍存在，但不再 active

只改变一个条件：

> Tool implementation 仍然注册，但不在 model-facing active set。

不变：

- Extension 文件还在；
- Tool implementation 还在；
- Python Runtime 还在。

第一处受影响：

> 模型 request 不再声明这个 Tool。

因此真实模型不能把它当当前允许的 direct action。

这暴露出：

> **Agent capability 不是“代码库里有什么函数”，而是“当前决策上下文里 runtime 暴露了什么 action”。**

---

# 14. Prediction Check：Python subprocess 超时

假设 read_office_file 仍 active，但 Python 超时。

根据当前 mental model，可以预测：

1. 模型仍可选择 Tool；
2. Pi 仍会进入 Tool execution；
3. HMBuddy Bridge 返回 error / throw；
4. Pi 把失败形成 Tool error observation；
5. 后续模型是否重试或向用户说明，取决于后续决策和 HMBuddy policy；
6. runner 不应该绕开 Pi 自己重读文件。

如果能从机制推出这个结果，而不是靠背规格，mental model 已经开始工作。

---

# 15. Mental Model

### AgentSession
一段 Pi Agent 工作会话的 orchestration boundary。

### Tool declaration
当前模型被允许看到和选择的 action contract。

### Tool Call
模型输出的结构化 action intent。

### Tool execution
Pi runtime 对 action intent 的受控执行。

### Tool Result / Observation
动作结果进入 conversation/context 的形式。

### Agent loop
只要 action 产生新 Observation，就继续让模型基于新状态决策，直到没有后续 action / queued work。

### HMBuddy
不拥有上述通用控制循环；它拥有某些 Tool 背后的 Office / Banking execution。

---

# 16. Learning Gate

面对另一个 Agent Framework，应主动找：

~~~text
1. 模型在哪里拿到 tool declarations？
2. toolCall 是什么数据结构？
3. 谁做参数验证？
4. Tool 实现在哪里执行？
5. Tool Result 怎么回到 context？
6. 什么条件触发下一次模型请求？
7. 什么条件让 loop 停止？
8. Session 和 low-level loop 分别拥有哪部分 state？
~~~

这比记住 Pi 文件名更重要。
