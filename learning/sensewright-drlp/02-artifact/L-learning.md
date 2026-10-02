# L — Learning：Artifact / ArtifactBlock：统一中间表示

> SenseWright：System Learning V0.5.3  
> 路径：Ground → Run Once → Explain → Vary One Condition → Model → Use

## Ground Object

读取一份包含标题、正文、表格与图片引用的 DOCX。

## Run Once

1. DocxAdapter 识别源结构。
2. 标题成为 heading(level)，正文成为 paragraph，表格成为 table block。
3. 每个可寻址 block 生成 DOCX locator。
4. build_artifact 写 provenance。
5. artifact_to_context 只按 block_type 渲染，不知道 DOCX。

## 为什么每一步存在

- 直接传 python-docx 对象会让每个上层功能认识每种解析库。
- 只保留纯文本会不可逆丢失表格/标题/位置。
- Core 若解释 Locator，又会重新认识每种格式。

## Boundary Variation

只改变一个条件：

> **假设 HMBuddy 永远只支持纯 TXT，且只做一次性全文问答。**

观察：

- 统一 identity/provenance 仍有价值。
- 复杂 Block/Locator 的边际收益显著下降。
- 说明 Artifact 的高价值来自多格式 + 多上层能力 + 持续修改，而不是抽象本身。

## Knowledge Model

- Artifact = HMBuddy 的办公文档 IR，不是 Prompt。
- Adapter 负责 Native → Artifact；Context/Search/Presenter 负责 Artifact → 用途表示。
- 正确 IR 统一公共语义，但不抹掉必要差异。

## Gap

- 关键 metadata schema 的正式化。
- Update 的 revision/conflict。
- 跨格式操作语义。

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
