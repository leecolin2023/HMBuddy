# D — Deep Read：Pi AgentSession / Tool Calling Vertical Slice

> **目标读者：** 会基本编程、知道 LLM 和 API，但没读过 Pi，也不了解 HMBuddy V1.0。  
> **Source pin：** `earendil-works/pi@4c6fb7cfe8c538a668726f6f8b3554098c39faee`  
> **Pi package：** `@earendil-works/pi-coding-agent@1.0.0`  
> **阅读目标：** 沿“问题 → 最小机制 → 新问题”的主线理解 Pi；关键机制讲到需求规格说明书粒度；长篇过程中保持术语和抽象层级连续。

---

# 0. 起点：会回答，不等于会做事

用户对 HMBuddy 说：

> “读取 `sample.docx`，告诉我项目编号、负责人和 Runtime。”

一个普通 LLM 应用完全可以：

```text
宿主程序判断用户要读文件
→ 宿主程序读取 sample.docx
→ 把文本塞进 Prompt
→ 模型回答
```

结果可能完全正确。

但控制权仍在宿主。

宿主已经提前决定：

- 要不要读；
- 读哪一份；
- 调什么函数；
- 读完下一步是什么。

一旦用户说：

> “先看看项目目录里有哪些材料，再自己判断应该读哪份，然后告诉我主要风险。”

宿主就需要继续预写：

```text
先 list
→ 再判断
→ 再 search
→ 再判断
→ 再 read
```

开放程度越高，宿主里的流程判断越多。

所以第一个真正的问题是：

> **怎样让模型自己选择下一步动作？**

---

# 1. 先让模型知道：它有哪些动作

模型不可能主动选择一个它从未见过的动作。

因此第一步不是执行，而是**声明动作**。

Pi 用 Tool 描述模型可以选择的 Action。

对模型最关键的是：

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
读取工作区中的 Office 文件

parameters:
{
  path: string
}
```

它们分别回答：

```text
动作叫什么？
↓
什么时候适合用？
↓
调用时必须提供什么？
```

程序侧还有：

```text
execute()
```

它是真正的实现。

于是第一个稳定概念建立起来：

> **Tool declaration**：模型可见的 Action Contract。  
> **Tool implementation**：程序真正执行动作的代码。

这两者不能混为一谈。

模型拿到 declaration 后，可以输出：

```json
{
  "name": "read_office_file",
  "arguments": {
    "path": "evals/fixtures/vnext/sample.docx"
  }
}
```

现在模型已经会表达：

> “我想执行这个动作。”

但仍只是表达。

所以唯一下一问是：

> **`name + arguments` 怎样真正变成一次函数调用？**

---

# 2. 从 Tool Call 到一次真实执行

先只解决“一次 Tool 怎么执行”。

最小执行器可以想成：

```text
收到 Tool Call
→ 根据 name 找到实现
→ 把 arguments 传进去
→ 调函数
→ 得到结果
```

此时先建立另一个稳定概念：

> **Tool Call**：模型给出的结构化 Action Intent。

它不是代码执行本身。

在 Pi 当前实现中，这条执行路径位于：

```text
packages/agent/src/agent-loop.ts
```

但源码文件名不决定我们现在就要理解 AgentLoop。

此刻只关心“一次 Tool execution”。

---

## 2.1 第一道问题：Tool 名真的存在吗？

模型可能输出：

```text
read_doc
```

但当前只有：

```text
read_office_file
```

所以程序必须先做：

```text
toolCall.name
→ Tool lookup
→ concrete implementation
```

Pi 找不到 Tool 时，会形成一个标准错误结果，而不是让代码因为 `undefined` 崩掉。

这一步解决：

> 模型使用的是符号名称；程序需要把它解析成当前真正可执行的能力。

Tool 找到了。

唯一下一问：

> **模型给的参数能直接交给实现吗？**

---

## 2.2 第二道问题：参数是模型生成的，不能直接信任

Tool 要求：

```json
{
  "path": "..."
}
```

模型却可能输出：

```json
{}
```

或：

```json
{
  "path": 123
}
```

因此真正执行前，需要：

```text
prepareArguments
→ validateToolArguments
```

`prepareArguments` 可以处理参数兼容性整理。

`validateToolArguments` 根据 Tool schema 做结构验证。

于是 Tool implementation 可以依赖：

> 正常进入 `execute()` 的参数已经通过 Tool Contract 的结构校验。

参数也正确了。

唯一下一问：

> **参数合法，就一定允许执行吗？**

---

## 2.3 第三道问题：合法动作仍可能不被允许

假设未来 Tool 是：

```text
delete_file
send_external_email
write_business_system
```

模型可能给出完全合法的参数。

但银行系统仍可能要求：

- 当前用户有权限；
- 目标路径允许访问；
- 敏感写入需要确认；
- 外发需要审批。

所以：

```text
参数合法
≠
动作被授权
```

Pi 在真正执行前提供 `beforeToolCall` hook。

逻辑位置是：

```text
Tool 已找到
→ 参数已校验
→ beforeToolCall
→ execute
```

它可以阻断：

```text
block = true
reason = ...
terminate = true / false
```

这里建立一个重要边界：

> 模型负责提出 Action Intent；程序负责决定这个 Action 是否允许落地。

动作现在也获准了。

唯一下一问：

> **即使允许执行，函数本身失败怎么办？**

---

## 2.4 第四道问题：执行失败也必须成为统一结果

Tool implementation 仍可能：

- 文件不存在；
- subprocess 超时；
- Parser 失败；
- 外部服务异常；
- execute 抛错。

Pi 会把多类失败统一变成 Tool Result，并标记错误状态。

因此一次 Tool execution 的完整最小链是：

```text
Tool Call
→ lookup
→ schema validation
→ beforeToolCall
→ execute
→ Tool Result
```

到这里，“一次动作怎样安全落地”已经完整。

现在正式建立第三个稳定概念：

> **Tool Result**：一次 Tool execution 的标准结果，可以成功，也可以表示失败。

注意，我们还没有说它是不是最终用户答案。

这正是下一问：

> **Tool Result 已经拿到了，为什么不能直接展示给用户然后结束？**

---

# 3. Tool Result 不是 Final Answer：它只是新的 Observation

假设 `read_office_file` 返回：

```text
项目编号：HM-VNEXT-001
负责人：林海
Runtime：Pi + Python
```

如果用户只问“负责人是谁”，似乎可以直接返回。

但如果用户问：

> “负责人是谁，并判断当前 Runtime 是否符合项目目标。”

Tool 只完成了“读取文件”。

它不知道最终目标是否完成。

所以我们引入一个认知层面的名称：

> **Observation**：Agent 采取 Action 后，新获得的事实或状态。

这里明确：

```text
Tool Result
= 程序层标准结果

