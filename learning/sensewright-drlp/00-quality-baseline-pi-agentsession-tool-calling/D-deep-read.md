# D — Deep Read：Pi AgentSession / Tool Calling Vertical Slice

> **目标读者：** 会基本编程、知道 LLM 和 API，但没读过 Pi，也不了解 HMBuddy V1.0。  
> **Source pin：** `earendil-works/pi@4c6fb7cfe8c538a668726f6f8b3554098c39faee`  
> **Pi package：** `@earendil-works/pi-coding-agent@1.0.0`  
> **阅读目标：** 不背类名。从“一个聊天模型怎样变成真正会行动的 Agent”开始，一层层追问，直到 Tool、AgentLoop、AgentSession、SessionManager、Queue、Compaction、Retry、Extension lifecycle 都有自然的出场理由；同时把每个关键机制讲到足以支持需求判断和实现设计的粒度。

---

# 0. 先看最原始的矛盾：会回答，不等于会做事

用户对 HMBuddy 说：

> “读取 `sample.docx`，告诉我项目编号、负责人和 Runtime。”

如果我们只想把这个功能做出来，一个普通聊天程序完全可以这样写：

```text
宿主程序
→ 自己判断用户要读文件
→ 自己读取 sample.docx
→ 把文件内容拼进 Prompt
→ 调模型
→ 模型生成答案
```

它能工作。

但这里真正拥有控制权的是宿主程序。

是宿主程序决定：

- 什么时候读文件；
- 读哪个文件；
- 用什么函数读；
- 读完以后是否还要做别的动作。

模型只负责处理已经送到眼前的信息。

所以第一个问题不是“Pi 的 AgentSession 怎么写”，而是：

> **怎样让模型自己决定下一步要采取什么动作，而不是宿主把流程预先写死？**

这一步如果没有解决，后面所有“Agent”设计都只是普通应用在调用 LLM。

---

# 1. 第一个解决方案：把动作声明给模型

最直接的思路是：既然模型不知道自己能做什么，就把可用动作告诉它。

在 HMBuddy 中，我们希望它至少知道一个动作：

```text
read_office_file(path)
```

Pi 把这种动作抽象为 Tool。

在 Extension contract 中，一个 `ToolDefinition` 至少包含：

```text
name
label
description
parameters
execute()
```

从需求角度看，这几项承担的是不同职责：

- `name`：模型调用时使用的稳定动作标识；
- `label`：主要服务 UI 和人类展示；
- `description`：告诉模型这个动作做什么、什么时候适用；
- `parameters`：定义模型必须提供什么参数；
- `execute()`：runtime 真正执行动作时进入的实现。

这里第一次出现一个非常重要的分界：

```text
Tool declaration
≠
Tool implementation
```

模型拿到 declaration，只知道：

> “我可以调用 `read_office_file`，而且需要给 `path`。”

它并不会直接执行 Python，也不会自己访问文件系统。

这解决了第一个问题：

> 模型终于拥有了一个可以选择的 Action。

但马上暴露出第二个问题：

> **模型即使输出了 `read_office_file(path=...)`，那也只是一段结构化意图。谁来验证它、找到实现并真的执行？**

这就逼出了 runtime。

---

# 2. Tool Call 不是执行：为什么需要受控执行边界

模型第一次响应时，可能不返回普通文本，而返回一个结构化 Tool Call：

```json
{
  "name": "read_office_file",
  "arguments": {
    "path": "evals/fixtures/vnext/sample.docx"
  }
}
```

这个对象本质上只是：

> **Action Intent：模型希望系统执行什么。**

Pi 不能看到这个对象就直接“相信并执行”。

真实的 Agent loop 在执行前至少要解决四类问题：

1. 这个 Tool 当前是否存在；
2. 参数是否符合 schema；
3. policy / hook 是否允许执行；
4. 如果执行，怎样把成功或失败统一变成后续可消费的结果。

这部分核心代码在：

```text
packages/agent/src/agent-loop.ts
```

其中 `prepareToolCall()` 的职责很清楚。

它先根据 `toolCall.name` 从当前可执行 Tool 集合中查找 Tool。

如果不存在，不会让整个 Agent 崩掉，而是形成一个 Tool error result：

```text
Tool <name> not found
```

如果存在，会继续做：

```text
prepareArguments
→ validateToolArguments
→ beforeToolCall hook
```

因此 runtime 在真正执行前已经建立了一条受控边界。

### 2.1 参数校验解决什么

模型输出的是概率生成结果。

即使 Tool 名称正确，也可能：

- 少字段；
- 字段类型错误；
- 参数格式错误；
- provider 返回兼容性不佳的旧格式。

所以 Pi 先把模型意图转成满足 Tool schema 的参数。

如果参数不合法，结果被编码成 Tool error，而不是让业务实现收到一份未知结构。

这让 Tool 实现可以建立一个重要假设：

> **进入 `execute()` 的参数已经通过 Pi 的结构校验。**

### 2.2 `beforeToolCall` 解决什么

参数合法仍然不代表动作应该被允许。

例如未来 HMBuddy 有：

```text
delete_file
send_email
write_core_banking_data
```

模型可能“正确”地产生参数，但银行策略仍要求：

