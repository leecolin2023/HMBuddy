# L — Learning：Human-in-the-loop Desktop：薄应用层与人工控制点

> SenseWright：System Learning V0.5.3  
> 路径：Ground → Run Once → Explain → Vary One Condition → Model → Use

## Ground Object

用户要问“这份授信方案的关键条件是什么”，当前先由人选中正确 DOCX。

## Run Once

1. 人选择 Workspace。
2. 系统列可处理 Ref。
3. 人选择目标文件。
4. 后台 Facade 读取 Artifact。
5. UI 展示解析摘要。
6. 模型只对当前 Artifact 回答，不拥有继续开别的文件的控制权。

## 为什么每一步存在

- 用户选择文件实际上承担了当前 planner/tool selection。
- 先固定输入，才能把错误定位到 Parser/Context/LLM。
- 未来自主性就是把这些人工决策点逐个迁移。

## Boundary Variation

只改变一个条件：

> **让 Desktop 直接调用具体 Adapter，绕过 Facade。**

观察：

- 表面仍能显示文档。
- Plugin priority/fallback、Workspace trust、trace/provenance 被绕过。
- UI 重新拥有 Runtime 知识，薄层失效。

## Knowledge Model

- Desktop = Control Surface，不是 Agent Runtime。
- “薄”意味着只掌握交互与导航，不拥有文件/Provider 领域实现。
- 后台线程 ≠ Persistent Task。

## Gap

- Phase 2.1 Application State。
- scan progress/cancel。
- 未来 Agent action preview/confirmation。

## 迁移到别的项目时怎么问

- 这个概念在系统里拥有哪一段控制权？
- 它的输入输出是否是稳定 Contract，还是某个实现对象？
- 改变刚才这个条件后，哪些结论仍成立、哪些立即失效？
- 失败时能否定位到本层，而不是统一归因给“模型不行”？

## Acceptance Gate

- [x] 概念已映射到真实 HMBuddy 对象。
- [x] 至少一条具体链路完整跑过。
- [x] 解释了关键步骤为何存在。
- [x] 只变化一个高信息量条件。
- [x] 明确当前模型的适用边界。

下一步：[P-practice.md](./P-practice.md)