Observation
= 从 Agent 决策角度看，这个结果提供的新信息
```

两者不是两个不同对象，而是同一结果在不同认知层的含义。

模型原本只有：

```text
用户目标
+
已有 Context
```

执行 Tool 后多了：

```text
Observation
```

如果 Observation 不重新交给模型，模型就无法：

- 判断是否足够；
- 决定是否还要搜索；
- 决定是否要读第二份文件；
- 处理 Tool 失败；
- 形成最终回答。

所以：

```text
Tool Result
→ 放回模型可见 Context
```

现在唯一下一问变成：

> **Observation 已经回来了，谁负责真的再让模型决策一次？**

到这里才需要 AgentLoop。

---

# 4. AgentLoop：让 Observation 重新进入 Decision

我们已经拥有：

```text
Decision
→ Action
→ Observation
```

真正的 Agent 还需要：

```text
Observation
→ Decision again
```

Pi 的 `runLoop()` 解决的就是这个闭环。

---

## 4.1 一轮模型响应后发生什么

assistant message 中可能包含 Tool Call。

Pi 找出：

```text
type = toolCall
```

然后走刚才已经建立的 Tool execution 路径。

执行完成后得到：

```text
ToolResultMessage[]
```

这些结果被加入：

```text
currentContext.messages
```

因此当前 Context 从：

```text
User:
读取 sample.docx
```

变成：

```text
User:
读取 sample.docx

Assistant:
toolCall(read_office_file)

Tool:
HM-VNEXT-001 / 林海 / Pi + Python
```

此时 Observation 已经真正进入下一轮模型可见状态。

---

## 4.2 为什么会再请求模型

只要刚才的 Tool batch 没有要求整体终止，Pi 会继续下一轮模型请求。

于是：

```text
第一次模型请求
→ 模型决定读文件

Tool execution
→ 得到文件事实