- 人工确认；
- 权限检查；
- 路径限制；
- 数据分级检查。

`beforeToolCall` 的作用就是在：

```text
参数已解析
↓
真正 execute 之前
```

给 runtime policy 一个阻断点。

它可以返回：

```text
block = true
reason = ...
terminate = true/false
```

所以：

```text
模型决定“想做什么”
≠
系统承诺“允许做什么”
```

这对 HMBuddy 非常关键。

银行治理必须尽量放在 deterministic execution boundary，而不是只靠 Prompt 里写一句“请谨慎”。

### 2.3 `prepareToolCall()` 最终产出什么

最终只有两类结果：

```text
immediate
```

表示不需要真正执行 Tool，已经有结果，例如：

- Tool 不存在；
- 参数不合法；
- 被 policy block；
- 已 abort。

或者：

```text
prepared
```

表示：

- Tool 已找到；
- 参数合法；
- policy 允许；
- 可以进入真正执行。

到这里，第二个问题解决了：

> Tool Call 被 runtime 转成受控执行。

但新的问题又出现：

> **Tool 执行完以后，结果究竟是什么？它是不是已经等于用户答案？**

---

# 3. Tool Result 为什么不能直接当最终答案

假设 `read_office_file` 最终读到：

```text
项目编号：HM-VNEXT-001
负责人：林海
Runtime：Pi + Python
```

最简单的做法似乎是：

```text
Tool Result
→ 直接显示给用户
→ 结束
```

但这在更真实的任务里会立刻失败。

用户可能说：

> “读取这份项目说明，告诉我负责人、Runtime，并判断当前技术路线是否和项目目标一致。”

文件读取只给出了事实。

它并没有完成“判断技术路线是否一致”这个更高层目标。

所以 Tool 的职责不是替 Agent 完成整个用户任务。

Tool 只负责：

> **执行一个具体动作，并产生新的事实或状态。**

因此 Tool Result 在 Agent 里更适合被理解为：

> **Observation。**

模型之前拥有：

```text
用户目标
+
已有上下文
```

Tool 执行后，多了：

```text
刚才动作的真实结果
```

只有把这个结果重新放回模型的决策上下文，模型才能决定：

- 信息已经够了，直接回答；
- 还缺一个文件；
- 还要再搜索；
- Tool 失败，需要换方案；
- 需要向用户追问。

这就是为什么 `agent-loop.ts` 不把 Tool Result 当作最终回答。

Tool 执行结束后，Pi 会创建 `ToolResultMessage`，并把它加入：

```text
currentContext.messages
```

到这里又产生第三个问题：

> **Observation 已经回到 Context 了，谁来保证模型真的再跑一轮，而不是整个函数结束？**

这才真正需要 AgentLoop。

---

# 4. AgentLoop：把一次调用变成“看结果再决定”的循环

现在我们已经有：

```text
用户目标
→ 模型产生 Action
→ runtime 执行
→ 得到 Observation
```

还差最后一环：

```text
Observation
→ 再次 Decision
```

Pi 的 `runLoop()` 就在解决这个问题。

一轮 assistant response 完成后，Pi 会从 `message.content` 中筛出：

```text
type = toolCall
```

如果找到 Tool Call：

```text
executeToolCalls(...)
→ 得到 ToolResultMessage[]
→ 写回 currentContext.messages
→ hasMoreToolCalls = true
```

`hasMoreToolCalls` 很关键。

它不是一个普通统计变量，而是在回答：

> **当前 assistant turn 产生了 Action，Action 已经形成 Observation，是否还应该让模型看到 Observation 并继续？**

只要 Tool batch 没有整体要求 terminate，内层 loop 就继续下一轮 provider request。

于是：

```text
第一次模型请求
看到：用户目标

第一次模型响应
产生：Tool Call

Tool execution
产生：Observation

第二次模型请求
看到：用户目标 + Tool Call + Tool Result
```

这时 Agent 才真正拥有：

```text
Decide
→ Act
→ Observe
→ Decide again
```

如果第二次模型又调用 Tool，循环继续。

如果第二次模型只返回文本，而且没有 steering / follow-up / explicit continuation，loop 才自然结束。

---

## 4.1 Tool batch 为什么还有 sequential / parallel

一个 assistant message 可以一次产生多个 Tool Call。

Pi 不假设所有 Tool 都必须串行执行。

`executeToolCalls()` 会同时看：

- 全局 `toolExecution` 配置；
- 每个 Tool 的 `executionMode`。

如果当前 batch 中任意 Tool 明确要求 sequential，则整批串行。

否则可以并行执行。

但即使并行，最终写入 `ToolResultMessage` 时仍保持 assistant source order。

这解决的是：

> **执行完成顺序可以不同，但对话记录与模型后续看到的逻辑顺序必须稳定。**

HMBuddy VNext-01 只有一个 `read_office_file`，现在不需要利用并行能力。

但理解这个机制可以看出：Pi 的 AgentLoop 已经不只是一个演示性质的 `while(toolCall)`，而是一套正式 Tool runtime。

---

## 4.2 Tool 失败为什么通常也会回模型

很多 Tool 失败不会直接让整个 Agent 异常退出，而是被包装成：

