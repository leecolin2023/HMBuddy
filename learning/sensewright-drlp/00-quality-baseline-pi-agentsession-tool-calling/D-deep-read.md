# D — Deep Read：Pi AgentSession / Tool Calling Vertical Slice

> **目标读者：** 会基本编程、知道 LLM 和 API，但没读过 Pi，也不了解 HMBuddy V1.0。  
> **Source pin：** `earendil-works/pi@4c6fb7cfe8c538a668726f6f8b3554098c39faee`  
> **Pi package：** `@earendil-works/pi-coding-agent@1.0.0`  
> **阅读目标：** 不按源码目录讲 Pi。只沿一条问题链推进：每解决一个问题，再让下一个问题出现；每个关键机制都解释到足以支撑需求规格和实现判断的粒度。

---

# 0. 原始矛盾：会回答，不等于会做事

用户对 HMBuddy 说：

> “读取 `sample.docx`，告诉我项目编号、负责人和 Runtime。”

一个普通 LLM 应用完全可以实现这个功能：

```text
宿主程序判断用户要读文件
→ 宿主程序读取 sample.docx
→ 把内容拼进 Prompt
→ 调模型
→ 模型回答
```

结果可能完全正确。

但这里真正做决定的是宿主程序。

宿主程序提前决定了：

- 什么时候读文件；
- 读哪个文件；
- 调什么函数；
- 文件读完以后下一步是什么。

模型只是接收已经准备好的信息。

如果用户换成：

> “先看看这个项目目录里有哪些材料，再自己判断应该读哪一份，然后回答我风险点。”

宿主程序就必须继续预写：

```text
先 list
如果……
再 search
如果……
再 read
然后……
```

流程越开放，宿主里的 `if / else` 越多。

所以真正的问题不是“怎样让 LLM 回答文件问题”，而是：

> **怎样让模型自己选择下一步动作？**

这才是 Tool Calling 的起点。

---

# 1. 第一步：先让模型知道“它有哪些动作”

模型如果从来不知道系统有 `read_office_file`，就不可能主动选择它。

因此第一步不是执行，而是**声明动作**。

在 Pi 中，这个动作通过 `ToolDefinition` 描述。

从模型视角，最关键的是：

```text
name
description
parameters
```

例如：

```text
name:
read_office_file

description:
读取工作区中的 Office 文件并返回结构化内容

parameters:
{
  path: string
}
```

这三部分分别回答：

```text
动作叫什么？
↓
什么时候应该用？
↓
调用时必须给什么参数？
```

而 `execute()` 是这个动作在程序中的真正实现。

所以从一开始就要分清：

```text
Tool declaration
≠
Tool implementation
```

Tool declaration 是模型的 **Action Space**。

Tool implementation 是程序真正能执行的代码。

模型拿到 declaration 后，终于可以表达：

> “为了回答这个问题，我要调用 `read_office_file`。”

它可能输出：

```json
{
  "name": "read_office_file",
  "arguments": {
    "path": "evals/fixtures/vnext/sample.docx"
  }
}
```

到这里，第一个问题解决了：

> 模型已经能够自己选择动作。

但现在出现了一个非常具体的新问题：

> **模型只是“说它想调用”。这段 `name + arguments` 怎样真正变成一次函数执行？**

下一步只解决这个问题。

---

# 2. 从 Action Intent 到真实执行：先做一个最小执行器

先不要想 AgentLoop，也不要想 Session。

假设我们自己写最简单的执行器，逻辑大概是：

```text
收到 Tool Call
↓
根据 name 找到实现
↓
把 arguments 传进去
↓
调用函数
↓
拿到结果
```

例如：

```text
read_office_file
↓
找到 readOfficeFile 实现
↓
传入 path
↓
执行
```

这已经回答了“谁来执行”的最朴素版本：

> **模型只表达 Action Intent；程序中的 Tool execution layer 把 Intent 变成真实调用。**

在 Pi 当前实现里，这条执行路径位于：

```text
packages/agent/src/agent-loop.ts
```

但现在我们只关心“执行一次 Tool”，暂时不需要理解为什么文件名叫 `agent-loop.ts`。

因为仅仅“找到函数然后调用”还不够。

第一个马上会发生的故障是：

> **如果模型给了一个不存在的 Tool 名怎么办？**