第二次模型请求
→ 模型基于文件事实继续判断
```

这就是 AgentLoop 的核心职责：

> **让 Action 产生的 Observation 能够重新进入 Decision。**

---

## 4.3 多个 Tool Call 怎么办

一个 assistant message 可以产生多个 Tool Call。

Pi 支持：

```text
sequential
parallel
```

是否并行由 Tool execution 配置和 `executionMode` 决定。

即使并行，最终形成 ToolResultMessage 时仍保持原 Tool Call 顺序。

这样：

> 物理执行可以并发，但模型看到的 Action / Result 对应关系仍然稳定。

---

## 4.4 Tool 失败后为什么 Agent 仍可能继续

前面建立的 Tool Result 可以表示失败。

所以：

```text
Tool not found
参数错误
PATH_NOT_ALLOWED
Parser failure
```

都可以作为 Observation 回到模型。

模型随后可以：

- 换策略；
- 请求用户操作；
- 明确解释失败。

所以 Tool failure 不必天然等于 Agent crash。

---

## 4.5 一次 Agent run 什么时候结束

当前 run 中，当：

- 没有更多 Tool Call；
- 没有新的当前工作输入；
- 没有显式 continuation；

底层 Agent run 才会自然结束。

到这里，AgentLoop 已经完整解决“一次 run 内的 Decide → Act → Observe”。

唯一下一问：

> **下一次用户再说“继续刚才那份文件”时，上一轮工作的状态从哪里来？**

这才进入 Session。

---

# 5. 从一次 run 到长期工作：先建立三个稳定概念

办公 Agent 的工作通常不是一轮完成。

用户会：

```text
先读报告
→ 继续追问
→ 改方向
→ 再读新文件
→ 隔一段时间恢复
```

所以：

```text
一次 Agent run
≠
一段长期工作
```

接下来为了避免后文术语漂移，我们先建立三个 canonical term。

### Work History

> **Work History**：一段工作完整、可追溯的历史记录。它不仅可能包含普通消息，也包括模型切换、Compaction、Extension state 等 Session entry。

### Session Tree

> **Session Tree**：Pi 用 append-only entries + `parentId` 表示 Work History 分支关系的结构。

### Current Model Context

> **Current Model Context**：某一次真实模型请求当前应该看到的内容。

这三个词后文保持不变。

特别注意：

```text
Work History
≠
Session Tree
≠
Current Model Context
```

Work History 是“完整工作记录”这个语义概念。

Session Tree 是 Pi 保存 Work History 的结构。

Current Model Context 是从 Work History 投影出来、真正送给模型的当前上下文。

现在我们才能问：

> **谁负责维护这些长期状态，并把 Work History 变成 Current Model Context？**

---

# 6. SessionManager：完整工作记录如何变成当前上下文

Pi 的 `SessionManager` 负责管理 Work History 的 Session entries，并重建当前工作路径与 Current Model Context。

---

## 6.1 为什么不是一个 mutable `messages[]`

长期工作中不只有：

```text
user
assistant
toolResult
```

还可能有：

```text
model_change
thinking_level_change
usage
compaction
branch_summary
custom
context_edit
session_info
```

而且用户还可能从旧节点重新开始。

假设曾经：

```text
A → B → C → D
```

后来从 B 分出：

```text
A → B → E → F
```

如果只有 mutable `messages[]`，很容易把旧路径 C、D 覆盖掉。

Pi 选择用 append-only Session Tree。

每个 entry 有：

```text
id
parentId
timestamp
```

当前：

```text
leafId
```

表示当前工作落在哪个叶子。

---

## 6.2 `getBranch()`：当前正在沿哪条 Work History 路径工作

Session Tree 里可以同时保留多条分支。

但模型当前只能沿其中一条工作路径继续。

`getBranch()` 从当前 leaf 沿 `parentId` 回到 root，再反转。

它得到：

> 当前工作所处的 branch。

所以：

```text
完整 Work History
```

可能包含多条路径；

而：

```text
Current Branch
```

只是当前 leaf 对应的一条路径。

这里再建立一个 canonical term：

> **Current Branch**：Session Tree 中当前 leaf 对应的工作路径。

---

## 6.3 为什么 Current Branch 还不能直接变成 Current Model Context

Current Branch 中仍包含很多不应直接发给模型的 entry。

例如：

```text
usage
label
session_info
model_change
compaction
context_edit
```

因此还需要一次投影。

`buildSessionProjection()` 把当前 Session state 解析为：

```text
messages
thinkingLevel
model
```

`buildSessionContext()` 再生成当前运行所需的 SessionContext。

所以：

```text
Work History
→ Session Tree
→ Current Branch
→ Session Projection
→ Current Model Context
```

这条链非常重要。

它说明 SessionManager 不是“保存聊天记录”的工具。

它负责的是：

> **从完整、可追溯的工作历史中，重建当前模型应该看到什么。**

---

## 6.4 `inMemory()` 改变的只是持久化

VNext-01 使用：

```text
SessionManager.inMemory()
```

它只是：

```text
persist = false
```

不写 Session file。

Work History 的 entry 逻辑、Session Tree、Current Branch 与 Context projection 仍然存在。

所以：

```text
inMemory
改变 persistence

