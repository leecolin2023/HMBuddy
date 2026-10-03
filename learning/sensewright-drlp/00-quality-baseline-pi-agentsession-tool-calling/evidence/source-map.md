# Evidence Source Map — Pi AgentSession / Tool Calling

本文件只记录样板使用的事实来源，防止 D/L/P 把“解释”与“源码事实”混在一起。

## Pi source pin

~~~text
repository: earendil-works/pi
commit: 4c6fb7cfe8c538a668726f6f8b3554098c39faee
package: @earendil-works/pi-coding-agent 1.0.0
~~~

## Primary source

### Session composition

packages/coding-agent/src/core/sdk.ts

建立以下事实：

- createAgentSession() 是 SDK composition entry；
- 默认组合 ModelRuntime / SettingsManager / SessionManager / ResourceLoader；
- 创建底层 Agent；
- 再创建 AgentSession；
- 可显式传 SessionManager.inMemory()；
- tools / noTools / excludeTools / customTools 控制工具集合。

### Session orchestration

packages/coding-agent/src/core/agent-session.ts

建立：

- AgentSession 拥有 agent、sessionManager、settingsManager 等 runtime state；
- prompt() 会处理扩展命令、输入 handler、模板/skill、streaming queue；
- 真正发起 run 前验证 model / auth；
- 将用户输入构造成 AgentMessage；
- getActiveToolNames() 返回当前声明给模型的 active tools；
- getLastAssistantText() 读取最终 assistant text；
- dispose() 负责释放 session 资源。

### Low-level Agent

packages/agent/src/agent.ts

建立：

- Agent 承担底层 prompt / run；
- AgentSession 不是 AgentLoop 本身；
- coding-agent package 在 Agent core 外叠加 session、resource、extension、compaction 等能力。

### Agent loop

packages/agent/src/agent-loop.ts

源码明确执行：

~~~text
stream assistant response
→ filter message.content for toolCall
→ executeToolCalls(...)
→ append ToolResultMessage into currentContext.messages
→ because hasMoreToolCalls = true, loop requests model again
→ no tool calls / no queued work
→ agent_end
~~~

这建立了：

> Tool Result 不是最终输出；它进入下一轮 context，模型基于 Observation 继续决策。

### Extension Tool contract

packages/coding-agent/src/core/extensions/types.ts

建立：

- ToolDefinition 需要 name / label / description / parameters / execute；
- direct tool 默认声明给模型；
- outputSchema 与 structuredContent 是 programmatic structured result 的正式契约；
- annotations 可以声明 readOnly / destructive / idempotent / openWorld hints；
- execute() 是 Pi runtime 调用 action implementation 的边界。

## Official docs / examples

- packages/coding-agent/docs/sdk.md
- packages/coding-agent/docs/extensions.md
- packages/coding-agent/examples/sdk/05-tools.ts
- packages/coding-agent/examples/sdk/06-extensions.ts

用途：核对 public contract，不把 private implementation 当 HMBuddy integration contract。

## Checked execution evidence

packages/coding-agent/test/suite/agent-session-tool-orchestration.test.ts

该测试使用 Pi 自己的 harness 和 deterministic assistant responses：

1. Extension 注册 run_tools / echo / helper；
2. 第一次 assistant response 确定性地产生 run_tools tool call；
3. Pi 执行 Tool；
4. Tool Result 被写入 session messages；
5. 第二次 assistant response 返回 done；
6. 测试断言 active/callable tools、tool call relationship、tool result 与 persistence。

L 的 Run Once 以这个 checked test 为真实执行证据，不虚构 live model trace。

## HMBuddy sources

- requirements/hmbuddy-architecture-baseline.md
- requirements/vnext-01-pi-native-bootstrap-integration-spike-v0.1.md

它们只建立 HMBuddy 自己的目标与 ownership：

~~~text
Pi owns Agent runtime
HMBuddy owns Office capability
~~~

以及 VNext-01：

~~~text
Pi AgentSession
→ read_office_file
→ TS Office Bridge
→ Python DOCX reader
→ Tool Result
→ final answer
~~~

## Source / Derived / Decision 示例

**Source fact：** Pi loop 在 assistant message 中找 toolCall，执行后把 tool result 加入 current context，再继续 loop。

**Derived explanation：** “Tool Result 是 Agent 的 Observation。”这是对源码行为的认知压缩，不是源码类名。

**HMBuddy decision：**

~~~text
TypeScript host
Python Office Runtime
one-shot subprocess
JSONL
10s timeout
MAX_MODEL_CHARS=20000
~~~

这些不是 Pi 原理，是 HMBuddy VNext-01 的工程选择。