---

## 2.1 Tool lookup：名字必须先解析成真实能力

假设模型输出：

```text
read_doc
```

但当前只有：

```text
read_office_file
```

程序不能直接：

```text
tools["read_doc"](...)
```

然后因为 `undefined` 崩掉。

Pi 的 Tool execution 路径会先根据：

```text
toolCall.name
```

从当前可执行 Tool 集合中查找。

找不到时，形成一个标准失败结果：

```text
Tool <name> not found
```

这里解决的是一个很基础但很重要的问题：

> **模型使用的是符号名称，程序执行的是具体实现，两者必须有确定的解析关系。**

所以一次 Tool execution 的第一道门是：

```text
Action name
→ Tool lookup
→ concrete implementation
```

现在 Tool 找到了。

新的问题自然出现：

> **名字找对了，模型给的参数就一定能用吗？**

---

## 2.2 Schema validation：模型输出是概率结果，参数不能直接信任

`read_office_file` 需要：

```json
{
  "path": "..."
}
```

但模型可能生成：

```json
{}
```

或者：

```json
{
  "path": 123
}
```

或者 provider 兼容层返回需要整理的旧格式。

如果这些参数直接进入 Office Runtime，错误会扩散到业务层。

因此 Pi 在真正执行 Tool 前，会先：

```text
prepareArguments
→ validateToolArguments
```

`prepareArguments` 可以处理兼容性整理。

`validateToolArguments` 则按照 Tool 的 schema 验证参数。

这使 Tool 实现可以依赖一个很重要的前提：

> **正常进入 `execute()` 的参数，已经通过 Tool contract 的结构校验。**

如果 validation 失败，Pi 不需要启动业务实现，而是直接得到一个 error Tool Result。

现在名字正确，参数也正确。

下一问是：

> **参数合法，是不是就代表这个动作一定允许执行？**

---

## 2.3 `beforeToolCall`：合法动作也可能没有权限做

假设以后 HMBuddy 有：

```text
delete_office_file
send_external_email
write_core_system
```

模型给出的 Tool 名和参数都可能完全正确。

但银行系统仍然可能要求：

- 当前用户有权限；
- 当前路径在允许范围；
- 敏感操作需要 ASK；
- 外发动作需要审批；
- 某类数据禁止进入开放网络。

所以：

```text
参数正确
≠
动作被授权
```

Pi 的 Tool execution 路径提供 `beforeToolCall` hook。

它发生在：

```text
Tool 已找到
↓
参数已校验
↓
真正 execute 之前
```

上层可以返回：

```text
block = true
reason = ...
terminate = true / false
```

于是 Tool execution 多了一道清楚的控制点：

```text
模型想做
↓
参数也对
↓
Policy 判断是否允许
↓
允许后才真正执行
```

这也是为什么银行治理不应该主要依赖 Prompt。

Prompt 可以影响模型行为。

但真正不能执行的动作，必须在程序边界阻断。

现在 Tool 找到了、参数合法、Policy 也允许。

终于可以执行。

但还有一个现实问题：

> **函数本身也可能失败。失败以后，系统怎样把它交给后续流程，而不是直接崩掉？**

---

## 2.4 执行失败也需要统一结果

Tool 实现可能：

- 文件不存在；
- Python subprocess 超时；
- 解析失败；
- 外部服务拒绝；
- execute 自己抛出异常。

如果每种失败都用不同异常一路冒泡，后面的系统很难继续做决定。

Pi 的 Tool execution 路径会把很多失败转成统一的 Tool Result，并带：

```text
isError = true
```

例如：

```text
PATH_NOT_ALLOWED
FILE_NOT_FOUND
Tool xxx not found
参数校验失败
```

到这里，一次 Tool Call 的最小执行闭环才真正完整：

```text
Tool Call
↓
lookup
↓
schema validation
↓
beforeToolCall policy
↓
execute
↓
统一 Tool Result
```

现在我们已经解决了第二个大问题：

> **模型的 Action Intent 怎样安全地变成一次真实程序动作。**

注意，到这里仍然不需要理解 AgentLoop。

因为我们现在只完成了：

> “一次动作怎样执行”。

新的问题是：

> **Tool Result 已经拿到了。是不是直接把它展示给用户，任务就结束了？**

