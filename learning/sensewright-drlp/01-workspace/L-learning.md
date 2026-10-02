# L — Learning：Workspace：工作空间、发现边界与信任域

> SenseWright：System Learning V0.5.3  
> 路径：Ground → Run Once → Explain → Vary One Condition → Model → Use

## Ground Object

工作区里有 report.docx、data.xlsx、~$report.docx，并安装一个支持 .foo 的外部插件。

## Run Once

1. Workspace 固定 root 并计算 workspace_id。
2. Catalog 从 Registry 得到 .docx/.xlsx/.foo。
3. list_artifacts 过滤临时文件并生成 Ref。
4. 用户选 Ref 后，Reader 验证 workspace_id 与 root。
5. 校验完成后才构造 CapabilityRequest。

## 为什么每一步存在

- 先边界校验再进插件，避免危险路径先产生副作用。
- 支持格式必须只有一个事实源，否则“Runtime 能读但 Workspace 看不见”。
- Ref 带 trust domain，才能阻止跨 Workspace 复用。

## Boundary Variation

只改变一个条件：

> **把来自 Workspace A 的 Ref 交给 Workspace B 读取。**

观察：

- 文件元数据仍然存在。
- Ref 的信任资格失效。
- Reader 在进入 Provider 前抛 WorkspaceBoundaryError。
- 因此 Ref 不是纯 DTO，而是带工作域语义的引用。

## Knowledge Model

- Workspace = Root Authority + Discovery + Ref Trust Domain。
- Workspace 回答“允许操作哪些对象”，Adapter 回答“怎样理解对象”。
- 先有 Workspace，再谈 Agent 自主选文件。

## Gap

- 语义相关性选择。
- 长期对象身份。
- 恶意插件隔离。

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