```text
isError = true
Tool Result
```

例如：

- Tool 不存在；
- 参数校验失败；
- `beforeToolCall` 阻断；
- Tool execute 抛错。

这样做的结果是：

> **失败本身也可以成为 Observation。**

模型可能看到：

```text
PATH_NOT_ALLOWED
```

然后决定：

- 换合法路径；
- 告诉用户没有权限；
- 请求用户重新选择文件。

这比“Tool 一失败整个 Agent 崩掉”更适合自主决策。

当然，HMBuddy 是否允许自动重试某类敏感动作，是更上层的 policy 问题。

---

# 5. 到这里已经有 AgentLoop，为什么还不够

如果用户只问一次：

> “读 `sample.docx`，告诉我负责人。”

AgentLoop 已经足够解释这一轮工作。

但办公 Agent 不会只活一轮。

用户很可能接着说：

> “再把刚才报告里的现金流部分展开。”

或者 Agent 正在执行时，用户突然输入：

> “先别看利润表了，重点看负债。”

再运行几十轮后，Context 可能塞不下。

Provider 也可能中途失败。

此时出现一个更大的问题：

> **一次 Decide → Act → Observe 循环，怎样组成一段长期、可继续、可恢复、可打断、可压缩的工作会话？**

这就是：

```text
一次 AgentLoop
≠
一段工作 Session
```

AgentSession 不是为了给 AgentLoop 换一个更高级的名字，而是为了解决 AgentLoop 外围的长期工作问题。

---

# 6. AgentSession：把“一次 run”提升为“一段工作会话”

Pi 的 `AgentSession` 位于：

```text
packages/coding-agent/src/core/agent-session.ts
```

它持有的关键对象包括：

```text
Agent
SessionManager
SettingsManager
ModelRuntime
ResourceLoader
Extension runtime
```

可以把它理解为：

> **围绕底层 Agent run 的会话协调层。**

它不重新实现 Tool Calling loop。

它解决的是 loop 外围那些真实产品一定会遇到的问题：

```text
历史以谁为准？
用户中途又输入怎么办？
上下文太长怎么办？
Provider 失败怎么办？
产品如何扩展 runtime？
什么时候才算真的结束？
```

这些问题必须逐个拆开。

---

# 7. SessionManager：历史不是一个 `messages[]` 就够了

最初做 Demo 时，保存对话似乎只需要：

```text
messages.push(...)
```

但持续工作后，历史不只包含普通对话。

Pi Session 里还可能存在：

- user / assistant / toolResult message；
- model change；
- thinking level change；
- usage；
- compaction；
- branch summary；
- extension custom entry；
- context edit；
- session metadata。

更麻烦的是，Session 不是永远只有一条直线历史。

Pi 的 `SessionManager` 把会话保存为：

> **append-only tree。**

每个 `SessionEntry` 都有：

```text
id
parentId
timestamp
```

当前的 `leafId` 表示：

> 当前工作路径走到了树上的哪个叶子。

当用户从更早的历史节点分支时，不需要篡改旧历史，只要移动 leaf，再从那里继续 append。

所以 SessionManager 解决的第一个问题是：

> **如何在不修改历史的前提下，表示当前有效分支。**

---

## 7.1 `getBranch()`：当前工作路径到底是哪一条

`getBranch()` 从当前 leaf 沿 `parentId` 一直回溯到 root，再反转顺序。

它得到的是：

> 当前 leaf 所在的那一条 Session 路径。

这和“读取整个 JSONL 文件”完全不同。

JSONL 里可以有多个分支。

真正与当前工作有关的是 current branch。

没有这个概念，Resume 或 Branch 后模型可能拿到并不属于当前路径的历史。

---

## 7.2 `buildSessionProjection()` / `buildSessionContext()`：模型下一轮到底应该看到什么

即使拿到了 current branch，也不能简单：

```text
branch 中所有 entry
→ 全部发给模型
```

因为有些 entry 只是状态信息：

- usage；
- label；
- session_info；
- custom state。

有些则改变上下文语义：

- compaction；
- context_edit；
- custom_message。

因此 SessionManager 提供：

```text
buildSessionProjection()
buildSessionContext()
```

`buildSessionProjection()` 负责把当前 append-only session tree 投影成：

```text
messages
thinkingLevel
model
```

`buildSessionContext()` 再把这个投影收敛成模型运行真正需要的 `SessionContext`。

所以 SessionManager 的权威性体现在：

> **磁盘上记录了什么，不等于模型下一轮应该看到什么；SessionManager 负责把历史事实投影成 canonical model context。**

这就是为什么 HMBuddy 不应再自己维护一份独立 `HMBuddySessionStore`。

否则会出现两个真相源：

```text
HMBuddy history
vs
Pi SessionManager projection
```

然后无法保证模型、UI、Resume、Compaction 对同一段工作有一致理解。

---

## 7.3 append-only 的意义：为什么不直接修改旧 message

SessionManager 的很多操作不是原地 edit，而是 append 新 entry。

例如 Context Edit 也是新增一条：

```text
context_edit
```

去表达“旧 entry 对模型 Context 的贡献发生变化”。

Compaction 也是新增一条 `compaction` entry。