---

# 3. Tool Result 不是答案：它只是模型新获得的事实

假设文件读取结果是：

```text
项目编号：HM-VNEXT-001
负责人：林海
Runtime：Pi + Python
```

如果用户只问：

> “负责人是谁？”

直接返回“林海”似乎没问题。

但用户可能问：

> “负责人是谁，并判断当前 Runtime 是否和项目目标一致。”

Tool 只完成了“读取”。

它并不知道：

- 用户最终想判断什么；
- 是否还需要第二份材料；
- 是否需要比较；
- 是否已经拥有足够证据。

因此 Tool Result 的职责不是“完成用户任务”。

它更像是：

> **模型刚刚采取一个动作后得到的 Observation。**

执行前模型知道：

```text
用户目标
+
旧上下文
```

执行后又知道：

```text
刚刚读到的文件事实
```

如果这些新事实不再交给模型，模型根本没有机会基于执行结果继续判断。

因此下一步必然是：

```text
Tool Result
→ 回到模型可见 Context
```

现在问题又推进了一层：

> **结果回到 Context 以后，谁负责真的再请求模型一次？**

到这里，AgentLoop 才第一次有必要出现。

---

# 4. AgentLoop：为什么 Observation 之后还要再 Decision

我们现在已经推导出：

```text
用户目标
↓
模型选择 Action
↓
程序执行 Action
↓
得到 Observation
```

但如果系统在这里停止，依然只是：

```text
LLM
→ function
→ end
```

真正的 Agent 需要：

```text
LLM
→ Action
→ Observation
→ LLM again
```

也就是：

> **模型必须能够根据刚刚发生的真实结果继续决策。**

这正是 Pi `runLoop()` 解决的问题。

---

## 4.1 一轮 assistant response 完成后，Pi 看什么

模型的 assistant message 可能包含：

```text
普通文本
thinking
toolCall
```

Pi 会筛出：

```text
type = toolCall
```

如果存在 Tool Call，就进入前面已经理解的 Tool execution 路径。

执行结束后，Pi 得到：

```text
ToolResultMessage[]
```

然后把这些 Result 加入：

```text
currentContext.messages
```

所以 Context 发生了真实变化：

执行前：

```text
User:
读取 sample.docx……
```

执行后：

```text
User:
读取 sample.docx……

Assistant:
toolCall(read_office_file)

Tool:
HM-VNEXT-001 / 林海 / Pi + Python
```

模型下一次看到的是一个已经包含 Observation 的世界。

---

## 4.2 `hasMoreToolCalls` 为什么重要

Pi 会根据 Tool batch 是否要求终止，设置：

```text
hasMoreToolCalls
```

只要刚才的 Action 仍允许继续，内层 loop 就再次请求模型。

因此：

```text
第一次模型请求
→ 决定要读文件

Tool 执行
→ 得到文件事实

第二次模型请求
→ 基于文件事实继续判断
```

这就是 AgentLoop 最核心的职责：

> **保证 Action 产生的新状态能够重新进入 Decision。**

---

## 4.3 如果第二轮模型还需要 Tool 呢

例如第一次读取后发现：

```text
文档只写了“详见附件二”
```

模型可以第二次再产生新的 Tool Call。

于是：

```text
Decision
→ Action
→ Observation
→ Decision
→ Action
→ Observation
→ …
```

直到某一轮模型不再产生 Tool Call。

---

## 4.4 多个 Tool Call 怎样执行

一个 assistant message 可能一次发出多个 Tool Call。

Pi 支持：

```text
sequential
parallel
```

Tool 可以通过 `executionMode` 要求顺序执行。

如果不存在 sequential 要求，多个调用可以并行。

但最终生成 ToolResultMessage 时仍保持 source order。

这里解决的是：

> **物理执行可以并发，但模型看到的 Tool Call / Tool Result 对应关系必须稳定。**

---

## 4.5 到什么条件，AgentLoop 才自然停止

当当前轮：

- 没有新的 Tool Call；
- 没有 steering message；
- 没有 follow-up；
- 没有显式 continuation；

loop 才有机会结束。

先暂时只记住：

> AgentLoop 负责一段 run 内的“继续还是停止”。

到这里，我们已经有一个真正会：

