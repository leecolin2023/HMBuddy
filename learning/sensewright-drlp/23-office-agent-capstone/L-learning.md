# L — Learning：End-to-End Office Agent：从工作区到持续可修改成果

> SenseWright：**System Learning V0.5.3**  
> 路径：Ground → Run Once → Explain → Vary One Condition → Model → Use

## Ground Object

“根据 Workspace 中 5 份材料生成一份 Markdown/Word 报告；我看完后提出两处修改，再给我最终版和差异。”

## Run Once

1. 创建 Session 绑定 Workspace。
2. AgentLoop 用 search/list/read 找材料。
3. 加载合适 Skill。
4. create_file 生成 Artifact。
5. validate_file 检查。
6. Conversation 展示结果/Preview。
7. 用户反馈进入同一 Session。
8. edit_file 生成 Patch。
9. 产生新 Version/Diff。
10. Session 标记 completed，可在重启后恢复。

## Mechanism：为什么这样跑

- 这个场景同时验证最少必要 Kernel 与 Office-specific 写能力。
- 如果某原语没有实际贡献，可以删；如果出现真实缺口，再演进。

## Boundary Variation

一次只改变一个高信息量条件：

> **只改变一个条件：生成成果只需 Markdown，不需要 DOCX。**

结果：

- Artifact 写 Provider/validation 简化。
- Session/Loop/Tool/Skill 架构仍成立。
- 可先用 Markdown 证明 Agent Kernel，再进入 DOCX Patch。

这个变化用来检查当前模型哪些仍成立、哪些削弱、哪些变成新问题，而不是做穷举。

## Knowledge Model

- 真正的 HMBuddy = Minimal Agent Harness × Artifact-native Office Runtime × WorkBuddy-like Product Surface。

## Gaps

- Stage B 全部原语。
- Stage C Tools。
- Artifact write lifecycle。

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
