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

# 6. D — Deep Read：技术文章，而不是源码摘要

D 的任务：

> **让一个没读过源码的人理解：这个设计到底解决什么问题，它真实如何运行，为什么会这样组织。**

内部执行顺序：

## A. Problem before abstraction

先找概念存在前的真实问题：

- 没有它时系统怎么工作？
- 哪个负担或失败模式逼出了它？
- 为什么简单做法不够？

不要从术语定义开始。

## B. Locate the real entry point

找到真实入口，例如：

~~~text
createAgentSession()
session.prompt()
pi.registerTool()
OfficeBridgeClient.read()
~~~

回答：

- 谁调用它；
- 创建了什么；
- 谁拥有状态；
- 下一步进入哪里。

## C. Trace one real call chain

至少跟踪一条具体输入：

~~~text
用户输入了什么
session 收到了什么
模型请求里有哪些 tools
模型返回了什么结构
哪个函数识别 toolCall
哪个函数执行
toolResult 放进哪里
为什么模型会再跑一轮
什么条件下停止
~~~

## D. Preserve cognitive engines

必须保留真正承担理解功能的：

- 关键代码片段；
- 真实对象；
- 对比；
- 失败例子；
- 调用关系；
- 状态变化；
- 有证据的历史演变；
- 必要解释冗余。

## E. Explain choices carefully

源码 / docs / changelog 有证据时可以说明设计原因。只有推断时，必须明确写“从当前实现可以推断”。

## F. Abstract last

只有具体对象和调用链已经看懂，才形成概念定义、ownership、边界和 mental model。

---

# 7. D Acceptance Gate

D 只有在陌生读者能够回答以下问题时才完成：

1. 为什么这个概念存在？
2. 没有它时会发生什么？
3. 真实入口函数 / 模块在哪里？
4. 能否跟踪一个具体输入走完主要调用链？
5. 能否指出关键状态在哪里改变？
6. 能否解释相邻概念的职责边界？
7. 哪些结论来自源码，哪些是解释或项目选择？
8. 把概念名遮掉后，能否仍用自己的话说明它解决什么问题？

任何关键问题仍需读者自行脑补，D 继续展开。

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