```text
看目标
→ 选择动作
→ 看结果
→ 再决定
```

的 Agent run。

但真实办公不是一次 run 就结束。

用户下一句很可能是：

> “刚才那份文件，再帮我看一下现金流。”

新的问题变成：

> **一次 AgentLoop 已经结束以后，上一轮工作怎样继续成为下一轮的上下文？**

这才进入 Session。

---

# 5. 一次 run 不等于一段工作：为什么需要 Session

一次 AgentLoop 有一个清楚的生命周期：

```text
开始
→ 多轮 Tool / Model 决策
→ 自然停止
```

但用户理解的“工作”可能持续很久：

```text
上午读报告
→ 下午继续追问
→ 改一次方向
→ 读另一份材料
→ 第二天重新打开
```

所以：

```text
一次 Agent run
≠
一段长期工作会话
```

现在新的问题是：

> **怎样把多次 run 组织成同一段可以继续的工作？**

最直觉的答案是：保存历史。

但“保存历史”很快又会暴露更具体的问题。

---

# 6. SessionManager：历史为什么不能只是一个 `messages[]`

最开始完全可以想象：

```text
messages = []
```

每轮结束就 append。

如果对话永远线性增长，这似乎够用。

但 Pi 需要支持：

- Resume；
- 从早期节点 Branch；
- Model change；
- Thinking level change；
- Compaction；
- Extension custom state；
- Context edit。

此时历史已经不只是“一串聊天消息”。

---

## 6.1 第一个新问题：如果用户从旧节点重新开始怎么办

假设历史是：

```text
A → B → C → D
```

用户回到 B，选择另一条路线：

```text
A → B → E → F
```

如果只有 mutable `messages[]`，最容易做的是删掉 C、D。

但这样原来的工作历史消失了。

Pi 的 SessionManager 选择：

> **append-only tree。**

每个 SessionEntry 有：

```text
id
parentId
timestamp
```

当前：

```text
leafId
```

代表工作正位于哪一个叶子。

所以 Branch 并不是“重写历史”，而是：

```text
移动当前 leaf
↓
从新的父节点继续 append
```

这解决了：

> **历史可以分叉，但过去发生过的内容不需要被覆盖。**

---

## 6.2 `getBranch()`：整个树里，当前工作到底是哪一条线

Session file 可能同时包含：

```text
A → B → C → D
      ↘ E → F
```

模型下一轮显然不能同时把两条互斥分支都当成当前事实。

`getBranch()` 从当前 leaf 沿 `parentId` 回到 root，再反转。

所以它得到：

> **当前工作路径。**

这一步解决的是：

```text
Session history
≠
Current branch
```

但即使拿到了 current branch，也还不能直接全部发给模型。

为什么？

因为 branch 里并不全是模型消息。

---

## 6.3 `buildSessionProjection()`：工作历史和模型 Context 不是一回事

Session branch 中可能包含：

```text
message
model_change
thinking_level_change
usage
compaction
branch_summary
custom
custom_message
context_edit
session_info
```

有些 entry 只是运行状态。

有些会改变模型真正应该看到的内容。

所以 SessionManager 需要把：

```text
append-only Session entries
```

投影成：

```text
messages
thinkingLevel
model
```

这就是：

```text
buildSessionProjection()
```

而：

```text
buildSessionContext()
```

进一步返回当前模型运行需要的 SessionContext。

于是 SessionManager 的核心职责变得清楚：

> **它不是单纯保存历史，而是负责从完整工作历史中重建“当前这一刻模型应该看到什么”。**

这也是为什么它是 context authority。

---

## 6.4 `inMemory()` 只改变存储方式

VNext-01 使用：

```text
SessionManager.inMemory()
```

它不会把 SessionManager 变成一个简化版。

它只是：

```text
persist = false
```

不写 Session file。

Branch、Entry、Projection、Context reconstruction 仍然存在。

因此：

```text
inMemory
改变 persistence

不改变
Session ownership
```

到这里，长期工作终于有了历史基础。

但还有一个真实交互问题没有解决：

> **Agent 正在运行时，用户又发来一句话，这句话应该什么时候进入工作？**

这就逼出了 Queue。

---

# 7. Queue：新输入不是“有没有”，而是“什么时候生效”

假设 Agent 正在：

