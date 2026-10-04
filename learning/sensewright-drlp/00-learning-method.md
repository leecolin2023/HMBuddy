# HMBuddy × SenseWright Technical Learning Protocol V1.0

**文档性质：** Canonical Learning Protocol  
**版本：** V1.0  
**状态：** Active  
**生效日期：** 2026-10-03  
**替代：** HMBuddy × SenseWright D → R → L → P 学习协议 V0.2  
**架构基线：** HMBuddy Architecture Baseline V1.0 — Pi-native Banking Office Agent

---

# 1. 为什么需要 V1.0

V0.2 的主要失败不是 D / R / L / P 方法本身错误，而是执行目标被替换成了“把所有概念快速生成一套结构齐全的四路文档”。

结果是大量内容退化为：

- 概念卡片；
- 架构速查表；
- bullet summary；
- 工程 TODO；
- 给熟悉项目的人看的 reminder。

它们没有承担“教会一个陌生人”的任务。

SenseWright 原方法要求：

> **删除语言冗余，不删除理解过程。**

因此 V1.0 把优化目标从“文档是否齐全”改成：

> **一个陌生读者是否已经形成可运行、可解释、可预测、可实施的 mental model。**

---

# 2. Highest Principle

本协议没有：

- 最低篇幅；
- 最高篇幅；
- 固定章节数；
- 固定文件长度；
- 每个概念必须使用同样模板的要求。

唯一完成条件：

> **An unfamiliar reader can explain the concept, trace one real execution, predict one nearby variation, and begin a real implementation without reconstructing missing steps.**

中文定义：

> **一个概念只有在陌生读者能够解释它、跟踪一次真实运行、预测一个相邻条件变化，并能够开始真实实施，而不需要自行脑补关键步骤时，才算完成。**

篇幅只是理解复杂度的结果，不是质量目标。

---

# 3. 陌生读者是谁

默认读者：

- 会基本编程；
- 理解函数、API、JSON、进程、测试等通用工程概念；
- 知道 LLM / Agent 的最基本含义；
- 没有读过 Pi 源码；
- 不了解 HMBuddy 当前架构；
- 不知道当前概念为什么存在、由谁拥有、运行时怎样工作。

因此不能把以下句子当成“已经解释”：

~~~text
SessionManager is authoritative.
Tool Result goes back to Context.
Extension registers tools.
Artifact is the IR.
~~~

这些只是结论。

学习材料必须继续回答：

~~~text
为什么需要这个东西？
没有它会怎样？
真实入口在哪里？
一个输入进来后每一步发生什么？
状态在哪里改变？
为什么下一步能够继续？
它和相邻概念有什么区别？
条件变化后哪些结论还成立？
真正打开 IDE 后第一步做什么？
~~~

---

# 4. Evidence First

HMBuddy 已切换为 Pi-native 架构，因此通用 Agent 概念必须优先读取 Pi 的真实实现，而不是从 HMBuddy 旧设计反推。

## 4.1 Pi-owned concept

~~~text
Pi pinned source / checked tests
        ↓
Pi official docs / checked examples
        ↓
HMBuddy Architecture / Requirement
        ↓
Derived explanation
~~~

## 4.2 HMBuddy-owned Office concept

~~~text
HMBuddy current code / tests / fixtures
        ↓
Canonical Architecture / Requirement
        ↓
Legacy algorithm as reference only
        ↓
Derived explanation
~~~

## 4.3 Source / Derived / Decision 必须分开

**Source fact**：源码、测试、官方文档直接建立的事实。  
**Derived explanation**：为了让人理解，对事实做的机制解释、类比、抽象。  
**HMBuddy decision**：HMBuddy 自己选择的实现，例如 Python subprocess、JSONL、10s timeout。

禁止：

- 把推断写成作者动机；
- 把 HMBuddy 选择写成 Pi 原理；
- 把 Future architecture 写成 current capability；
- 把 Legacy contract 写成 VNext contract。

---

# 5. D / R / L / P 的新职责