不改变
SessionManager 的 authority
```

现在长期工作的“历史问题”解决了。

唯一下一问：

> **如果 Agent 正在当前 run 中工作，用户又发一条新要求，这条输入应该什么时候生效？**

---

# 7. Queue：新输入最重要的不是“有没有”，而是“何时生效”

假设 Agent 正在：

```text
读文件
→ Tool execution
→ 准备下一次模型判断
```

用户突然说：

> “先别看利润，重点看现金流。”

如果只是 append 一条 message，并不能说明它什么时候进入 Current Model Context。

Pi 因此区分：

```text
steer
followUp
```

---

## 7.1 `steer`：属于当前工作，要尽快影响下一次决策

`AgentSession.steer()` 的语义是：

> 当前 run 仍在进行，但新输入应在当前 assistant turn 的 Tool Call 执行完后、下一次模型请求前进入。

内部：

```text
steer(text)
→ _queueUserInput(..., "steer")
→ _queueSteer()
→ _steeringMessages.push(text)
→ queue_update
→ agent.steer(UserMessage)
```

这条消息最终会在下一个合适的决策边界进入 Current Model Context。

所以：

> **steer = 当前工作的方向修正。**

---

## 7.2 `followUp`：当前工作先结束，再处理下一项

如果用户说：

> “做完以后，再给我写个摘要。”

这不应该改变当前工作。

`followUp()` 会把输入排到当前 Agent 自然结束之后。

Agent 原本要结束时，再检查 follow-up queue；有内容就开始下一项。

所以：

> **followUp = 当前工作完成后的追加任务。**

---

## 7.3 `queue_update`：为什么产品层也要知道

AgentSession 还维护：

```text
_steeringMessages
_followUpMessages
```

并在变化时发：

```text
queue_update
```

这样 UI 才知道：

- 输入已被接收；
- 是当前方向修正还是后续任务；
- 还有多少内容待处理。

到这里 Queue 解决的是“输入时序”。

唯一下一问：

> **即使输入时序解决了，Work History 越来越长，Current Model Context 装不下怎么办？**

---

# 8. Compaction：Work History 可以很长，但 Current Model Context 不能无限长

这里先重新接回第 5～6 章建立的两个 canonical term：

> **Work History** 是完整、可追溯的工作记录。  
> **Current Model Context** 是某一次模型请求真正看到的内容。

前面之所以把两者分开，就是因为它们迟早会出现长度矛盾：

```text
Work History 持续增长
↓
模型 Context Window 有上限
```

这正是 Compaction 要解决的问题。

---

## 8.1 为什么不能直接删除 Work History

最粗暴的方案是删老消息。

但旧内容可能包含：

- 用户长期目标；
- 关键约束；
- 之前确认的事实；
- Tool Result；
- 重要决策。

直接删 Work History，会损坏可追溯性，也可能让后续无法 Resume 或解释过去发生了什么。

因此 Compaction 的目标不是：

> 删除 Work History。

而是：

> **让更长的 Work History 能以更短的形式投影成 Current Model Context。**

---

## 8.2 CompactionEntry：为什么压缩本身也要成为 Work History 的一部分

`CompactionEntry` 会记录例如：

```text
summary
firstKeptEntryId
tokensBefore
systemMessage
details / usage
```

它表达：

> 较早的一段 Work History，后续构建 Current Model Context 时由 summary 代表；从 `firstKeptEntryId` 往后的内容继续保留明细。

这里没有出现一个新的“Session history”概念。

仍然只有前面定义过的：

```text
Work History
Current Model Context
```

为什么 CompactionEntry 自己也要 append 到 Work History？

因为如果只把当前 `messages[]` 原地替换掉，那么恢复 Session 时会失去：

- 什么时候发生过压缩；
- 压缩前大约多长；
- 哪段旧内容由 summary 代表；
- 从哪里继续保留明细。

把 Compaction 作为 Work History 中的正式 entry，SessionManager 以后才能重新构建同样的 Current Model Context。

所以：

```text
完整 Work History
仍保留可追溯事实