```text
读文件
→ Tool 执行
→ 准备下一次模型判断
```

这时用户输入：

> “先不要分析利润，重点看现金流。”

如果系统只是：

```text
messages.push(newMessage)
```

并不能说明这条指令什么时候生效。

它可能：

- 错过当前 run；
- 立即打断 Tool；
- 等整个任务做完才生效。

所以 Pi 区分两种明确语义：

```text
steer
followUp
```

---

## 7.1 `steer`：当前工作没结束，但下一次决策要改变方向

`AgentSession.steer()` 的语义是：

> 当前 run 仍在进行，但这条用户输入要在当前 assistant turn 的 Tool Call 执行完后、下一次 LLM request 前进入。

内部路径：

```text
steer(text)
→ _queueUserInput(..., "steer")
→ input handlers / skill / template
→ _queueSteer()
→ _steeringMessages.push(text)
→ queue_update
→ agent.steer(UserMessage)
```

这里有两层状态。

AgentSession 保存 `_steeringMessages`，供 UI / Session 状态观察。

底层 Agent 保存真正等待被 loop 消费的 steering UserMessage。

因此 `steer` 的作用不是“排队”这么泛。

它定义：

> **这条输入属于当前正在进行的工作，并且要在下一个正常决策点生效。**

---

## 7.2 `followUp`：当前工作先做完，再开始下一项

用户也可能说：

> “做完这个以后，再给我写一段摘要。”

它不应该改变当前决策。

这就是 `followUp`。

内部路径：

```text
followUp(text)
→ _queueFollowUp()
→ _followUpMessages.push(text)
→ queue_update
→ agent.followUp(UserMessage)
```

AgentLoop 原本准备自然结束时，会检查：

```text
getFollowUpMessages()
```

如果发现 follow-up：

```text
原本要结束
→ 取出 follow-up
→ 再进入下一轮工作
```

所以：

```text
steer
= 当前工作中的方向修正

followUp
= 当前工作结束后的追加任务
```

---

## 7.3 `queue_update` 为什么有必要

如果 runtime 只在内部排队，UI 会不知道：

- 用户刚才的输入是否已接收；
- 是 steering 还是 follow-up；
- 还有多少内容待处理。

因此 AgentSession 在队列变化时发：

```text
queue_update
```

把当前 steering / followUp 状态暴露给产品层。

这里 Queue 才算讲完整：

```text
用户输入
→ 明确时序语义
→ 进入相应队列
→ runtime 在正确阶段消费
→ UI 能观察状态
```

现在长期工作可以接收中途输入了。

但继续运行几十轮后，会碰到另一个完全不同的问题：

> **历史可以无限增长，但模型 Context Window 不能无限增长。怎么办？**

这才轮到 Compaction。

---

# 8. Compaction：保存完整历史，不等于每次都把完整历史发给模型

SessionManager 可以保留越来越长的工作历史。

但模型每次请求都有 Context Window。

所以迟早会出现：

```text
完整工作历史
>
模型可接受 Context
```

最简单的办法是删除旧消息。

但被删除的内容可能包含：

- 用户长期目标；
- 关键约束；
- 已验证事实；
- Tool Result；
- 重要决策。

直接删会让 Agent 丢失工作状态。

因此 Pi 引入 Compaction。

---

## 8.1 CompactionEntry 表达的不是“删除”，而是“替代表示”

SessionManager 的 `CompactionEntry` 会记录例如：

```text
summary
firstKeptEntryId
tokensBefore
systemMessage
details
usage
```

它表达：

> 较早的一段历史，后续不再逐条进入模型 Context，而由 summary 代表；从某个 entry 往后的新内容继续保留明细。

因此：

```text
完整 Work History
```

仍然存在。

但：

```text
Current Model Context
```

可以更短。

---

## 8.2 为什么 Compaction 要进入 Session history

如果只把 `messages[]` 原地替换成 summary，会丢掉：

- 什么时候压缩；
- 压缩前多少 token；
- 从哪里开始保留明细；
- 原始历史是什么。

Pi 把 compaction 自己也 append 成 SessionEntry。

这样 Resume 时可以重新知道：

> 当前 Context 为什么是这个样子。

这延续了 SessionManager 的 append-only 思路。

---

## 8.3 Compaction 什么时候发生

Pi 区分至少三种 reason：

