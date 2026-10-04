# HMBuddy × SenseWright Learning Orchestration Protocol V1.1

**文档性质：** Project Learning Orchestration Protocol  
**版本：** V1.1  
**状态：** Active  
**生效日期：** 2026-10-04  
**上游方法基线：** SenseWright V2.7.0  
**架构基线：** HMBuddy Architecture Baseline V1.0 — Pi-native Banking Office Agent  
**替代：** HMBuddy × SenseWright Technical Learning Protocol V1.0

---

# 1. 这份文件是什么

这份文件不是第五个 Skill，也不重新定义 Deep Read / Review / Learning / Practice。

它只负责一件事：

> **把 SenseWright 的四种认知模式，正确编排到 HMBuddy 的技术学习场景里。**

真正的方法定义仍然来自 SenseWright：

```text
D — Deep Read V6.4
R — Vibe Review V0.10
L — System Learning V0.5.3
P — Practice V0.2
```

因此本文件不应复制或覆盖 SenseWright Skill 的内部实现。

如果 HMBuddy 学习过程中发现新的质量问题，先判断：

1. 它是否能够映射回 SenseWright 已有的核心原则；
2. 它是否具有跨主题、跨技术、跨项目的普适性；
3. 它是否改变了认知任务本身，而不只是修复某一个案例的写作方式。

只有满足这些条件，才进入本协议。

否则：

> **把它留在具体 Quality Baseline / Regression Case 中，不升级成 Canonical Rule。**

---

# 2. 为什么要从 V1.0 再收敛

V1.0 解决了一个真实问题：

> 旧学习资料为了目录完整，批量生成了大量 D / R / L / P 文档，但很多结果只像概念卡片，不能真正帮助陌生人理解和实施。

后续围绕 `Pi AgentSession / Tool Calling Vertical Slice` 的多轮迭代，又发现了：

- 文章要有认知推进，而不是源码目录导览；
- 关键机制不能只点名；
- 新概念不能一次泄露过多；
- 长文章需要保持术语和上下文连续；
- 从通用机制映射到 HMBuddy 时需要明确过桥。

这些发现都有效。

但如果把每次修复直接固化成新的顶层 Gate，就会产生另一个问题：

> **方法越来越像“为这一篇 Pi 文章定制的写作规范”，而不是一个可以泛化到 RAG、数据库、Office Runtime、业务规则、系统架构等主题的学习协议。**

因此 V1.1 回到 SenseWright 的设计思想：

> **保持认知模式少而稳定；把具体技巧降回各 Skill 的执行策略与 Repair Pattern。**

---

# 3. SenseWright 是 Source of Truth

HMBuddy 不 fork SenseWright 的认知架构。

四个模式分别回答四个不同问题：

```text
D — 我理解原材料了吗？
R — 这份材料可靠吗、够用吗？
L — 我真正懂了吗？
P — 如果现在真的要把它做出来，我该怎么做？
```

它们的边界必须保持。

---

# 4. Context / Evidence Architecture

## 4.1 D / R：Source-facing，彼此隔离

Deep Read 与 Review 都直接读取 Raw Source。

```text
Raw Source
   ├─→ D
   └─→ R
```

规则：

- D 不读取 R / L / P 结果；
- R 不读取 D / L / P 结果；
- D 与 R 不互相继承结论；
- 两者都可以读取用户对当前任务的直接要求和必要原始上下文。

原因：

> Deep Read 要忠实恢复材料；Review 要独立判断材料。  
> 如果先读 sibling output，容易把别人的解释当成原文。

---

## 4.2 L / P：Knowledge-facing，可选择性引用

Learning 可以选择性参考 D / R / P。

Practice 可以选择性参考 D / R / L，其中 L 的 Knowledge Model 通常最重要。

统一遵守 SenseWright 三条规则：

> **Reference ≠ Evidence**  
> **Transform, don't copy**  
> **Selective, not mandatory**

