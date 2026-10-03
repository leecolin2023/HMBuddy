# D — Deep Read：Pi AgentSession / Tool Calling Vertical Slice

> 目标读者：会基本编程和 LLM 概念，但没读过 Pi，也不了解 HMBuddy V1.0。  
> Source pin：earendil-works/pi@4c6fb7cfe8c538a668726f6f8b3554098c39faee  
> 任务：不先背 Agent 定义；从一个真实问题出发，沿源码看清“一句用户请求如何变成 Tool Call，再回到模型”。

---

## 先不要想 AgentLoop，先看普通聊天程序做不到什么

假设用户对 HMBuddy 说：

> “读取 sample.docx，告诉我负责人是谁。”

如果 HMBuddy 只是普通聊天程序，最简单的做法是：

~~~text
runner
→ 读取 sample.docx
→ 把文本拼进 prompt
→ 调模型
→ 得到答案
~~~

这个方案能回答问题，却没有证明存在 Agent。

因为真正决定：

- 要不要读文件；
- 读哪个文件；
- 什么时候读；
- 读完以后下一步做什么；

的还是宿主程序。

Pi 的 Tool Calling vertical slice 改变的是控制权：

~~~text
用户给目标
→ 模型看到可用动作
→ 模型选择动作和参数
→ runtime 执行动作
→ runtime 把动作结果作为 Observation 放回上下文
→ 模型基于新事实继续决定
→ 没有更多动作时才结束
~~~

HMBuddy V1.0 为什么决定“不再自研 AgentLoop”，核心就藏在这条链里：Pi 已经把这套控制循环做成正式 runtime。

---

# 1. HMBuddy 实际从哪里进入 Pi

VNext-01 不直接 new 底层 Agent，而通过 Pi SDK 的 createAgentSession()。

它位于：

~~~text
packages/coding-agent/src/core/sdk.ts
~~~

读源码会发现，它会组合：

- working directory；
- ModelRuntime；
- SettingsManager；
- SessionManager；
- ResourceLoader；
- tools；
- extensions；
- 底层 Agent；
- 最后的 AgentSession。

第一个重要认知：

> **AgentSession 不是“聊天记录对象”。它是 Pi coding-agent 层对一段 Agent 工作会话的 runtime façade。**

HMBuddy 用 SDK 接 Pi，意味着它把很多原本准备自研的东西直接交给上游。

---

# 2. AgentSession 和 Agent 不是一个东西

在 createAgentSession() 内部，Pi 先构造底层 Agent，再把它交给 AgentSession。

粗略理解：

~~~text
Agent
= 让模型进入 Decide → Act → Observe 的底层控制循环

AgentSession
= 管理这一段具体工作会话的模型、工具、消息、扩展、compaction、queue、session state
~~~

为什么这层区分重要？

旧 HMBuddy 曾准备自研：

- AgentLoop；
- SessionStore；
- ToolRegistry；
- ExtensionHost。

Pi 当前代码已经把这些责任分布在 Agent core、AgentSession、SessionManager、Extension runtime 等正式模块里。

如果 HMBuddy 再写一套，就不是“集成 Pi”，而是在 Pi 外再套第二个 Agent runtime。

---

# 3. session.prompt() 并不是“马上打一次 LLM API”

入口位于：

~~~text
packages/coding-agent/src/core/agent-session.ts
~~~

prompt() 会先处理：

- extension command；
- extension input handler；
- skill / prompt template；
- streaming 时的 steer / follow-up；
- pending messages；
- model 是否存在；
- provider auth；
- before-agent lifecycle。

所以：

> **用户输入一句话，不等于直接调用模型。**

AgentSession 是 orchestration boundary。

这也解释为什么 HMBuddy runner.ts 不应该自己维护 conversation history、queue 或 tool loop。

---

# 4. 模型怎样知道 read_office_file 存在

模型不会凭空知道 HMBuddy 有 Python Office Runtime。

Pi 的 Extension Tool contract 定义在：

~~~text
packages/coding-agent/src/core/extensions/types.ts
~~~

一个最小 ToolDefinition 需要：