这样做的价值是：

- 历史可追踪；
- 分支不会被破坏；
- Resume 时可以重建；
- Compaction / Extension state 有明确时间位置。

从当前实现可以推断，Pi 更倾向把 Session 当作：

> **可重放的工作历史，而不是一个不断被覆盖的 mutable messages array。**

---

## 7.4 `SessionManager.inMemory()` 到底改变了什么

VNext-01 用：

```text
SessionManager.inMemory()
```

它创建同样的 SessionManager，只是：

```text
persist = false
```

不写 session file。

这只是为了 Spike 减少变量。

它不意味着 Session 逻辑不存在。

branch、entry、projection、context authority 仍然由 SessionManager 提供。

也就是说：

```text
inMemory
改变的是 persistence
不是 ownership
```

---

# 8. Queue：Agent 正在工作时，用户又说话怎么办

现在 Session 可以持续了，但马上出现交互问题。

假设 Agent 正在：

```text
读取报告
→ Tool Call
→ 等 Tool Result
→ 准备下一次模型请求
```

这时用户输入：

> “先重点看现金流，不要继续原来的方向。”

系统有三个粗糙选择：

1. 禁止用户输入；
2. 立刻粗暴终止当前 run；
3. 把新消息简单塞进 history，至于模型什么时候看到不确定。

Pi 选择显式区分两种语义：

```text
steer
followUp
```

它们不是两个同义 API。

---

## 8.1 `steer`：改变仍在进行中的工作方向

`AgentSession.steer()` 的源码注释明确说明：

> 当前 Agent 运行中加入 steering message；它会在当前 assistant turn 的 Tool Call 执行完成后、下一次 LLM Call 之前被送入。

内部过程是：

```text
steer(text)
→ _queueUserInput(..., "steer")
→ input handler / skill / template 处理
→ _queueSteer()
→ _steeringMessages.push(text)
→ emit queue_update
→ agent.steer(UserMessage)
```

它维护两层状态。

**AgentSession 层**

保存 `_steeringMessages`，用于 UI / Session 状态展示。

**底层 Agent 层**

真正把 UserMessage 放入 steering queue，供 AgentLoop 在合适时点消费。

所以 `steer` 解决的是：

> **当前工作还没有结束，但用户希望下一轮决策立即考虑新方向。**

它不会在 Tool 正执行到一半时把一条文本强塞进已经发出的 provider request。

而是在清晰的 turn boundary 进入。

---

## 8.2 `followUp`：当前任务先自然结束，再继续处理

`followUp` 的语义不同。

它的源码注释明确说明：

> 只有当 Agent 已经没有更多 Tool Call 或 steering message 时，才处理 follow-up。

内部同样经过：

```text
followUp(text)
→ _queueFollowUp()
→ _followUpMessages.push(text)
→ queue_update
→ agent.followUp(UserMessage)
```

AgentLoop 的外层循环在自然要结束时，会再检查：

```text
getFollowUpMessages()
```

如果有 Follow-up：

```text
原本准备结束
→ 取出 follow-up
→ 再进入 inner loop
→ 形成新的 turn
```

所以：

```text
steer
= 修改当前进行中的工作方向

followUp
= 当前工作完成后追加下一项要求
```

没有这一区分，交互语义会很混乱：

- “先别做这个”可能要等当前工作完全结束才生效；
- “做完以后再总结”又可能错误打断当前 Tool。

---

## 8.3 `queue_update`：为什么 Queue 还需要事件

AgentSession 内部维护：

```text
_steeringMessages
_followUpMessages
```

每次变化会 emit：

```text
queue_update
```

事件携带当前完整：

```text
steering
followUp
```

队列。

这解决 UI / Host 的可观察性问题：

> runtime 知道消息已排队，还必须让产品层知道“现在还有多少用户输入待处理”。

这就是一个机制从内部状态走向产品体验的完整链。

---

# 9. Compaction：Session 能持续，不等于 Context 能无限增长

现在多轮工作和 Queue 都解决了。

新的问题迟早出现：

```text
Session 越来越长
↓
messages / Tool Result 越来越多
↓
模型 Context Window 有上限
```

最粗暴的办法是删旧消息。

但旧消息里可能包含：

- 用户长期目标；
- 之前确定的约束；
- 文件事实；
- 已完成的判断；
- Tool 调用结果。

随便删会让 Agent 失忆。

所以 Pi 需要 Compaction。

---

## 9.1 Compaction 解决什么

SessionManager 的 `CompactionEntry` 会记录：

```text
summary
firstKeptEntryId
tokensBefore
systemMessage
details / usage
```

它表达的是：

> 某一段较老的 Session 历史不再逐条进入模型 Context，而由一个 summary 代表；从 `firstKeptEntryId` 往后的内容继续保留。

这使：

```text
长期 Session 历史
```

和：

```text
当前模型能装下的 Context
```

不必是同一个东西。

---

## 9.2 为什么 Compaction 属于 Session，而不是 AgentLoop

AgentLoop 只关心：

> 下一轮拿到什么 `currentContext`。

至于 currentContext 为什么比原始历史短、哪些旧消息已经被 summary 替代，不应该由 Tool Calling loop 自己决定。

