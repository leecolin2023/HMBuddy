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

# 6. D — Deep Read：Narrative Spine + Progressive Disclosure + Mechanism Depth + Cognitive Continuity

D 的任务不是“把源码讲一遍”，而是：

> **让一个没读过源码的人沿一条因果主线理解系统为什么一步步长成现在这样；每一步只引出解决当前问题所必需的最小机制；每个机制下钻到接近需求规格说明书的粒度；同时在长篇阅读中保持术语、已知前提和抽象层级的连续性。**

Deep Read 同时受四条规则约束。

```text
1. Narrative Spine
问题
→ 最小解决
→ 新问题
→ 新机制
→ 最终架构自然出现
```

```text
2. Progressive Disclosure
当前问题
→ 只引出当前必需机制
→ 先讲清
→ 再暴露下一问题
→ 后续概念才允许登场
```

```text
3. Mechanism Depth
为什么存在
→ Trigger
→ Input
→ Responsibility
→ State
→ Output
→ Collaboration
→ Failure / Boundary
→ Source Anchor
```

```text
4. Cognitive Continuity
当前读者已经知道什么
→ Canonical Term 是什么
→ 距离上次出现是否过远
→ 是否需要 Re-entry Bridge
→ 是否发生 Pi→HMBuddy / Abstract→Concrete 等层级切换
→ 是否需要 Transition Bridge
```

四者缺一不可。

---

## A. Narrative Spine：章节顺序必须由问题推动

正文不能优先按源码目录、类定义、方法列表或 API 顺序展开。

必须恢复一条因果链：

```text
原始矛盾是什么？
↓
最简单方案解决了什么？
↓
它留下了什么新问题？
↓
哪个机制因此必须出现？
↓
这个机制解决后，又留下什么问题？
```

每一主要章节都必须回答：

> **为什么读者此刻必须进入下一章？**

如果下一章只是因为“源码里下一个文件叫这个名字”，Narrative Gate 失败。

---

## B. Problem before abstraction

第一次出现一个概念时，先让读者看见具体矛盾，再给概念命名。

不要先写：

```text
AgentSession 是……
SessionManager 是……
Compaction 是……
```

而应先写出：

```text
一次 run 已经能 Tool Calling，
但第二轮继续追问时，上一轮状态由谁负责？

完整工作历史越来越长，
模型 Context 装不下怎么办？
```

机制应该是问题逼出来的结果。

---

## C. Progressive Disclosure Gate：一次只引出一个认知层

每个“新问题”只能引出解决该问题所必需的最小机制。

例如当前问题只是：

> 模型已经输出 `read_office_file(path=...)`，怎样真正执行？

此时可以引出：

```text
Tool lookup
参数校验
执行前 policy
Tool execute
结果规范化
```

但不能提前引出：

```text
AgentLoop
AgentSession
Compaction
Retry
```

这些必须等后续问题自然出现。

### C.1 不允许用未来概念解释当前概念

如果一个概念还没有被推导出来，不能把它当当前解释的前提。

### C.2 Source Location 不等于 Cognitive Order

多个机制写在同一源码文件，不代表文章里应该同时讲。

例如 `agent-loop.ts` 中同时有：

- Tool preparation；
- Tool execution；
- Tool Result creation；
- loop continuation。

正文仍应按：

```text
一次 Tool 怎样执行
↓
Result 为什么回模型
↓
为什么形成 Loop
```

逐层展开。

### C.3 每节结尾只留下清楚的下一问

如果一节结尾一次抛出多个跨层问题，说明 Progressive Disclosure 失败。

---

## D. Mechanism Depth：禁止裸机制名

只要一个机制对主线成立是必要的，就不能只出现名字或一句定义。

内部调查至少覆盖：

| 维度 | 必须弄清 |
|---|---|
| Purpose | 它解决哪个具体问题 |
| Trigger | 什么条件进入它 |
| Input | 接收哪些对象 / 状态 |
| Responsibility | 内部真正负责什么 |
| State | 读取、维护、改变什么 |
| Output | 向后续产生什么 |
| Collaboration | 上下游分别是谁 |
| Failure / Boundary | 没有它或失败会怎样 |
| Source Anchor | 源码 / checked test / docs 在哪里 |

这是作者内部调查清单，不是正文固定模板。

---

## E. Cognitive Continuity Gate：长文章必须管理“读者已经知道什么”

长文章不能只保证相邻两节连贯。

作者必须显式维护一个内部 **Concept Ledger**：

```text
概念 / Canonical Term
第一次建立的位置
当前定义
与相邻概念的关系
最后一次出现的位置
是否需要重新进入
当前是否允许使用
```

### E.1 Canonical Term Rule：一个概念一个稳定名称

关键概念第一次建立后，必须选定 canonical term。

例如：

```text
Work History
= SessionManager 保存的完整、可追溯工作记录

Current Model Context
= 当前一次模型请求真正看到的上下文

Session Tree
= append-only entries 组成的分支结构
```

后文不能为了语言变化，随意把同一对象改写成：

```text
Session history
conversation history
full history
historical state
```

除非明确说明：

> “这里的 Session history 指前文定义的 Work History。”

默认应直接继续使用 canonical term。

### E.2 No Synonym Drift

如果两个词代表同一对象，必须选一个主名称。

如果两个词不完全相同，必须显式说明差异。

禁止让读者自己判断：

```text
Work History
Session History
Session Tree
Current Branch
Messages
Context
```

到底是不是一回事。

### E.3 Re-entry Bridge：旧概念隔得太远时必须重新接回

如果一个关键概念距离上次正式解释已经跨越多个章节，重新使用前先用 1–3 句恢复它在当前论证中的角色。

例如 Compaction 不能直接写：