已有输出可以帮助定位重点，但不能替代真实证据。

---

## 4.3 HMBuddy 的证据优先级

### Pi-owned concept

例如：

```text
AgentLoop
AgentSession
SessionManager
Tool lifecycle
Extension
Context / Compaction
Provider / Model runtime
```

优先级：

```text
Pi pinned source / checked tests
        ↓
Pi official docs / examples
        ↓
HMBuddy Architecture / Requirement
        ↓
Derived explanation
```

### HMBuddy-owned concept

例如：

```text
Office Artifact
DOCX / XLSX / PPTX / PDF
OCR
COM
Artifact Locator / Patch / Diff / Validation
Banking Skill
Bank Governance
```

优先级：

```text
HMBuddy current code / tests / fixtures
        ↓
HMBuddy Canonical Architecture / Requirement
        ↓
Legacy implementation as reference
        ↓
Derived explanation
```

### Mixed concept

如果一个主题跨 Pi 与 HMBuddy：

> 先分 Ownership，再分别取证。

不要用 HMBuddy 旧实现解释 Pi 原理，也不要把 Pi 通用机制当成 HMBuddy 领域实现。

---

## 4.4 Source / Derived / External 必须可区分

学习材料至少能区分：

**Source-supported**  
源码、测试、文档、原始材料直接建立。

**Derived synthesis**  
为了理解，对 source fact 做结构化解释、抽象或映射。

**External extension / Project choice**  
为了实施或补充，引入新的工程选择、外部事实或当前项目决策。

禁止：

- 把推断写成作者动机；
- 把 HMBuddy choice 写成 Pi invariant；
- 把 Future design 写成 Current capability；
- 把 Legacy behavior 写成 VNext contract。

---

# 5. Full Learning Track

当一个概念需要完整学习时，默认采用：

```text
Raw Source
   ├─────────────┐
   ▼             ▼
Deep Read       Review
   D             R
[isolated]     [isolated]
   │             │
   └──────┬──────┘
          │ optional references
          ▼
       Learning
          L
          │
          │ Knowledge Model
          ▼
       Practice
          P
          │
          │ Implementation Gap
          └──────────────→ Learning
```

注意：

> **D → R → L → P 是学习路径，不是信息继承链。**

D / R 仍然独立读取 Raw Source。

L 才可以选择性吸收 D / R。

P 主要把已经形成的 Knowledge Model 编译成 Engineering Model。

---

# 6. D — Deep Read：忠实恢复技术材料的认知结构

HMBuddy 不再为 Deep Read 维护一套平行方法。

直接继承 SenseWright Deep Read V6.4：

```text
Raw Source
→ Restore Cognitive Topology
→ Identify Cognitive Units / Engines
→ Choose Compression Contract
→ Deliverable
→ Acceptance Gate
→ Repair Loop
```

核心原则：

> **先恢复材料自己的认知结构，再决定哪些信息允许消失。**

> **删除语言冗余，不删除理解过程。**

---

## 6.1 Technical Source Profile

技术源码 / 架构材料有几个常见特征：

- 认知结构不一定等于目录结构；
- 真实设计逻辑可能分散在 source、test、docs、examples；
- 一个类名或方法名本身通常不足以帮助陌生人理解；
- 关键机制需要通过调用关系、状态变化、失败行为才能看清。

因此对技术材料执行 Deep Read 时，优先做三件事。

### A. Restore Cognitive Topology

恢复的是：

> **问题、机制、依赖、控制权、状态与边界之间的真实关系。**

而不是机械按：

```text
file A
→ class B
→ method C
```

讲解。

如果材料真实结构表现为：

```text
问题
→ 机制
→ 新约束
→ 下一机制
```

输出可以跟随这条认知推进。

如果材料本身是并列模块或多主题结构，也应保留多分支，不为了“故事感”强行制造单线叙事。

---

### B. Preserve Cognitive Engines

技术材料中的“认知发动机”可能是：