Session 层可以在 turn 之间做 compaction，然后通过 SessionManager 的 projection 生成新的 canonical context，再交给底层 Agent。

所以职责边界是：

```text
Session
负责“下一轮应该看到什么历史”

AgentLoop
负责“拿到这份 Context 后怎样继续 Decide / Act / Observe”
```

---

## 9.3 Compaction 什么时候触发

Pi 的 Session event 明确区分：

```text
compaction_start
reason:
  manual
  threshold
  overflow
```

也就是说至少存在三类触发。

**manual**

用户或上层显式要求压缩。

**threshold**

当前 Context 使用量达到自动压缩阈值。

**overflow**

Provider 已经因为上下文过长发生失败，需要先压缩再恢复。

所以 Compaction 既是长期 Session 管理，也是 runtime recovery 的一部分。

---

## 9.4 为什么 Compaction 不能只修改一个 `messages[]`

SessionManager 使用 append-only entries。

Compaction 自己也是新 entry。

这样 Resume 时不是“只看到压缩后的结果，却不知道之前发生过什么”，而是可以知道：

- 原始历史仍然存在；
- 哪个时间点发生了压缩；
- summary 是什么；
- 从哪个 entry 开始保留明细；
- 当时系统提示与上下文状态是什么。

这让：

```text
Work History
```

和：

```text
Current Model Context
```

彻底解耦。

这也是 SessionManager 不只是 history storage 的关键证据。

---

# 10. Retry / Recovery：一次请求失败，不等于整段工作结束

Agent 已经能长时间运行，但 Provider 请求不可能永远成功。

可能出现：

- 临时网络错误；
- Rate limit；
- Provider transient error；
- Context overflow；
- Summary / Compaction 自己的失败。

如果底层每次错误都直接告诉产品：

> Agent 完成了。

那用户会遇到大量“任务突然死掉”。

所以 AgentSession 还承担自动 Retry / Recovery。

它内部维护例如：

```text
_retryAbortController
_retryAttempt
_failedResponse
```

并暴露：

```text
auto_retry_start
auto_retry_end
```

等事件。

---

## 10.1 为什么 `agent_end` 不是“任务彻底结束”

低层 AgentLoop 在一次 run 结束时发：

```text
agent_end
```

但 Session 层收到后，仍可能判断：

- 是否需要 auto retry；
- 是否因为 overflow 需要 compaction；
- 是否还有 queued work；
- extension 是否请求 continuation。

因此：

```text
agent_end
= 某一次 low-level run 结束

agent_settled
= Pi 已确定不会再自动继续
```

这是一个非常重要的生命周期边界。

Host 如果在 `agent_end` 时就：

```text
退出进程
关闭 UI busy 状态
判定任务完成
```

可能会过早结束。

SDK / UI 真正需要“完全空闲”语义时，应等：

```text
agent_settled
```

---

## 10.2 Retry 改变了什么状态

Retry 并不是重新创建一条新 Session。

AgentSession 会记住 failed response，并在 recovery 时继续同一段工作。

因此用户工作仍然属于同一 Session。

这就是为什么 Retry 属于 Session orchestration，而不是 HMBuddy runner 里的：

```text
try prompt()
catch 再 prompt()
```

宿主盲目重放用户 Prompt，可能重复 Tool action。

未来如果 Tool 有写文件、副作用或外发动作，这会直接制造重复执行风险。

所以必须区分：

```text
Pi Provider Retry
≠
HMBuddy Office Tool Retry
```

前者是模型 / Session runtime 的恢复机制。

后者是领域动作是否安全重试的问题。

VNext-01 的 Python Bridge timeout 第一版不自动 retry，就是因为这两层不能混淆。

---

# 11. Extension lifecycle：怎样加 HMBuddy 能力，而不去改 AgentLoop

到现在还有最后一个架构问题。

HMBuddy 想增加：

```text
read_office_file
银行权限
审计
敏感操作确认
内部系统连接
```

最坏的做法是每新增一种产品能力，就修改：

```text
agent-loop.ts
agent-session.ts
```

这样 Pi 就失去了上游 runtime 的意义，HMBuddy 最终会变成长 fork。

Pi 提供 Extension runtime，正是为了避免这种耦合。

---

## 11.1 `registerTool()`：把领域动作接入 Pi 的正式 seam

HMBuddy Extension 通过：

```text
pi.registerTool(...)
```

注册 Office Tool。

`ToolDefinition` 不只是一个 function pointer。

它同时定义：

- model-facing name / description；
- parameters schema；
- outputSchema；
- exposure；
- defaultActive；
- executionMode；
- annotations；
- execute()。

因此 Extension Tool 是一个完整 action contract。

对于 HMBuddy `read_office_file`，可以对应：

```text
parameters
→ { path: string }

annotations.readOnlyHint
→ true

outputSchema
→ OfficeReadResult schema

execute()
→ 调 TS Office Bridge
```

---

## 11.2 registered、active、callable 为什么要区分

Pi 当前 Tool model 明确区分：

```text
registered
active / declared
callable
```

并定义 exposure：

```text
direct
model-only
codemode
deferred
hidden
```

对于 `direct` Tool：

> 默认注册后 active，声明给模型，也可以被正常执行。