~~~text
name
label
description
parameters
execute()
~~~

这里必须分开：

### Tool declaration

告诉模型：你可以做什么、参数是什么。

### Tool execute

模型真的选这个动作后，Pi runtime 调哪个实现。

因此：

> **模型不会直接调用 Python，也不会直接“执行 office.ts”。它只产生结构化 toolCall。真正执行动作的是 Pi runtime。**

---

# 5. “模型自主调用 Tool”在源码里具体是什么意思

核心在：

~~~text
packages/agent/src/agent-loop.ts
~~~

Pi 每轮先请求模型，得到 assistant message。

然后源码明确检查：

~~~text
assistant message.content 中有没有 type = toolCall
~~~

没有 Tool Call 时，如果也没有 queued work 或 continuation，run 可以结束。

如果有 Tool Call：

~~~text
toolCalls
→ executeToolCalls(...)
→ 得到 ToolResultMessage
→ push 到 currentContext.messages
→ hasMoreToolCalls = true
→ 再进入下一轮模型请求
~~~

这就是整个 Agent vertical slice 的心脏。

---

# 6. 为什么 Tool Result 不能直接变成最终答案

假设模型调用：

~~~json
{
  "name": "read_office_file",
  "arguments": {
    "path": "sample.docx"
  }
}
~~~

Python 返回：

~~~text
项目负责人：林海
~~~

为什么 Pi 不直接把“林海”显示给用户然后结束？

因为 Tool 只负责执行动作并产生事实或状态变化，它不拥有完整用户目标。

用户可能真正问：

> “读取报告，告诉我负责人，并判断他负责的工作是否与项目目标一致。”

一次读取只解决其中一部分。

所以 Tool Result 必须回模型。模型看到原始目标、自己刚才的 action、action result，才能决定：

- 已经足够，可以回答；
- 还需要再读一个文件；
- 需要搜索；
- 工具失败，需要换策略。

因此：

> **Observation 属于下一轮决策输入，而不是最终 UI 输出。**

---

# 7. Tool Call 后为什么 loop 会自动再跑

agent-loop.ts 在 Tool Call 执行成功后把 ToolResultMessage 放回 currentContext.messages。

只要这个 Tool batch 没有要求 terminate：

~~~text
hasMoreToolCalls = true
~~~

内层 loop 继续。

下一次模型请求看到的不再只是：

~~~text
User: 读取 sample.docx
~~~

而是完整上下文，包括刚才的 Tool Result。

如果没有这一步，系统只是：

~~~text
LLM
→ function call
→ function
→ end
~~~

而不是：

~~~text
LLM
→ action
→ observation
→ LLM
→ next decision
~~~

Agent 的“自主性”主要不是多了 Tool API，而是动作结果能重新进入决策循环。

---

# 8. Session 在这条链里保存什么

不要因为低层 AgentLoop 有 currentContext，就认为 SessionManager 可有可无。

Agent loop 负责一轮控制。

AgentSession / SessionManager 还承担：

- conversation state；
- persistence / in-memory state；
- queued messages；
- compaction；
- branch；
- model / thinking changes；
- extension lifecycle；
- finalized context reconstruction。

VNext-01 使用 SessionManager.inMemory()，不是因为 Session 不重要，而是为了第一条 vertical slice 暂时排除持久化变量，只验证：

~~~text
Pi Agent
↔ HMBuddy Tool
↔ Python Office Runtime
~~~

---

# 9. Extension 在链中处于哪里

正确路径：

~~~text
HMBuddy extension
→ pi.registerTool(read_office_file)
→ Pi 把 Tool 放进当前 session tool runtime
→ active tool declaration 进入模型请求
→ 模型选择
→ Pi 执行 ToolDefinition.execute()
~~~

ownership：

~~~text
谁决定什么时候调用？
→ 模型 + Pi AgentLoop

谁负责 Tool 注册和生命周期？
→ Pi Extension runtime

谁负责读 DOCX？
→ HMBuddy Office Runtime
~~~

这就是 V1.0 的“Pi 会 Agent；HMBuddy 会银行办公”。