- 一个真实调用链；
- 一段决定控制权的代码；
- 一个关键状态转换；
- 一组 schema / contract；
- 一个 checked test；
- 一个失败案例；
- 一个前后设计对比；
- 一个能解释职责边界的例子。

判断是否保留，不看它是不是“源码细节”，而看：

> **删掉以后，陌生读者是否只剩结论，却不知道为什么成立、为什么需要、前后怎么接起来。**

如果是，就不能删。

---

### C. Preserve Comprehensibility

SenseWright 的要求不是“逻辑上能推出”就够。

还要：

> **陌生读者不需要自己补关键推理。**

在技术长文中，可能需要：

- 逐步引入概念；
- 稳定使用关键术语；
- 隔得很远时重新接回旧概念；
- 从抽象机制切到具体项目时解释为什么现在切换；
- 对关键机制补真实输入、状态和输出。

这些属于 **Comprehensibility Repair Patterns**。

它们不是固定章节，也不是每篇都必须机械执行。

只在输出出现理解断层时启用。

---

## 6.2 不再维护四套独立写作 Gate

V1.0 中的：

```text
Narrative Spine
Progressive Disclosure
Mechanism Depth
Cognitive Continuity
```

不再作为 HMBuddy 自己的四个一级 Canonical Gate。

它们被归并回 Deep Read 的核心合同：

```text
Narrative Spine
→ Restore Cognitive Topology

Mechanism Depth
→ Preserve Cognitive Engines + Comprehensibility

Progressive Disclosure
→ Preserve Cognitive Progression + Comprehensibility

Cognitive Continuity
→ Comprehensibility in long-form material
```

以后只有当具体 Deep Read 输出出现相应失败时，才把它们作为 Repair Lens 使用。

这样既保留这几轮验证有效的经验，又避免把一个 Quality Baseline 的局部写法变成全局模板。

---

## 6.3 D 的完成标准

D 是否完成，回到 SenseWright V6.4 的 Acceptance Gate：

- Structure：是否恢复了真实认知结构；
- Fidelity：是否忠实于材料；
- Comprehensibility：陌生读者能否跟上；
- Source Boundary：是否越过原材料边界；
- Coverage / Model Preservation：根据 Compression Contract 判断。

HMBuddy 不再额外要求固定：

- 章节数量；
- Narrative 格式；
- 每个机制九项字段；
- Concept Ledger；
- 固定结尾问题。

如果这些技巧能提高当前材料的理解质量，就使用；否则不强制。

---

# 7. R — Review：独立检查是否站得住

Review 直接继承 SenseWright V0.10：

```text
Atomize Source
→ Reconcile Coverage
→ Review Every Unit
→ Assess Materiality
→ Report Selectively
```

核心原则：

> **Coverage before judgment.**

> **Review comprehensively; report selectively.**

对技术材料，常见 Review focus 可以包括：

- ownership；
- public / private contract；
- current / future；
- data / state / lifecycle；
- failure mode；
- security boundary；
- compatibility；
- architecture drift；
- upstream duplication。

但这些只是 Triggered Lens。

不能预先拿一套固定 Checklist 去决定“哪些 source span 值得看”。

---

# 8. L — Learning：从 Source Understanding 到 Knowledge Model

Learning 不是 Deep Read 的加长版。

D 回答：

> 原材料到底在说什么？

L 回答：

> 我现在真正理解这个对象了吗？

通用主体仍然来自 SenseWright：

```text
Ground Object
→ Build Model
→ Find Gaps
→ Project to Use
```

对于 Agent、Runtime、RAG、Database、Office Pipeline 等机制型技术知识，优先启用：

```text
Ground
→ Run Once
→ Explain Mechanism
→ Vary One Condition
→ Compress Model
```

---

## 8.1 Ground before abstraction

先回答：

> 没有这个东西时真实怎么工作？  
> 引入以后哪一步真的变了？

如果用户反馈：