但不能把：

```text
registerTool()
```

普遍等同于：

> 模型一定看见这个 Tool。

因为：

- `codemode` Tool 可能只供其他 Tool 调；
- `deferred` Tool 可能等待 tool search；
- `hidden` Tool 即使注册也不可达；
- `defaultActive=false` 也可能暂时不声明。

这对未来 HMBuddy 动态权限很重要：

> Tool implementation 可以存在，但不代表当前用户 / 当前任务必须看到。

---

## 11.3 `bindExtensions()`：为什么创建 Session 后还要绑定

SDK 创建 AgentSession 后，Extension runtime 还要与具体 Session lifecycle 绑定。

`session.bindExtensions()` 会把：

- UI context；
- mode；
- command actions；
- abort handler；
- shutdown handler；

等 bindings 注入 Extension runtime，并触发 Session 生命周期。

官方 SDK 示例中，MCP Extension 会在：

```text
session_start
```

去连接 MCP servers。

所以 Extension 不是“启动时 import 一次就结束”。

它是跟随 Session 生命周期运行的。

对于 HMBuddy，以后审计、权限、Office Tool、UI 状态都可以通过这个正式 seam 进入。

---

## 11.4 Extension lifecycle 解决的真正问题

它让 HMBuddy 可以做到：

```text
Pi Agent runtime
      ↑
Extension seam
      ↓
HMBuddy Office / Banking capability
```

而不是：

```text
HMBuddy 修改 Pi internal AgentLoop
```

这就是 Architecture V1.0 的关键所有权边界。

---

# 12. `createAgentSession()` 为什么现在才应该出场

到这里，我们已经一步步被问题逼出了：

```text
Tool declaration
Tool execution boundary
AgentLoop
SessionManager
Queue
Compaction
Retry
Extension lifecycle
```

现在才适合看：

```text
createAgentSession()
```

它位于：

```text
packages/coding-agent/src/core/sdk.ts
```

它的意义不再是“一个创建对象的方法”。

它是 Composition Root：

> **把前面已经理解的各个 runtime responsibility 组装成一段可工作的 AgentSession。**

---

## 12.1 第一步：确定运行范围与配置来源

`createAgentSession()` 先解析：

```text
cwd
agentDir
```

然后准备：

```text
ModelRuntime
SettingsManager
SessionManager
ResourceLoader
```

如果调用者没有传 `ResourceLoader`，Pi 创建 `DefaultResourceLoader` 并 `reload()`。

这一步解决：

> 模型、配置、Session、扩展资源从哪里来。

---

## 12.2 第二步：恢复既有 Session 状态

SessionManager 会先：

```text
buildSessionContext()
```

得到：

```text
messages
thinkingLevel
model
```

如果已有 Session，Pi 会尝试恢复：

- 之前使用的 model；
- thinking level；
- 历史 messages。

这就是为什么 `createAgentSession()` 不是单纯“new Agent”。

它必须先把一段可能已经存在的工作恢复成 runtime state。

---

## 12.3 第三步：确定模型与 Tool loadout

如果 Session 没有可恢复的 model，Pi 会根据：

- explicit model；
- settings default；
- provider defaults；

寻找初始模型。

随后计算：

```text
allowed tools
excluded tools
initial active tools
```

这决定：

> 第一轮模型到底能看到哪些 Action。

---

## 12.4 第四步：创建底层 Agent

底层 Agent 得到：

- model；
- systemPrompt；
- tools；
- existing messages；
- stream function；
- context transform；
- steering / follow-up hooks；
- retry / turn lifecycle hooks。

这说明：

> AgentLoop 不是孤立对象，它运行所需的上下文和控制钩子都来自 Session 组装。

---

## 12.5 第五步：再把 Agent 包装为 AgentSession

最后 Pi 创建 AgentSession，把：

```text
Agent
SessionManager
SettingsManager
ResourceLoader
ModelRuntime
Extension runtime reference
Tool policy
```

组合在一起。

所以：

```text
前面回答：
为什么需要这些部件

createAgentSession() 回答：
如何把这些部件装成一次真实 Session
```

这就是为什么它应该在文章后半段出现，而不是一开头就讲。

---

# 13. 回到 HMBuddy：我们究竟应该插在哪里

现在再看 VNext-01，边界已经非常清楚。

Pi 已经拥有：

```text
Model request
Tool declaration
Tool argument validation
Tool execution lifecycle
Tool Result reinjection
AgentLoop
Session history projection
Queue
Compaction
Retry / recovery
Extension lifecycle
settled semantics
```

HMBuddy 不应该再写这些通用层。

它真正需要做的是：

```text
read_office_file.execute()
        ↓
TypeScript Office Bridge
        ↓
Python subprocess
        ↓
DOCX reader
        ↓
OfficeReadResult
```

完整链因此是：

```text
用户目标
↓
AgentSession.prompt()
↓
模型看到 active read_office_file
↓
模型产生 Tool Call
↓
Pi prepareToolCall / validation / hook
↓
Pi 调 execute()
↓
HMBuddy TS Bridge
↓
Python 读取 DOCX
↓
Tool Result / Observation
↓
Pi 写回 Context
↓
AgentLoop 再请求模型
↓
最终回答
↓
AgentSession 处理可能的 retry / queue / compaction
↓
agent_settled
```