CompactionEntry
记录“如何压缩投影”

Current Model Context
使用压缩后的表示
```

这是 Compaction 与 SessionManager 的真正协作关系。

---

## 8.3 Compaction 什么时候触发

Pi 区分：

```text
manual
threshold
overflow
```

- `manual`：显式触发；
- `threshold`：达到自动压缩阈值；
- `overflow`：Provider 已经因为 Context 超限失败，需要恢复。

所以 Compaction 既服务长期工作，也服务 overflow recovery。

Context 长度问题解决了。

唯一下一问：

> **如果失败不是 Context 太长，而只是一次 Provider 临时失败，整段工作还要不要继续？**

---

# 9. Retry / Recovery：一次请求失败，不等于整个工作失败

Provider 可能因为：

- 临时网络异常；
- Rate limit；
- transient provider error；
- overflow；

失败。

AgentSession 因此维护自动恢复状态，例如：

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

---

## 9.1 `agent_end` 为什么还不是整段工作的结束

底层一次 Agent run 结束时会出现：

```text
agent_end
```

但 Session 层可能还要：

- auto retry；
- overflow compaction；
- 处理 queued work；
- 做其他 Session-level continuation。

所以：

```text
agent_end
= 一次 low-level run 结束

agent_settled
= 当前 Session 已确定不会再自动继续
```

这对产品状态很重要。

HMBuddy UI 如果在 `agent_end` 就显示 Done，可能过早。

---

## 9.2 Provider Retry 和 Domain Action Retry 为什么必须分开

不能简单在 runner 里：

```text
prompt 失败
→ 再 prompt 一次
```

因为上一轮可能已经执行过有副作用的 Tool。

例如：

```text
写文件
发送邮件
提交业务
```

盲目重放用户 Prompt 可能重复动作。

所以：

```text
Pi Provider Retry
≠
HMBuddy Domain Action Retry
```

前者是 Session / Provider runtime 的恢复问题。

后者是具体领域 Action 是否具有幂等性、是否允许重复执行的问题。

到这里，我们已经把 Pi 自己如何维持长期 Agent 工作讲清。

现在出现的是另一类问题：

> **一个具体产品怎样把自己的领域能力接入 Pi，而不修改这些已经稳定的 runtime 机制？**

这才进入 Extension。

---

# 10. Extension：从 Pi 通用 runtime 过渡到产品能力

先明确到目前为止我们建立的通用结论：

```text
Pi 已经负责：
Tool execution
AgentLoop
Work History / Context projection
Queue
Compaction
Retry / Recovery
```

这些都是“Agent 如何运行”的通用问题。

一个产品真正不同的地方，通常不是它需要另一套 AgentLoop，而是：

> **它需要让 Agent 拥有不同的领域 Action。**

Pi 为此提供 Extension seam。

Extension 的目的就是：

> **产品可以增加 Tool、lifecycle handler、UI integration 等能力，而不修改 Pi 核心 runtime。**

---

## 10.1 `registerTool()`：先理解通用能力，不急着跳 HMBuddy

Extension 可以通过：

```text
pi.registerTool(...)
```

注册领域 Tool。

ToolDefinition 可以包含：

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

所以 `registerTool()` 的通用意义是：

> **把一个产品领域 Action 接入 Pi 已经存在的 Tool runtime。**

注意，这里仍然是在讲 Pi 通用机制。

---

## 10.2 registered、active、callable：实现存在，不等于模型现在拥有它

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

因此：

```text
Tool implementation exists
≠
Current model can see this Action
```

这为不同产品留下了动态能力控制空间。

到这里，Extension 的通用机制已经讲完。

现在才做一次明确的 Abstract → Concrete Transition。

---

# 11. 从 Pi Extension 到 HMBuddy：领域差异到底是什么

刚刚建立的通用结论是：

> Pi Extension 给产品留下了一个公开位置，用来增加领域 Action，而不重新拥有 Agent runtime。

现在回到 HMBuddy。

HMBuddy 与普通 coding agent 的主要差异，不是它需要：

```text
另一套 AgentLoop
另一套 SessionManager
另一套 ToolRegistry
```

而是它需要真正理解和操作：

```text
DOCX
XLSX
PPTX
PDF
OCR
Office / WPS
银行办公规则
```

因此，HMBuddy 在 Pi Extension seam 上最自然的第一项领域 Action 就是：

```text
read_office_file
```

这就是从“Pi 通用 Extension”到“HMBuddy 具体 Tool”的桥。

---

## 11.1 `read_office_file` 怎样映射到 ToolDefinition

对 HMBuddy：

```text
name
→ read_office_file