- 太抽象；
- 像生造的；
- 不知道有什么用；
- 不就是另一个 X；

不要继续增加 taxonomy。

回到真实对象和具体任务。

---

## 8.2 Run Once

技术机制能跑就不要只描述。

优先选择最小实例，让真正决定行为的：

- 输入；
- 中间表示；
- 状态；
- 数据流；
- 控制流；
- 资源；
- 动作；
- 输出；

变得可观察。

不要求每次全部展示。

---

## 8.3 Explain Mechanism

跑完后继续问：

> 为什么必须有这一步？  
> 它解决上一步留下的什么问题？  
> 跳过会怎样？

Learning 的目标不是流程记忆，而是形成因果模型。

---

## 8.4 Boundary Variation

当改变一个条件能带来明显认知增量时，只改变一个高信息量变量。

观察：

```text
Still holds
Weakens
Disappears / reverses
Becomes unanswerable
Reframes the object
```

这不是固定 Checklist。

只有当变化能帮助理解边界时才做。

---

## 8.5 L 的终点

> **形成一个能运行、能解释、能预测相邻变化的 mental model。**

已有 D / R 只能作为 Reference Context。

涉及事实、源码行为或原文表述时，仍回真实 source。

---

# 9. P — Practice：把 Knowledge Model 编译成 Engineering Model

Practice 直接继承 SenseWright V0.2：

```text
Knowledge Model
→ Ground Real Scenario
→ Build Engineering Model
→ Implement End-to-End
→ Run One Concrete Path
→ Verify
→ Troubleshoot
→ Operationalize
→ Generalize
```

中心问题：

> **如果现在真的要把它做出来，我该怎么做？**

---

## 9.1 Prefer Real HMBuddy Scenario

如果概念属于当前 HMBuddy VNext，应优先放进真实 VNext 场景。

但这是 HMBuddy 项目选择，不是 Practice 的通用定义。

如果用户真实任务不适合 HMBuddy 当前 VNext，就使用更合适的真实场景。

---

## 9.2 Engineering specificity follows the scenario

Practice 根据真实场景决定是否需要：

- 文件；
- 模块；
- schema；
- interface；
- fixture；
- command；
- test；
- trace；
- monitoring；
- deployment；
- rollback。

不维护固定工程产物清单。

原则仍然是：

> **任何阻碍实际执行的关键空白，都不能用概念性语言跳过。**

---

## 9.3 One concrete path

至少让一个真实输入走完整链路：

```text
Input
→ Processing
→ State Change
→ Intermediate Artifact
→ Output
```

然后回答：

> 我怎么知道它真的做对了？

建立真实 Feedback Loop。

---

## 9.4 Failure / Troubleshooting

选择最有信息价值的失败点。

不是为了考试，而是为了暴露 Engineering Model 的边界。

---

## 9.5 Generalize

最后区分：

**Concept / Upstream invariant**

与：

**Current project implementation choice**

这样用户学到的是可迁移工程模型，不是当前 Repo 的一次性代码。

---

# 10. Quality Baseline 的角色

`Pi AgentSession / Tool Calling Vertical Slice` 继续作为当前第一个 Quality Baseline。

但它的角色被重新定义为：

> **Regression Case，而不是 Protocol Generator。**

它用于验证：

- Deep Read 是否真的可理解；
- Learning 是否形成可运行机制模型；
- Practice 是否可实施；
- D / R / L / P 边界是否正确。

它不能反过来规定：

> 所有未来主题都必须使用与 Pi AgentSession 完全相同的章节、术语、Gate 或写法。

---

## 10.1 新规则进入 Canonical Protocol 的条件

从某个 Baseline / Case 中发现的规则，进入本协议前至少检查：

### SenseWright Alignment

它是否能映射到 SenseWright 已有核心原则？

### Domain Neutrality

把 `Pi / Tool / AgentSession / HMBuddy` 等专有名词拿掉以后，它是否仍成立？

### Cross-Case Value

