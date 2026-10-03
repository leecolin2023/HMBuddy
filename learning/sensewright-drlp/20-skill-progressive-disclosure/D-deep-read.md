# D — Deep Read：Skill：Markdown-first 工作方法与 Progressive Disclosure

> SenseWright：**Deep Read V6.4 / Coverage-Preserving**  
> HMBuddy Source Baseline：`14b79558cf25bba31a971fe144d83c145d9e7b46`  
> 当前状态：**Canonical future capability；SenseWright 被指定为优先接入 Skills**

## 阅读任务

只恢复 HMBuddy 当前源码/Canonical Architecture 自己建立的认知结构，不独立批判、不用外部框架改写它。

> **Skill 为什么是‘Agent 应怎样完成一类工作’，而不是 Workflow Engine 或 Agent 子类？**

## Raw Source

- `requirements/hmbuddy-architecture-baseline.md`
- `SenseWright skills/article-deep-read-v6.4/SKILL.md`
- `SenseWright skills/vibe-review-v0.10/SKILL.md`
- `SenseWright skills/system-learning-v0.5.3/SKILL.md`
- `SenseWright skills/practice-v0.2/SKILL.md`

## 认知拓扑

```text
Skill metadata name/description
→ 按需选择
→ 加载 SKILL.md
→ 按需加载 references/templates/scripts
→ Agent 使用 Tools 执行
→ Validation
```

## 独立认知单元

1. Skill 解决工作方法，Tool 解决动作，Capability Plugin 解决动作实现。
2. 推荐 Markdown-first 目录 SKILL.md + references/scripts/templates。
3. Progressive Disclosure：初始只看到 name/description，需要时再加载正文与资源。
4. SenseWright 四路 Skill 应作为 HMBuddy Skills 接入，而不是改写成 Python Workflow/Graph。
5. 只有确定性步骤才配套 Script/Tool。

## 认知发动机

Skill 把高层工作方法放在可编辑文本层，使 Kernel 不因每种业务方法都新增状态机；Progressive Disclosure 则保护 Context 预算。

## 当前边界

- Skill 不是 durable Session state。
- Skill 不直接绕过 Tool/Policy。
- 复杂 Planner 不默认成为 Core。

## Coverage Reconciliation

本篇覆盖的是与该概念有独立语义的：**角色、输入输出、控制权、调用关系、当前实现状态、明确非目标与演进接口**。未来概念只按 Canonical Architecture 恢复其目标语义，不把设计目标升级为当前事实。

## 压缩后的认知模型

- Skill = how to work；Tool = what can be done；Plugin = how action is implemented。

Deep Read 到此只回答“HMBuddy 在说什么、为什么这样组织”。判断是否站得住交给同目录 Review。

下一步：[R-review.md](./R-review.md)