parameters
→ { path: string }

annotations.readOnlyHint
→ true

outputSchema
→ OfficeReadResult schema

execute()
→ TypeScript Office Bridge
```

这里 `execute()` 不自己解析 DOCX。

它继续把领域动作交给：

```text
TS Office Bridge
→ Python Office Runtime
→ DOCX reader
```

所以 HMBuddy 接入 Pi 的边界是：

```text
Pi Tool runtime
↓
HMBuddy Tool adapter
↓
Office capability
```

而不是在 Pi 外再建第二套 Agent framework。

---

## 11.2 为什么 Tool 是否 active 对 HMBuddy 也重要

前面 Pi 已经区分：

```text
registered
active
callable
```

映射到 HMBuddy 后，它意味着：

> `read_office_file` 的实现可以存在，但不代表当前用户、当前工作区、当前任务一定应该看到它。

以后可以根据：

- 权限；
- Workspace；
- 文件类型；
- 银行 policy；

决定 Action 是否暴露给模型。

这里我们没有重新定义 active。

只是把前面 Pi 的通用概念映射到 HMBuddy 的产品场景。

---

# 12. `createAgentSession()`：最后才看这些机制怎样被组装起来

到这里，读者已经知道为什么需要：

```text
Model
Tools
AgentLoop
SessionManager
Queue
Compaction
Retry
Extensions
```

现在再看：

```text
createAgentSession()
```

它就不再是一串陌生依赖。

它是 Composition Root：

> **把前面已经建立的 runtime responsibilities 组装成一段真正可工作的 AgentSession。**

---

## 12.1 它先准备运行环境

包括：

```text
cwd
agentDir
ModelRuntime
SettingsManager
SessionManager
ResourceLoader
```

如果没传 ResourceLoader，会创建 `DefaultResourceLoader` 并 reload。

---

## 12.2 它恢复既有工作

通过：

```text
sessionManager.buildSessionContext()
```

恢复已有：

```text
messages
thinkingLevel
model
```

所以创建 Session 也可能是在恢复已有 Work History 的当前运行状态。

---

## 12.3 它计算初始 Tool loadout

结合：

```text
tools
noTools
excludeTools
settings defaultTools
```

确定第一轮模型真正看到哪些 Action。

---

## 12.4 它创建底层 Agent，再包装为 AgentSession

底层 Agent 获得：

- model；
- messages；
- tools；
- stream function；
- context transform；
- queue / turn hooks。

然后 AgentSession 再与：

```text
SessionManager
SettingsManager
ResourceLoader
ModelRuntime
Extension runtime
```

组合。

所以：

```text
前文解释：
为什么这些机制分别存在

createAgentSession() 解释：
它们如何成为一段实际运行的 Session
```

---

# 13. 现在再看 HMBuddy VNext-01 的完整链

经过前面的推导，Pi 与 HMBuddy 的 ownership 已经自然形成。

Pi 负责：

```text
Tool declaration / execution contract
lookup / validation / beforeToolCall
Tool Result normalization
Observation reinjection
AgentLoop
Work History → Current Model Context
Queue
Compaction
Retry / Recovery
Extension lifecycle
Session composition
```

HMBuddy 负责：

```text
read_office_file.execute()
→ TypeScript Office Bridge
→ Python Office Runtime
→ DOCX reader
→ OfficeReadResult
```

完整运行：

```text
用户目标
↓
模型看到 read_office_file declaration
↓
模型产生 Tool Call
↓
Pi lookup
↓
Pi validation
↓
Pi beforeToolCall
↓
HMBuddy Tool execute
↓
Office Bridge / Python / DOCX
↓
Tool Result
↓
Observation 回到 Current Model Context
↓
AgentLoop 再请求模型
↓
最终回答
↓
Session 层处理 queued work / recovery
↓
agent_settled
```

这时：

> **Pi 会 Agent；HMBuddy 会银行办公**

不是预设 slogan，而是前文一步步推导出的 ownership 结论。

---

# 14. 三个变化，检查长程 mental model 是否还连得上

## 变化一：模型调用不存在的 Tool

第一处失败：

```text
Tool lookup
```

所以不应该先查 Python parser。

---

## 变化二：用户中途说“先看现金流”

问题属于：

```text
Queue semantics
```

如果要影响当前工作，应考虑 `steer`。

---

## 变化三：运行很久后 Context 太长

重新调用前面的 canonical terms：

```text
Work History
仍然可以完整保留