换成 RAG、Database、Office Parsing、Workflow、业务制度等对象时，它是否仍能提高质量？

### Contract Level

它是在定义“认知任务必须做到什么”，还是只是在描述“这一篇文章最好怎么写”？

只有前者才进入 Canonical Protocol。

后者留在：

- Quality Baseline；
- Regression Note；
- Skill Repair Pattern；
- Case-specific guidance。

---

# 11. Completion / Status

本协议不再发明一套平行于 SenseWright 的复杂状态机。

每个阶段是否完成，优先由对应 Skill 自己的 Acceptance Gate 决定。

HMBuddy 只保留几个跨阶段状态用于学习地图：

```text
DRAFT
SOURCE-UNDERSTOOD
KNOWLEDGE-MODELED
ENGINEERING-TRANSFERRED
QUALITY-BASELINE
```

含义：

**DRAFT**  
当前概念仍在处理中。

**SOURCE-UNDERSTOOD**  
D / R 已完成当前 source-facing 工作；不表示用户已经真正形成 Knowledge Model。

**KNOWLEDGE-MODELED**  
L 已形成可解释、可运行、可预测边界的 Knowledge Model。

**ENGINEERING-TRANSFERRED**  
P 已把 Knowledge Model 落进真实工程路径，并具有执行、验证、排错能力。

**QUALITY-BASELINE**  
该 Case 同时达到当前 D / R / L / P 的高质量要求，可用于回归检查。

如果 Practice 只是写了方案但没有真实执行证据，不应提前标记 ENGINEERING-TRANSFERRED。

---

# 12. No Batch Completion

不再使用：

```text
23 concepts × 4 files
```

作为学习进度指标。

一个概念可以很复杂，也可以很简单。

正确顺序是：

```text
选择一个真实概念
→ 按需要运行 D / R / L / P
→ 执行对应 Acceptance / Repair Loop
→ 达到当前学习目标
→ 再进入下一个概念
```

复杂概念耗费更多篇幅、更多实验、更多工程产物是正常的。

---

# 13. No Fixed Length / No Fixed Template

这条规则同时来自 SenseWright Deep Read、Learning 与 Practice 的共同设计。

本协议不规定：

- 最低篇幅；
- 最高篇幅；
- 固定章节数；
- 固定案例数；
- 固定代码量；
- 固定文件数量。

判断标准不是：

> “写得够不够长？”

而是：

> **当前认知任务是否已经完成？**

简单对象可以很短。

复杂对象可以自然展开。

---

# 14. HMBuddy Architecture Alignment

当前 Canonical Architecture：

> HMBuddy Architecture Baseline V1.0 — Pi-native Banking Office Agent

因此学习时保持：

```text
Pi owns generic Agent runtime
HMBuddy owns Office / Banking domain
```

旧 V0.2：

```text
SessionStore
AgentLoop
ToolRegistry
ExtensionHost
```

等自研 Kernel 方向属于 Legacy。

学习这些通用 Agent 概念时：

> 去读 Pi 的真实实现。

学习 Office Domain 时：

> 去读 HMBuddy 当前代码、测试、Fixture 与真实办公案例。

---

# 15. 最终原则

这份协议最终只保留五条长期稳定原则：

1. **Use the right cognitive mode.**  
   D / R / L / P 不互相替代。

2. **Respect evidence boundaries.**  
   Reference 不是 Evidence，Source / Derived / Project Choice 要分开。

3. **Understand before compressing or abstracting.**  
   先恢复真实对象与认知结构，再抽象。

4. **Make mechanisms observable when understanding requires it.**  
   技术知识不能只剩组件名和流程名。

5. **Transfer understanding into execution only when the task reaches Practice.**  
   不把 Deep Read 写成工程教程，也不把 Practice 退化成再次解释概念。

Quality Baseline 用来检验这些原则，而不是不断产生新的顶层规则。

> **Read what it says. Review whether it holds. Learn how it works. Practice how it gets built and run.**