---

# 10. structuredContent 不是随手多返回一份 JSON

Pi 当前 Extension contract 对 structured result 有正式语义。

如果 Tool 需要 programmatic structured output，应声明 outputSchema 并返回匹配的 structuredContent。

同时 content 仍然是给模型看的 representation。

因此 HMBuddy VNext 的三分设计：

~~~text
content
structuredContent
details
~~~

方向正确。

但实施时要记住：

> **如果 HMBuddy 依赖 structuredContent 作为正式程序接口，就应该同时声明 outputSchema。**

这是读 Pi 1.0 contract 后得到的重要实施校准。

---

# 11. 什么时候才算一次 Agent 工作真正结束

Pi 暴露：

~~~text
message_end
agent_end
agent_settled
~~~

它们不等价。

- message_end：某条 message 完成；
- agent_end：一次 low-level agent run 结束；
- agent_settled：自动 retry、recovery、queued work 等都不会再继续。

所以 HMBuddy T4 不能看到第一条 assistant message 就算成功。

---

# 12. 把 HMBuddy VNext-01 的完整链连起来

用户：

> “读取 sample.docx，告诉我项目编号、负责人、Runtime。”

## A. Host

createAgentSession() 创建 Pi session。

## B. Extension

pi.registerTool(read_office_file)。

## C. Prompt

session.prompt(user text)。

## D. First model request

模型看到用户目标和 read_office_file declaration。

## E. Model decision

模型产生 toolCall：

~~~text
read_office_file(path=...)
~~~

这是模型决定，不是 runner 的 if/else。

## F. Pi AgentLoop

loop 识别 toolCall 并执行。

## G. HMBuddy Tool

~~~text
office.ts
→ TS OfficeBridge
→ Python subprocess
→ DOCX reader
→ structured result
~~~

## H. Observation

Tool Result 进入 current context。

## I. Second model request

模型现在看到文件事实。

## J. Final

模型不再产生 Tool Call，返回最终回答；无更多 queued work 后 run settled。

---

# 13. 如果没有 Pi，HMBuddy 至少要自己长期维护什么

~~~text
model runtime
tool schema / validation
tool execution
agent loop
tool result injection
event lifecycle
session state
queue
retry
compaction
extensions
resource loading
provider differences
~~~

而 HMBuddy 真正有差异化价值的部分是：

~~~text
DOCX / XLSX / PPTX / PDF
OCR
Office / WPS COM
Artifact / Patch / Diff / Validation
Banking Skills
Governance
Internal integration
~~~

所以 V1.0 不是“为了少写代码”，而是在重新划分长期所有权。

---

# 14. Mental Model

~~~text
AgentSession
= 一段 Pi Agent 工作会话的运行边界

Agent / AgentLoop
= 模型基于 Observation 继续决定下一 Action 的控制循环

Extension Tool
= Pi 正式提供给模型的可执行动作

Tool Result
= 动作产生的 Observation，进入后续模型决策

HMBuddy Office Runtime
= Tool 背后的领域执行能力，不拥有 Agent 控制流
~~~

最重要的一句：

> **HMBuddy 不需要自己实现 AgentLoop；它需要知道 Pi 在什么 public seam 上允许自己注入 Office action。**

---

# 15. 读完后应能回答

1. 为什么“宿主先读文件再塞 Prompt”不能证明 Agent？
2. AgentSession 和底层 Agent 为什么不是一个概念？
3. 模型如何知道 read_office_file 存在？
4. 模型返回 toolCall 后，真正执行动作的是谁？
5. Tool Result 为什么要重新进入模型上下文？
6. Pi loop 为什么会自动再发一次模型请求？
7. Extension 和 Office Runtime 的 ownership 分别是什么？
8. 为什么 HMBuddy 不再需要自研 ToolRegistry / AgentLoop？
9. content 和 structuredContent 分别服务谁？
10. 为什么 T4 必须观察真正 Tool Call，而不能只检查最终答案？

如果只能靠术语回答，而不能沿真实调用链解释，Deep Read 还没有完成。