此时：

> **Pi 会 Agent；HMBuddy 会银行办公**

不再是架构 slogan。

它是这条因果链推导出来的工程所有权结论。

---

# 14. 一张“机制职责表”检查有没有讲漏

| 机制 | 解决的问题 | 主要输入 | 维护 / 改变的状态 | 主要输出 | 不负责什么 |
|---|---|---|---|---|---|
| ToolDefinition | 模型怎样知道可用动作 | Tool contract | Tool registry / loadout metadata | model-facing declaration + execute contract | 不决定何时调用 |
| prepareToolCall | Action intent 能否安全执行 | toolCall + tools + hooks | 无长期 Session 状态 | prepared call 或 error result | 不负责业务解析 |
| AgentLoop | Observation 后怎样继续决策 | Context + Model + Tools | 当前 run 的 context / pending loop state | messages + agent events | 不负责长期 Session persistence |
| SessionManager | 历史如何形成 canonical context | append-only entries + leaf | tree / branch / entries / leaf | SessionProjection / SessionContext | 不执行模型 Tool |
| steer | 当前 run 如何改变方向 | 用户新输入 | steering queues | 下一次正常 LLM turn 的用户消息 | 不等当前 run 自然结束 |
| followUp | 当前工作结束后怎样追加工作 | 用户新输入 | follow-up queues | 自然结束后的新 turn | 不抢占当前工作 |
| Compaction | 长期历史装不进 Context 怎么办 | Session history / token pressure | compaction entry / projection | 压缩后的模型 Context | 不删除原始工作历史 |
| Retry / Recovery | 一次 provider failure 是否终结任务 | failed response / retry policy | retry attempt / failed response | 后续自动恢复 run | 不替 HMBuddy Tool 做业务级 retry |
| Extension lifecycle | 产品能力怎样接入 Pi | Extension factory / session bindings | extension runtime state | Tools / hooks / events / UI integration | 不重新拥有 AgentLoop |
| createAgentSession | 这些部件怎样组合 | cwd / model / settings / resources / session | 完整 Session runtime composition | AgentSession | 不承担 Office domain logic |

这张表不是正文替代品。

它只是检查：主线里出现的关键机制，是否都已经解释到足够深。

---

# 15. 几个容易混淆的边界

## AgentLoop vs AgentSession

```text
AgentLoop
= 一次 run 内，模型怎样 Action → Observation → 再 Decision

AgentSession
= 多次 run、历史、队列、压缩、恢复、扩展怎样组成一段持续工作
```

## AgentSession vs SessionManager

```text
AgentSession
= orchestration

SessionManager
= append-only session history + branch + canonical context projection
```

AgentSession 使用 SessionManager，但两者不是同义词。

## Tool Result vs Final Answer

```text
Tool Result
= Observation

Final Answer
= 模型基于目标 + Observation 形成的用户响应
```

## Pi Retry vs HMBuddy Tool Retry

```text
Pi Retry
= provider / session runtime recovery

HMBuddy Tool Retry
= Office capability 是否重试某个具体副作用动作
```

后者未来必须更谨慎，不能照搬前者。

## registered Tool vs active Tool

```text
registered
= runtime 知道这个 Tool 存在

active / declared
= 当前模型 request 可以看到这个 Tool

callable
= 其他 Tool 是否可以通过 ctx.executeTool() 调它
```

---

# 16. 用一个完整场景重新走一次

用户：

> “阅读 `sample.docx`。告诉我项目编号、负责人、Runtime。”

### 运行前

`SessionManager.inMemory()` 已存在。

ResourceLoader 已加载 HMBuddy Office Extension。

Extension 注册：

```text
read_office_file
```

它当前是 active direct Tool。

### 用户 Prompt

`AgentSession.prompt()`：

1. 处理 input handlers；
2. 展开 skill / prompt template；
3. 检查当前是否 streaming；
4. 检查 model / auth；
5. 构造 UserMessage；
6. 启动底层 Agent run。

### 第一次模型请求

Context 包含：

```text
用户目标
+
read_office_file declaration
```

### 模型决定

返回：

```text
toolCall(read_office_file, path=sample.docx)
```

### Pi 执行前

`prepareToolCall()`：

1. 找到 Tool；
2. 验证 path 参数；
3. 执行 `beforeToolCall`；
4. 得到 prepared call。

### HMBuddy 执行

`ToolDefinition.execute()`：

```text
TS Office Bridge
→ Python subprocess
→ DOCX parser
→ OfficeReadResult
```

### Pi 接回结果

形成 `ToolResultMessage`。

写入 `currentContext.messages`。

`hasMoreToolCalls = true`。

### 第二次模型请求

模型现在看到：

```text
原始用户目标
+
自己调用 read_office_file
+
文件内容 Observation
```

模型返回最终文本：

```text
项目编号……
负责人……
Runtime……
```

### 低层 run 结束

AgentLoop 发 `agent_end`。

### Session 层检查

AgentSession 还要判断：

- 是否需要 retry；
- 是否需要 overflow recovery / compaction；
- 是否还有 queued steering / follow-up；
- extension 是否还要求 continuation。

