# L — Learning：Stable Facade + Capability：稳定入口与能力语义

> SenseWright：System Learning V0.5.3  
> 路径：Ground → Run Once → Explain → Vary One Condition → Model → Use

## Ground Object

同一 .md 同时有内置 Text Provider(priority 50) 与外部 Markdown Provider(priority 100)。

## Run Once

1. Desktop 仍只调 read_artifact。
2. Facade 构造 artifact.read.full。
3. Registry 返回多个候选。
4. Router 检查支持/可用性并按 priority 选择。
5. 外部 Provider 执行，Desktop 收到同一种 Artifact。

## 为什么每一步存在

- 调用方若直接点名 Provider，替换/fallback 就不再透明。
- Capability 用格式命名会把实现细节污染意图层。
- Application 选 capability，Runtime 选 provider。

## Boundary Variation

只改变一个条件：

> **让 Desktop 直接实例化 DocxAdapter/PdfAdapter，绕过 Facade。**

观察：

- 单个文件仍可解析。
- Workspace trust、统一大小限制、Plugin priority/fallback、trace/provenance 被绕过。
- Facade 的价值在治理，不只是少写几行。

## Knowledge Model

- Facade = 应用稳定入口。
- Capability = Runtime 稳定意图。
- Provider = capability 的可替换实现。

## Gap

- read.outline/search 的正式 Contract。
- 写能力的安全语义。
- 多 Facade 的组织方式。

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