Current Model Context
不能无限增长
```

所以问题落在：

```text
Compaction + Session projection
```

而不是“AgentLoop 循环次数太多”。

---

# 15. Canonical Concept Map

这张表不是替代正文，而是确认全文术语没有漂移。

| Canonical Term | 本文固定含义 |
|---|---|
| Tool declaration | 模型可见的 Action Contract |
| Tool implementation | 真正执行动作的程序实现 |
| Tool Call | 模型给出的结构化 Action Intent |
| Tool Result | 一次 Tool execution 的标准程序结果 |
| Observation | 从 Agent 决策视角看 Tool Result 带来的新信息 |
| AgentLoop | 让 Observation 重新进入 Decision 的 run-level 控制循环 |
| Work History | 一段工作的完整、可追溯记录 |
| Session Tree | Pi 用 append-only entries 表示 Work History 分支的结构 |
| Current Branch | Session Tree 中当前 leaf 对应的工作路径 |
| Current Model Context | 某一次模型请求真正看到的内容 |
| SessionManager | 从 Work History 重建 Current Branch 与 Current Model Context 的 authority |
| AgentSession | 组织长期 Agent 工作的 session-level orchestration |
| Extension | 产品向 Pi 注入领域 Action / lifecycle 的公开扩展面 |

---

# 16. 最终 Mental Model

### Tool

> 模型 Action Space 与程序执行能力之间的 Contract。

### Tool execution path

> 把 Tool Call 经过 lookup、validation、policy、execute，变成 Tool Result 的受控执行边界。

### AgentLoop

> 让 Tool Result 带来的 Observation 回到模型，使模型能够继续 Decision。

### SessionManager

> 管理完整 Work History 的结构，并重建 Current Branch 和 Current Model Context。

### AgentSession

> 把一次次 Agent run 组织成长期工作，承接 Queue、Compaction、Retry、Extension lifecycle 等 session-level concern。

### Extension

> 产品通过公开 seam 注入自己的领域 Action，而不重新拥有 Pi runtime。

### HMBuddy

> 在 Pi 的 Extension / Tool seam 上提供 Office 与 Banking capability。

---

# 17. Deep Read Gate

读完后，读者应该能够连续解释：

1. 为什么普通“宿主读文件 + LLM”不等于 Agent；
2. Tool declaration 解决了什么；
3. Tool Call 为什么不是执行；
4. lookup / validation / policy 为什么按这个顺序出现；
5. Tool Result 与 Observation 的关系；
6. AgentLoop 为什么直到 Observation 回来后才真正需要；
7. 一次 run 为什么不等于长期工作；
8. Work History、Session Tree、Current Branch、Current Model Context 分别是什么；
9. SessionManager 为什么不是简单 history store；
10. `inMemory()` 改变什么、不改变什么；
11. `steer` / `followUp` 的时序语义；
12. Compaction 为什么解决的是 Work History 与 Current Model Context 的失配；
13. CompactionEntry 为什么属于 Work History；
14. Retry 为什么是 Session-level recovery；
15. `agent_end` 与 `agent_settled` 的边界；
16. Extension 的通用意义；
17. 为什么从 Extension 映射到 HMBuddy 时首先得到 `read_office_file`；
18. `registerTool()` 在 Pi 通用机制和 HMBuddy 具体实现中分别意味着什么；
19. `createAgentSession()` 为什么最后理解最自然；
20. HMBuddy VNext-01 的 ownership 边界在哪里。

如果文章后半程出现一个词，读者必须翻回多章才能重新猜它是什么，Cognitive Continuity 失败。

如果从 Pi 机制突然跳到 HMBuddy 代码而没有说明“为什么现在切过去”，Transition Bridge 失败。

只有四类 Gate 同时通过，这篇 Deep Read 才达到 Quality Baseline。