```text
manual
threshold
overflow
```

**manual**：主动要求压缩。  
**threshold**：上下文达到自动压缩阈值。  
**overflow**：Provider 已经因为 Context 超限失败，需要恢复。

所以 Compaction 不只是“节省 token”。

它也是长期 Session 的连续性机制。

现在 Context 长度问题解决了。

但 Provider 还会发生另一类问题：

> **如果一次请求只是临时失败，整段工作是不是就应该结束？**

这才进入 Retry。

---

# 9. Retry / Recovery：一次请求失败，不等于整段 Session 失败

Provider 调用可能因为：

- 临时网络错误；
- Rate limit；
- transient provider error；
- overflow；

失败。

如果任何一次底层请求失败都直接把整个工作标记为完成，长任务会非常脆弱。

AgentSession 因此维护自动恢复状态，例如：

```text
_retryAbortController
_retryAttempt
_failedResponse
```

并产生：

```text
auto_retry_start
auto_retry_end
```

事件。

---

## 9.1 `agent_end` 和 `agent_settled` 为什么不是一回事

底层 Agent run 结束时会出现：

```text
agent_end
```

但 Session 层此时仍可能：

- 自动 retry；
- 做 overflow compaction；
- 处理 queued work；
- 根据 lifecycle 继续运行。

所以：

```text
agent_end
= 一次 low-level run 结束

agent_settled
= Session 已确定不会再自动继续
```

如果 HMBuddy UI 在 `agent_end` 就把 Busy 状态改成 Done，可能过早。

真正需要“完全空闲”语义时，应关注：

```text
agent_settled
```

---

## 9.2 为什么不能让 HMBuddy runner 自己盲目 retry `prompt()`

看起来可以写：

```text
try {
  session.prompt(...)
} catch {
  session.prompt(...)
}
```

但这可能重新执行已经产生副作用的动作。

未来如果 Tool 是：

```text
修改文件
发送邮件
提交业务
```

重复 Prompt 可能导致重复执行。

所以必须区分：

```text
Pi Provider Retry
```

和：

```text
HMBuddy Domain Action Retry
```

它们不是一回事。

到这里，一个 Session 已经能够：

- 保留历史；
- 分支；
- 接收中途输入；
- 压缩 Context；
- 从部分 Provider failure 中恢复。

新的问题已经不再是“怎样持续运行”。

而是：

> **HMBuddy 怎样把自己的 Office / Banking 能力接进 Pi，又不去修改 Pi 内部 runtime？**

这才轮到 Extension。

---

# 10. Extension：产品怎样扩展 Pi，而不是重新拥有 Pi

HMBuddy 需要加入：

```text
read_office_file
search_office_content
银行权限
审计
敏感操作确认
内部系统连接
```

一个直接但糟糕的办法是：

```text
修改 agent-loop.ts
修改 agent-session.ts
```

每加一种产品能力就改上游。

这样 HMBuddy 很快就会变成长期 fork。

Pi 提供 Extension runtime，就是让产品通过公开扩展面加入能力。

---

## 10.1 `registerTool()`：把领域动作加入 Agent Action Space

HMBuddy Extension 可以：

```text
pi.registerTool(...)
```

注册 `read_office_file`。

ToolDefinition 可以描述：

```text
name
description
parameters
outputSchema
exposure
defaultActive
executionMode
annotations
execute()
```

对于 HMBuddy：

```text
parameters
→ path

outputSchema
→ OfficeReadResult

annotations.readOnlyHint
→ true

execute()
→ TS Office Bridge
```

所以 Extension Tool 不是“一个回调”。

它是：

> **HMBuddy 领域能力与 Pi Tool runtime 之间的正式 Action Contract。**

---

## 10.2 registered、active、callable 为什么要区分

Tool 被注册，不代表一定直接暴露给模型。

Pi 区分：

```text
registered
active / declared
callable
```

并支持：

```text
direct
model-only
codemode
deferred
hidden
```

这说明：

> **代码库里存在某个 Tool，和当前模型拥有这个 Action，是两件不同的事。**

这对未来银行权限尤其重要。

某个实现可以存在，但根据：

- 用户；
- 工作区；
- 权限；
- 当前任务；

决定是否进入 model-facing Action Space。

---

