# L — Learning：Skill：Markdown-first 工作方法与 Progressive Disclosure

> SenseWright：**System Learning V0.5.3**  
> 路径：Ground → Run Once → Explain → Vary One Condition → Model → Use

## Ground Object

用户说“用 Deep Read 学习这份制度”。

## Run Once

1. Agent 初始看到 DeepRead name/description。
2. 判断匹配后加载 SKILL.md。
3. 按 Skill 步骤调用 read/search 工具。
4. 需要时才读取 references。
5. 输出后执行 Skill validation。

## Mechanism：为什么这样跑

- 所有 Skill 全量注入会浪费 Context。
- 方法属于可变知识，不应编译成 AgentLoop 分支。

## Boundary Variation

一次只改变一个高信息量条件：

> **Skill 里某一步必须确定性比较两个表格。**

结果：

- 这一步适合调用 compare/validate Tool 或 script。
- Skill 仍是方法编排，不需要升级 Workflow Engine。

这个变化用来检查当前模型哪些仍成立、哪些削弱、哪些变成新问题，而不是做穷举。

## Knowledge Model

- Skill = how to work；Tool = what can be done；Plugin = how action is implemented。

## Gaps

- Skill discovery/loader。
- Tool dependency validation。
- Session 中 skill usage trace。

这些 Gap 只有在阻塞下一步时才进入实现，不为了“完整”全部提前建设。

## Prediction Check

如果把当前概念放到相邻场景，至少应能预测：

- 哪一层最先受到条件变化影响；
- 哪些 Contract 仍可复用；
- 哪些只是当前实现选择；
- 什么情况下需要回到 Architecture Change / Contract redesign。

## Project to Use

学习完本篇后，面对别的 Agent/办公系统，应先定位：**谁拥有控制权、状态在哪、实现细节在哪一层结束、上层依赖的稳定 Contract 是什么。**

下一步：[P-practice.md](./P-practice.md)