~~~text
Raw Source
   │
   ├── D：恢复“为什么存在 + 真实怎么工作”，写成人能读懂的技术文章
   │
   └── R：重新读 Raw Source，独立检查正确性、边界、风险与隐含假设
              │
              ▼
       L：让机制真的跑起来
          输入 / 状态 / 数据 / 控制流 / 输出
          + 为什么每一步存在
          + 一个高信息量变化
              │
              ▼
       P：把已理解的机制落进真实工程
          建文件 / 写接口 / 跑测试 / 看 trace
          + 制造失败 / 排错
          + 区分原理与项目选择
~~~

D、R、L、P 可以长度完全不同。

---

# 6. D — Deep Read：Narrative Spine + Progressive Disclosure + Mechanism Depth

D 的任务不是“把源码讲一遍”，而是：

> **让一个没读过源码的人沿着一条因果主线，理解一个设计为什么一步步长成现在这样；同时，每一步只引出解决当前问题所必需的最小机制，并把这个机制下钻到接近需求规格说明书的粒度。**

Deep Read 同时受三条规则约束：

```text
横轴：Narrative Spine

问题
→ 第一个最小解决
→ 新问题
→ 新机制
→ 新问题
→ 新机制
→ 最终架构自然出现
```

```text
时序：Progressive Disclosure

当前问题
→ 只引出解决当前问题的最小机制
→ 先把它讲清
→ 再暴露它留下的新问题
→ 后续机制才允许登场
```

```text
纵轴：Mechanism Depth

为什么存在
→ 什么时候触发
→ 接收什么
→ 内部负责什么
→ 改变什么状态
→ 产出什么
→ 与谁协作
→ 失败或缺失会怎样
→ 真实源码 / test 锚点
```

三者缺一不可。

只有 Narrative Spine，没有 Mechanism Depth，会变成“故事讲得顺，但每个机制只是点名”。

只有 Mechanism Depth，没有 Narrative Spine，会退化成 API 手册。

有 Narrative Spine 和 Mechanism Depth，但没有 Progressive Disclosure，则会出现另一种失败：

> 当前问题还没有讲清，就提前泄露 AgentLoop、Session、Retry、Policy 等后续概念，导致读者需要同时记住多层尚未建立的抽象。

## A. Narrative Spine：章节顺序必须由问题推动

正文不能优先按源码目录、类定义、方法列表或 API 顺序展开。

必须恢复一条认知因果链：

```text
原始矛盾是什么？
↓
最简单的方案能解决什么？
↓
它留下了什么新问题？
↓
哪个机制因此必须出现？
↓
这个机制又暴露了什么新问题？
↓
下一个机制为什么自然出现？
```

章节之间必须能够回答：

> **为什么读者此刻必须进入下一章？**

如果下一章只是因为“源码里下一个文件叫这个名字”，Narrative Gate 失败。

## B. Problem before abstraction

第一次出现一个概念时，先解释它被什么问题逼出来。

不要先写：

```text
AgentSession 是……
SessionManager 是……
Compaction 是……
```

而应先让读者看见具体矛盾，再让机制登场。

## C. Progressive Disclosure Gate：一次只引出一个认知层

每一个“新问题”只能引出解决该问题所必需的最小机制。

例如当前问题只是：

> 模型已经输出 `read_office_file(path=...)`，怎样真正执行？

这一阶段可以引出：

```text
Tool lookup
参数校验
执行前 policy
Tool execute
结果规范化
```

因为它们都属于“把 Action Intent 变成一次受控执行”。

但此时**不应该提前引出**：

```text
AgentLoop
AgentSession
Compaction
Retry
```

这些必须等到新的问题真正出现，例如：

```text
Tool Result 已经拿到了，为什么还不能结束？
↓
Observation

Observation 已经回来了，谁负责再跑一轮？
↓
AgentLoop

一次 AgentLoop 能工作，但长期会话怎么办？
↓
AgentSession / SessionManager
```

### C.1 不允许用未来概念解释当前概念

如果一个概念在叙事上尚未被推导出来，就不能把它当成当前解释的前提。

不推荐：

```text
真实 AgentLoop 会先验证 Tool……
```

如果读者此时尚不知道为什么需要 AgentLoop。

更好的写法：

```text
程序现在需要一个受控执行层：
先找到 Tool，再校验参数，再决定是否允许执行。
在 Pi 当前实现中，这些逻辑位于 agent-loop.ts 的 Tool execution 路径。
```

先建立机制，再映射源码归属。