## 10.3 `bindExtensions()`：Extension 不是 import 完就结束

Extension 还会跟随 Session lifecycle。

`session.bindExtensions()` 会把当前 Session 所需 bindings 注入 Extension runtime，并触发例如：

```text
session_start
```

Extension 因而可以在会话生命周期中：

- 注册 / 调整 Tool；
- 监听 Tool Call；
- 接入 UI；
- 连接外部资源；
- 维护自己的 Session state。

所以 Extension 真正解决的是：

```text
Pi 保持 Agent runtime ownership
+
HMBuddy 仍然能注入领域能力
```

现在所有核心部件都已经有了。

最后只剩一个组装问题：

> **Model、SessionManager、ResourceLoader、Tools、Extensions、底层 Agent，这些东西是谁在程序启动时拼成一个可工作的 Session？**

到这里才应该看 `createAgentSession()`。

---

# 11. `createAgentSession()`：前面所有机制的 Composition Root

如果文章一开始就列：

```text
ModelRuntime
SettingsManager
SessionManager
ResourceLoader
Agent
AgentSession
```

读者只会得到一串名字。

现在再看它们，意义不同。

我们已经知道为什么分别需要：

- Model；
- Tool runtime；
- Session history；
- Resources；
- Extensions；
- low-level Agent；
- Session orchestration。

`createAgentSession()` 做的是：

> **把这些已经有清楚职责的部件组合成真正可运行的一段 AgentSession。**

---

## 11.1 先确定运行环境

它解析：

```text
cwd
agentDir
```

并准备：

```text
ModelRuntime
SettingsManager
SessionManager
ResourceLoader
```

如果没提供 ResourceLoader，就创建 `DefaultResourceLoader` 并 `reload()`。

这决定当前项目资源、配置、Skill、Extension 从哪里来。

---

## 11.2 再恢复已有 Session

它调用：

```text
sessionManager.buildSessionContext()
```

拿到已有：

```text
messages
thinkingLevel
model
```

如果是恢复 Session，就尝试恢复之前的 Model 与 Thinking 状态。

这说明 Session 创建不是“从零 new 一次”这么简单。

它可能是在恢复一段已有工作。

---

## 11.3 再确定初始 Tool loadout

Pi 根据：

```text
tools
noTools
excludeTools
settings defaultTools
```

计算初始 active Tool 集合。

这直接决定：

> 第一轮模型能看到哪些 Action。

---

## 11.4 创建底层 Agent，再包装成 AgentSession

底层 Agent 获得：

- model；
- messages；
- tools；
- stream function；
- context transform；
- queue hooks；
- turn lifecycle hooks。

之后再被包装进 AgentSession，与：

```text
SessionManager
SettingsManager
ResourceLoader
ModelRuntime
Extension runtime
```

协作。

所以：

```text
前面的问题链
解释了“为什么需要这些部件”

createAgentSession()
解释“这些部件怎样真正被装起来”
```

---

# 12. 回到 HMBuddy：VNext-01 真正需要实现什么

现在 Pi 的边界已经可以从前面的推导直接得到。

Pi 已经拥有：

```text
模型 Action Space
Tool lookup
参数 validation
执行前 hook
Tool execution lifecycle
Tool Result normalization
Observation reinjection
AgentLoop
Session history projection
Queue
Compaction
Retry / Recovery
Extension lifecycle
Session composition
```

HMBuddy 不应该重新实现这些通用 Agent 能力。

HMBuddy 真正新增：

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

完整运行链因此是：

```text
用户目标
↓
模型看到 read_office_file declaration
↓
模型产生 Tool Call
↓
Pi 找 Tool
↓
Pi 校验参数
↓
Pi 运行 beforeToolCall
↓
Pi 调 Tool execute
↓
HMBuddy TS Bridge
↓
Python 读 DOCX
↓
Tool Result
↓
Pi 把 Observation 放回 Context
↓
AgentLoop 再请求模型
↓
模型形成最终回答
↓
Session 层处理可能的 queued work / recovery
↓
agent_settled
```

这时：

> **Pi 会 Agent；HMBuddy 会银行办公**

不再是先验口号。

它是整篇问题链推导出来的 ownership 结论。

---

# 13. 用真实 HMBuddy 场景从头走一次

用户：