> “Compaction 为什么要进入 Session history？”

应先写：

> 前面讲 SessionManager 时，我们建立了两个稳定概念：  
> **Work History** 是完整工作记录；  
> **Current Model Context** 是当前请求真正送给模型的内容。  
> Compaction 现在要解决的，就是两者长度开始失配的问题。

Re-entry Bridge 不重新讲整章，但必须让读者重新找到认知坐标。

### E.4 Reader-State Check：每章开头先检查前置知识

写新章节前内部检查：

```text
这一章依赖哪些旧概念？
它们是否已经正式建立？
读者最后一次见到它们在哪里？
是否可能已经失去上下文？
是否需要一句 re-entry？
```

如果某个前置概念从未建立，不能直接使用。

### E.5 Transition Bridge：跨抽象层级必须显式过桥

以下切换不能直接跳：

```text
Pi generic mechanism → HMBuddy concrete implementation
Abstract principle → code / project mapping
Runtime internals → Product UX
Mechanism → Architecture ownership decision
```

每次切换至少回答：

```text
刚刚建立了什么通用结论？
↓
它留下了哪个扩展位置 / 决策位置？
↓
当前项目为什么恰好要在这里接入？
```

例如从 Pi Extension 切到 HMBuddy：

```text
Extension 已解决：
产品如何在不修改 Pi runtime 的前提下加入领域能力
↓
HMBuddy 的领域差异是什么：
Office / Banking capability
↓
因此第一个具体映射：
read_office_file
```

不能直接从“Extension lifecycle”跳到：

```text
HMBuddy 通过 registerTool 注册……
```

### E.6 Concept Reuse ≠ Concept Re-definition

旧概念重新出现时：

- 如果定义没变：只做 Re-entry；
- 如果作用范围扩大：说明“原定义 + 新增部分”；
- 如果当前只是举例：不要把例子写成新定义。

避免同一概念在文章后半段悄悄改变含义。

---

## F. 需求规格说明书级粒度

一个关键机制至少要达到：

```text
为什么需要
↓
什么时候进入
↓
输入是什么
↓
内部状态怎样变化
↓
输出是什么
↓
上下游如何配合
↓
失败会怎样
↓
源码 / test 在哪里
```

但正文仍按文章叙事组织。

---

## G. Locate real entry point，但不要让源码入口支配叙事

必须找到真实入口，例如：

```text
createAgentSession()
session.prompt()
pi.registerTool()
SessionManager.buildSessionContext()
runLoop()
```

入口是证据锚点，不是章节排序原则。

---

## H. Trace one real call chain

至少跟踪一条具体输入。

第一次出现某一步时，只展开当前已建立的概念。

完整链最终应覆盖：

```text
用户目标
→ Tool declaration
→ Tool Call
→ lookup / validation / permission / execute
→ Tool Result
→ Observation reinjection
→ next model request
→ AgentLoop stop
→ Session-level continuation / recovery
→ agent_settled
```

---

## I. Preserve cognitive engines

必须保留：

- 关键代码；
- 真实对象；
- 数据形态；
- 状态变化；
- 对比；
- 失败例子；
- checked test；
- 调用关系；
- 必要解释冗余。

可以删除语言重复，但不能删除理解桥梁。

---

## J. Explain choices carefully

源码 / docs / changelog 有证据时可以说明设计原因。

只有推断时，明确写：

> 从当前实现可以推断……

---

## K. Abstract last

只有具体问题、真实路径、关键机制和长期概念关系都已经建立后，才形成：

- 概念定义；
- ownership；
- 不变量；
- 边界；
- mental model。

---

# 7. D Acceptance Gate

D 只有同时通过四类 Gate 才完成。

## 7.1 Narrative Gate

1. 原始矛盾是什么？
2. 每个主要机制为什么在那个位置出现？
3. 上一节留下什么问题，逼出下一节？
4. 调换章节后，因果链是否会断？
5. 最终架构是否像被问题推导出来？

## 7.2 Progressive Disclosure Gate

1. 当前章节只解决哪个问题？
2. 本节新概念是否都是当前必需？
3. 是否提前使用未来概念？
4. 是否因为源码同文件而混讲多个认知层？
5. 结尾是否留下一个主要下一问？
6. 删除未来术语后，本节是否仍成立？

## 7.3 Mechanism Depth Gate

对每个关键机制，读者能否说明：

1. Purpose；
2. Trigger；
3. Input；
4. Responsibility；
5. State；
6. Output；
7. Collaboration；
8. Failure / Boundary；
9. Source Anchor。

## 7.4 Cognitive Continuity Gate

逐章检查：

1. 本章使用的每个关键术语是否已经正式建立？
2. 是否坚持 canonical term，而没有 synonym drift？
3. 如果旧概念相隔较远，是否提供 Re-entry Bridge？
4. 是否把 Work History、Session Tree、Current Branch、Messages、Current Model Context 等不同层次混成一个词？
5. 是否发生 Pi→HMBuddy、Abstract→Concrete、Runtime→Product 等层级切换？
6. 如果发生，是否有 Transition Bridge？
7. 旧概念重新出现时，定义是否保持稳定？
8. 读者是否需要翻回很多页才能知道“这里说的这个词是什么”？

如果读者在后半程遇到一个看似熟悉但无法定位含义的词，Cognitive Continuity Gate 失败。

## 7.5 Whole-article Gate

读者还应能：

- 跟踪完整调用链；
- 指出关键状态变化；
- 区分相邻概念；
- 区分 Source fact / Derived explanation / HMBuddy decision；
- 对相邻条件变化做预测；
- 反向解释为什么 Pi 最终需要这些层；
- 不需要依赖作者脑中的隐含词义映射。

任何关键步骤仍需自行脑补，D 继续展开。

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