### C.2 Source Location 不等于 Cognitive Order

多个机制可以恰好写在同一个源码文件里，但不代表它们应在文章里同时登场。

例如 `agent-loop.ts` 同时包含：

- Tool preparation；
- Tool execution；
- Tool Result creation；
- loop continuation。

正文仍应按认知顺序拆开：

```text
先理解一次 Tool 怎样执行
↓
再理解 Result 为什么回模型
↓
最后理解为什么形成 Loop
```

代码模块边界不能覆盖认知边界。

### C.3 每一节结尾必须显式留下“唯一下一问”

每一主要章节结束时，至少要有一个自然的未解决问题，把读者带入下一章。

如果一节结尾同时抛出三到五个跨层问题，说明 Progressive Disclosure 失败。

## D. Mechanism Depth：禁止“裸机制名”

只要一个概念或机制对主线成立是必要的，就不能只出现名字或一句定义。

内部调查至少覆盖：

| 维度 | 必须弄清 |
|---|---|
| Purpose | 它具体解决哪个问题 |
| Trigger | 什么条件下进入它 |
| Input | 它接收哪些对象 / 状态 |
| Responsibility | 它内部真正负责什么 |
| State | 它读取、维护、修改什么状态 |
| Output | 它向后续产生什么 |
| Collaboration | 它的上下游分别是谁 |
| Failure / Boundary | 没有它、失败或越界时会怎样 |
| Source Anchor | 源码 / checked test / docs 在哪里 |

这是作者内部调查清单，不是固定正文模板。

最终文章仍然按 Narrative Spine 自然叙述。

## E. 需求规格说明书级粒度

“讲清一个机制”至少应达到：

```text
为什么需要
↓
何时进入
↓
输入是什么
↓
内部状态如何变化
↓
输出是什么
↓
上下游如何配合
↓
失败会怎样
↓
源码 / test 在哪里
```

而不是：

```text
AgentSession 还负责 queue、compaction、retry。
```

## F. Locate real entry point，但不要让入口支配叙事

必须找到真实入口，例如：

```text
createAgentSession()
session.prompt()
pi.registerTool()
SessionManager.buildSessionContext()
runLoop()
```

但入口只是证据锚点，不是章节排序原则。

## G. Trace one real call chain

至少跟踪一条具体输入，但仍然服从 Progressive Disclosure。

第一次出现某一步时，只展开当前已建立的概念；不能在第一遍调用链里提前塞满所有未来术语。

完整链最终应覆盖：

```text
用户目标
→ Tool declaration
→ Tool Call
→ Tool lookup / validation / permission / execute
→ Tool Result
→ Result reinjection
→ next model request
→ AgentLoop stop
→ Session-level continuation / recovery
→ agent_settled
```

## H. Preserve cognitive engines

必须保留关键代码、真实对象、数据形态、状态变化、对比、失败例子、调用关系、checked test、有证据的历史演变和必要解释冗余。

Deep Read 可以删除语言重复，但不能删除“为什么下一步成立”的桥梁。

## I. Explain choices carefully

源码 / docs / changelog 有证据时可以说明设计原因。

只有推断时，必须明确写：

> 从当前实现可以推断……

## J. Abstract last

只有具体问题、运行路径、关键机制都已经看懂后，才形成概念定义、ownership、不变量、边界和 mental model。

抽象是已理解事实的压缩，不是解释的起点。

---

# 7. D Acceptance Gate

D 只有同时通过 Narrative、Progressive Disclosure、Mechanism Depth 三类 Gate 才完成。

## 7.1 Narrative Gate

陌生读者应能回答：

1. 文章最开始的原始矛盾是什么？
2. 每个主要机制为什么在那个位置出现？
3. 上一节留下了什么问题，逼出了下一节？
4. 如果交换两个主要章节，因果链是否会断？
5. 最终架构是否像被问题一步步推导出来，而不是作者一次性宣布？

## 7.2 Progressive Disclosure Gate

逐节检查：

1. 当前章节到底只解决哪个问题？
2. 本节引入的每个新概念是否都是解决当前问题所必需？
3. 是否提前使用了尚未推导出来的概念解释当前机制？
4. 是否因为源码同文件，就把多个认知层一起讲了？
5. 本节结尾是否留下一个清楚、自然的“下一问”？
6. 如果删除提前泄露的后续术语，当前章节是否仍能完整成立？