> “阅读 `evals/fixtures/vnext/sample.docx`。告诉我项目编号、负责人、Runtime。”

第一轮模型拥有：

```text
用户目标
+
read_office_file Tool declaration
```

模型决定：

```text
read_office_file(
  path = "evals/fixtures/vnext/sample.docx"
)
```

Pi 的执行层：

```text
lookup
→ 找到 read_office_file

schema
→ path 是 string

beforeToolCall
→ 允许读取

execute
→ HMBuddy Office Bridge
```

Python 返回：

```text
HM-VNEXT-001
林海
Pi + Python
```

Pi 把这个结果变成 ToolResultMessage，放回 Context。

AgentLoop 发起下一次模型请求。

模型现在看到：

```text
用户问题
+
自己的 Tool Call
+
真实文件内容
```

于是返回最终回答。

如果没有 queued work，也不需要 recovery，Session 最后进入：

```text
agent_settled
```

---

# 14. 再看三个变化，检验 mental model 是否真的建立

## 变化一：模型调用了不存在的 Tool

第一处失败发生在：

```text
Tool lookup
```

不会进入 HMBuddy Python。

所以排错不应该先查 DOCX parser。

---

## 变化二：用户中途说“先看现金流”

这不是 Tool execution 问题。

它属于：

```text
Session queue semantics
```

如果希望影响当前工作，应进入 `steer`。

---

## 变化三：运行几十轮后 Context 过大

这不是 AgentLoop “循环太多”的 bug。

问题属于：

```text
Session history
→ Context projection
→ Compaction
```

这三个判断能直接验证你是否真的知道每层负责什么。

---

# 15. 最终 Mental Model

现在才压缩概念。

### Tool

> 模型 Action Space 与程序执行能力之间的 Contract。

### Tool execution path

> 把模型的 Action Intent 经过 lookup、validation、policy、execute，变成统一结果的受控边界。

### Tool Result

> Action 产生的 Observation，不天然等于最终用户答案。

### AgentLoop

> 让 Observation 重新进入 Decision，使模型能够基于动作结果继续行动。

### SessionManager

> 从 append-only 工作历史、分支和压缩记录中重建当前 canonical model context。

### AgentSession

> 把一次次 Agent run 组织成长期工作会话，承接 Queue、Compaction、Retry、Extension lifecycle 等 Session concern。

### Extension

> 产品通过公开 seam 向 Pi 注入领域 Action 和 lifecycle 行为，而不重新拥有 Agent runtime。

### `createAgentSession()`

> 把 Model、Resources、Tools、Session state、Extensions 和底层 Agent 组合成可工作的 Session。

---

# 16. Deep Read Gate

读完后，读者应该能沿因果链回答：

1. 为什么普通“宿主读文件 + LLM”不等于 Agent？
2. 为什么第一步只需要 Tool declaration？
3. Tool Call 为什么只是 Action Intent？
4. 为什么必须先 lookup，再 validation？
5. 为什么参数合法后仍需要 policy hook？
6. 为什么 execute failure 要规范化为 Tool Result？
7. 为什么 Tool Result 不等于最终答案？
8. 为什么 Observation 必须再回模型？
9. AgentLoop 是在哪个问题出现时才真正必要？
10. AgentLoop 明确不负责什么？
11. 为什么一次 run 结束后还需要 Session？
12. 为什么 Session history 不能只是 mutable `messages[]`？
13. append-only tree / leaf / branch 分别解决什么？
14. `buildSessionContext()` 为什么是 Context authority？
15. `steer` 与 `followUp` 为什么必须分开？
16. Compaction 为什么不是删历史？
17. Provider Retry 与 Domain Tool Retry 为什么不是一回事？
18. `agent_end` 为什么不一定代表整个工作完成？
19. Extension 为什么是 HMBuddy 的正确接入面？
20. 为什么 `createAgentSession()` 应该最后理解，而不是最先背？
21. HMBuddy VNext-01 真正应该实现哪一小段？

如果读者必须先知道后面几章的概念，才能理解前面某一章，说明 Progressive Disclosure 失败。

如果读者只能说出类名，却说不清输入、状态变化、输出和边界，说明 Mechanism Depth 失败。

只有当这两类失败都不存在，这篇 Deep Read 才通过 Quality Baseline。