都没有后，才进入：

```text
agent_settled
```

到这里，一次完整的 Agent 工作才真正结束。

---

# 17. 如果用户中途插一句话，会发生什么

假设第一次 Tool 执行时用户输入：

> “顺便把项目目标也告诉我。”

如果产品把它作为 `steer`：

```text
AgentSession.steer()
→ steering queue
→ queue_update
→ 当前 assistant turn 的 Tool Call 执行完
→ 下一次 LLM request 前加入这条 UserMessage
```

于是第二次模型看到：

```text
原始目标
+
Tool Result
+
新的 steering 要求
```

它可以直接在当前工作里调整方向。

如果作为 `followUp`：

```text
当前 Agent 先完成原目标
→ 没有 Tool / steering 后
→ outer loop 发现 follow-up
→ 开始下一项用户要求
```

这就是为什么 Queue 不是“一个数组”这么简单。

它定义的是：

> **用户新输入在 Agent 时序中的语义。**

---

# 18. 如果 Context 太长，会发生什么

假设 Session 已运行很久。

下一轮 Context 接近上限。

AgentSession 可以触发 threshold compaction。

或者 Provider 已经因为 overflow 拒绝请求，再触发 overflow recovery。

Compaction 生成 summary，并在 SessionManager 中 append `CompactionEntry`。

下一次：

```text
buildSessionProjection()
```

不再机械投影全部旧消息，而是按 compaction boundary 生成当前模型可用的 messages。

原历史仍然存在于 Session tree。

模型 Context 被压缩。

这就是：

```text
Work History
≠
Current Model Context
```

也是 SessionManager 核心价值之一。

---

# 19. 如果 Provider 临时失败，会发生什么

低层 Agent run 可能结束并产生 error outcome。

但 AgentSession 不一定立刻 settled。

如果符合 retry policy：

```text
auto_retry_start
→ 等待 / recovery
→ 再次 run
→ auto_retry_end
```

所以 UI 不能把 `agent_end` 简单画成“任务完成”。

真正完整的空闲边界是：

```text
agent_settled
```

这一点也是 HMBuddy 以后 Desktop UI 必须尊重的 Pi lifecycle，而不是自己另造一套 Busy / Done 语义。

---

# 20. 最终 Mental Model

现在才压缩。

### Tool

不是函数列表。

它是：

> **模型 Action Space 与真实程序执行之间的 contract。**

### AgentLoop

不是“while 循环”这个语法概念。

它是：

> **Observation 能重新进入 Decision，从而让模型根据真实执行结果继续行动的控制机制。**

### SessionManager

不是聊天记录数据库。

它是：

> **append-only 工作历史、分支与模型 canonical context 之间的投影 authority。**

### AgentSession

不是 AgentLoop 的包装名。

它是：

> **把一次次 Agent run 组织成长期工作会话的 orchestration boundary，负责 Queue、Compaction、Retry、Extension lifecycle 等 session-level concern。**

### Extension

不是 HMBuddy 自建 PluginRuntime。

它是：

> **HMBuddy 把 Office / Banking capability 注入 Pi runtime 的正式 public seam。**

### `createAgentSession()`

不是“方便创建几个对象”的 helper。

它是：

> **Pi coding-agent runtime 的 composition root，把 Model、Session、Resource、Tool、Extension 和底层 Agent 组装成可工作的 Session。**

---

# 21. Deep Read Gate：读完以后你应该能做什么

读者现在不应该只会回答“AgentSession 有哪些模块”。

而应该能够解释：

1. 为什么普通“宿主读文件 + LLM”不等于 Agent；
2. 为什么 Tool declaration 和 Tool execution 必须分开；
3. Tool Call 在执行前经过哪些 validation / hook；
4. Tool failure 为什么也可以成为 Observation；
5. Tool Result 为什么必须重新进入 Context；
6. `hasMoreToolCalls` 为什么会触发下一轮模型请求；
7. AgentLoop 到底解决什么，又明确不解决什么；
8. 为什么长期工作需要 SessionManager，而不是 `messages[]`；
9. append-only tree、leaf、branch 与 `buildSessionContext()` 各自解决什么；
10. `inMemory()` 只改变 persistence，为什么不改变 Session authority；
11. `steer` 与 `followUp` 的时序语义为什么不同；
12. `queue_update` 对产品层有什么意义；
13. Compaction 为什么不是简单删历史；
14. `CompactionEntry` 怎样让 Work History 和 Model Context 解耦；
15. 一次 provider failure 为什么不等于工作结束；
16. `agent_end` 与 `agent_settled` 为什么必须区分；
17. Extension lifecycle 为什么能让 HMBuddy 不 fork Pi；
18. registered / active / callable Tool 为什么不是同一集合；
19. `createAgentSession()` 为什么应该在理解完这些机制后再读；
20. HMBuddy VNext-01 真正应该实现的边界在哪里。

如果这些问题中任何一类只能靠记住类名回答，而不能沿：

```text
问题
→ 机制
→ 输入
→ 状态变化
→ 输出
→ 新问题
```

解释，这篇 Deep Read 仍然没有通过 Quality Baseline。