如果读者需要先理解后面三章，才能理解当前章节，Progressive Disclosure Gate 失败。

## 7.3 Mechanism Depth Gate

对正文中每一个关键机制，陌生读者至少应能说明：

1. 它为什么存在？
2. 什么条件触发它？
3. 它接收什么输入或前置状态？
4. 它具体承担哪些职责？
5. 它改变或维护什么状态？
6. 它向后续输出什么？
7. 它与上下游分别怎么协作？
8. 没有它或失败时具体会坏在哪里？
9. 真实源码 / test / docs 锚点在哪里？

如果正文只留下机制名，D 未完成。

## 7.4 Whole-article Gate

读者还应能：

- 跟踪具体输入走完主要调用链；
- 指出关键状态在哪里变化；
- 区分相邻概念；
- 区分 Source fact / Derived explanation / HMBuddy decision；
- 对相邻条件变化做出有依据的预测；
- 在读完整篇后，能够反向解释“为什么 Pi 最终需要这些层”，而不是只能背模块名称。

任何关键步骤仍需读者自行脑补，D 继续展开。

---
# 8. R — Review：独立审阅

R 重新读取 Raw Source，D 只能导航，不能当证据。

R 回答：

> **当前设计 / 理解是否站得住？什么地方会让后续实现、学习或决策出错？**

重点检查：

- ownership 是否读错；
- public contract 与 private implementation 是否混淆；
- current / future 是否混淆；
- Session / Tool / Extension 等边界是否被过度简化；
- 是否存在改变 HMBuddy 架构的真实限制；
- 是否遗漏安全、生命周期、错误语义；
- HMBuddy 是否正在重新实现 Pi 已经拥有的能力。

R 报告只展开 materially 改变理解或行动的发现。

---

# 9. L — Learning：从流程复述变成机制实验

对于 Agent / Runtime / RAG / Database / Office Pipeline 等机制型知识，L 必须让机制真正跑一次。

## 9.1 Real input first

选择具体输入，不能写“用户提出请求”。

## 9.2 Executable Trace

至少展示真正决定机制的状态：

~~~text
输入
→ session / context
→ model request
→ model response / toolCall
→ tool execution
→ toolResult / observation
→ next model request
→ final answer / stop
~~~

每一步回答：

- 收到什么；
- 做了什么；
- 哪个状态改变；
- 产生什么；
- 为什么下一步能够继续。

## 9.3 Explain after the run

跑完再逐步问：

- 为什么必须有这一步？
- 它解决上一阶段留下的什么问题？
- 删除它会具体坏在哪里？

## 9.4 One high-information variation

改变一个真正影响行为的条件，例如：

- Tool 被移出 active set；
- Tool description 变模糊；
- Session history 丢失；
- Tool Result 被截断；
- subprocess 超时；
- Context 超限；
- 文件路径越界。

优先真实运行。当前环境不能运行时，必须使用已有真实 test / trace 作为证据，或明确标记 Pending，不得伪造结果。

## 9.5 Mental model last

只有运行与 variation 都看懂后，才压缩成可迁移 mental model。

---

# 10. L Acceptance Gate

陌生读者应能：

1. 复述一个真实输入如何跑完整条机制；
2. 指出主要状态 / 数据 / 控制流变化；
3. 解释关键步骤为什么存在；
4. 预测至少一个相邻条件变化；
5. 区分“模型决定”“Pi runtime 决定”“HMBuddy tool 决定”；
6. 不靠背流程图也能解释为什么下一步发生。

如果只能记住 Model → Tool → Observation → Model，L 没有完成。

---

# 11. P — Practice：必须落到真实工程

P 的任务是从“我理解它了”走到“我打开 IDE 知道第一步做什么，而且知道怎么证明做对”。

## 11.1 优先进入 HMBuddy VNext

对于 Pi-native 概念，Practice 优先选择当前 HMBuddy VNext 的真实需求，不为学习另造无关 Framework。

## 11.2 Real engineering artifacts

根据场景真实创建或明确指向：

- 文件；
- 模块；
- interface / schema；
- fixture；
- test；
- command；
- trace；
- compatibility record。

