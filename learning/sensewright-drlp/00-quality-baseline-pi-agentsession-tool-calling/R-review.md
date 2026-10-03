# R — Review：Pi AgentSession / Tool Calling Vertical Slice

> Review 重新读取 Pi pinned source / tests / docs，不把 D 当证据。

## 总体判断

这条 vertical slice 足以支撑 HMBuddy 当前的 Pi-native Ownership Boundary：

~~~text
Pi owns:
Agent / Session / Tool execution / Extension lifecycle / Agent loop

HMBuddy owns:
Office capability behind the Tool
~~~

没有看到需要 HMBuddy 自建第二套 AgentLoop、ToolRegistry 或 Session Framework 的证据。

但有几处如果不澄清，会让 VNext-01 实施时产生错误。

## Finding 1 — AgentSession 不是 AgentLoop 的另一个名字

**Material**

低层 control loop 在 packages/agent。

AgentSession 位于 packages/coding-agent，它把 Agent、SessionManager、Settings、ModelRuntime、ResourceLoader、Extensions、compaction / retry / queue 组合成一段工作会话。

必须坚持：

~~~text
Agent core
≠
AgentSession orchestration
≠
SessionManager persistence/context authority
~~~

否则会看错 ownership。

## Finding 2 — structuredContent 应与 outputSchema 一起设计

**Material**

Pi 1.0 Extension contract 明确：Tool 如果声明结构化程序输出，应定义 outputSchema 并返回匹配的 structuredContent。

VNext-01 的 content / structuredContent / details 三分方向正确，但实施时不应只是“多塞一个 JSON 字段”。

应形成：

~~~text
parameters schema
→ Tool input contract

outputSchema
→ Tool structured output contract

content
→ model-facing representation
~~~

## Finding 3 — Tool 注册成功与模型自主调用是两种证据

**Material**

T3 可以证明：

~~~text
Extension loads
Tool is registered
Tool is active
Tool contract works
~~~

但不能证明：

~~~text
真实模型会在自然语言目标下自主选择这个 Tool
~~~

所以：

~~~text
T3 = Extension contract smoke
T4 = Real Agent behavior
~~~

T1–T3 全绿时不能把 Architecture Spike 标记 Complete。

## Finding 4 — active tool 不等于所有 registered tool

**Material for learning**

Pi 区分：

- registered；
- active / declared-to-model；
- callable-from-other-tools。

exposure 还包括 direct / model-only / codemode / deferred / hidden。

VNext-01 的 read_office_file 使用 direct Tool 足够，但学习材料不能把 registerTool() = 模型一定看得到 当成普遍规律。

## Finding 5 — agent_end 不是最强完成信号

**Material**

Pi docs 明确 agent_end 后仍可能有自动 retry / recovery / queued work。

agent_settled 才表示不会自动继续。

HMBuddy live eval 应记录：

~~~text
tool_execution_start
tool_execution_end
message_end(final)
agent_settled
~~~

## Finding 6 — cwd / project trust 不是银行安全边界

**Material for future governance**

Pi Extension 与 Pi 进程共享 OS 权限。

因此 cwd、Tool path check、project trust 可以形成资源边界，但不是完整 sandbox。

HMBuddy 后续仍需负责 OS / process isolation、network restriction、ACL、approval、audit、sensitive-data rules。

## Finding 7 — deterministic upstream test 可以验证机制，但不能冒充 T4

**Material**

Pi checked test 可以真实观察：

~~~text
assistant emits toolCall
→ runtime executes
→ Tool Result enters messages
→ second assistant response
~~~

这是机制证据。

但它不是“真实 LLM 在自然语言目标下自主选择 HMBuddy Tool”。

所以：

~~~text
L = deterministic test 可完成 mechanism validation
P / VNext T4 = 仍需真实 model behavior
~~~

## Review 结论

源码证据支持：

> **HMBuddy V1.0 直接把 Pi 作为 Agent substrate 是合理的；HMBuddy 应把工程重点放在 Tool 背后的 Office / Banking capability，而不是再建 Agent runtime。**

本轮 R 对后续 L/P 的校准：

1. 不把 AgentSession 和 AgentLoop 混为一谈；
2. structuredContent 配 outputSchema；
3. registered / active / callable Tool 分开；
4. deterministic test 与真实模型自主选择分开；
5. agent_settled 作为完整 run 的重要边界；
6. Pi runtime seam 不是银行安全边界。