不能停在“实现 Tool、增加测试、记录日志”。

## 11.3 Run a real path

至少一个 concrete input 从入口跑到最终输出。

如果当前环境无法执行：

- 可以引用上游 checked test 作为 mechanism evidence；
- HMBuddy 尚未运行的部分必须标记 Pending；
- 不把“可执行设计”写成“已验证实现”。

## 11.4 Manufacture one failure

至少主动制造一个高信息量失败，并展示：

~~~text
现象
→ 首先检查哪里
→ 根因
→ 修复
→ 如何证明修复有效
~~~

## 11.5 Principle vs Project Choice

最后必须拆开：

**Upstream / Concept principle**  
**HMBuddy implementation choice**

这样才形成可迁移能力。

---

# 12. P Acceptance Gate

P 只有在读者能够回答以下问题时完成：

1. 真正应该创建哪些工程对象？
2. 第一步具体做什么？
3. 接口 / schema 是什么？
4. 一个输入如何跑完整条实现？
5. 用什么测试证明成功？
6. 最有价值的失败如何复现和定位？
7. 哪些行为来自 Pi，哪些来自 HMBuddy？
8. 换 Office 格式 / Provider / UI 后，哪些部分仍成立？

如果仍然是“原理懂了，但打开 IDE 不知道干什么”，Practice 未完成。

---

# 13. Status Semantics

文档存在不等于学习完成。

每个概念可以标记：

~~~text
DRAFT
SOURCE-GROUNDED
MECHANISM-VALIDATED
PRACTICE-VALIDATED
QUALITY-BASELINE
~~~

- DRAFT：正在形成；
- SOURCE-GROUNDED：D/R 通过 source gate；
- MECHANISM-VALIDATED：L 有真实 execution evidence；
- PRACTICE-VALIDATED：P 有真实工程执行 / 测试 / failure evidence；
- QUALITY-BASELINE：四阶段均达到陌生人可理解标准，可作为样板。

如果 HMBuddy 实现尚未运行，P 可以 Pending，不得提前标记 PRACTICE-VALIDATED。

---

# 14. 禁止批量生成

禁止：

~~~text
23 concepts × D/R/L/P
一次性批量完成
~~~

正确节奏：

~~~text
Concept A
→ D
→ R
→ L
→ P
→ Acceptance Gate
→ 修复
→ Quality Review
→ 再进入 Concept B
~~~

复杂概念耗时远高于简单概念是正常的。

---

# 15. First Quality Baseline

第一份样板固定为：

> **Pi AgentSession / Tool Calling Vertical Slice**

路径：

~~~text
learning/sensewright-drlp/00-quality-baseline-pi-agentsession-tool-calling/
~~~

样板通过前：

- 不重写旧 23 个概念；
- 不新建新的完整概念地图；
- 不以文件数量衡量学习进度。

后续概念必须至少达到同等：

- source grounding；
- human comprehensibility；
- execution visibility；
- mechanism depth；
- engineering specificity；
- epistemic honesty。

---

# 16. Current architecture rule

2026-10-03 起：

- Pi owns generic Agent runtime；
- HMBuddy owns Office / Banking domain；
- 旧 V0.2 SessionStore / AgentLoop / ToolRegistry / ExtensionHost 学习材料属于 Legacy；
- 学习这些概念时，应读 Pi 的真实实现，而不是继续设计 HMBuddy 自研版本。

Office Domain 仍由 HMBuddy 深入学习：

~~~text
DOCX / XLSX / PPTX / PDF
OCR / COM
Artifact / Locator
Patch / Version / Diff
Validation
Banking Skills
Governance
~~~

---

# 17. 最终原则

> **学习材料不是给已经懂的人做索引，而是替陌生读者承担理解成本。**

> **模板可以帮助执行 Skill，但不能替代真实解释。**

> **抽象必须来自已经跑通的对象；不能用抽象掩盖没有跑通。**

> **没有真实机制证据，不宣称“理解完成”；没有真实工程证据，不宣称“Practice 完成”。**

最终目标不是拥有最多学习文件，而是：

> **把 HMBuddy 变成一条可以沿真实 Pi / Office 工程逐层学会 Agent 开发的路径。**
