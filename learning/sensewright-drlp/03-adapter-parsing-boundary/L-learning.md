# L — Learning：Adapter / Parsing Boundary：格式解析隔离层

> SenseWright：System Learning V0.5.3  
> 路径：Ground → Run Once → Explain → Vary One Condition → Model → Use

## Ground Object

同一个“读取一张表”的目标，分别从 XLSX 与 PDF 输入。

## Run Once

1. XLSX 直接获得 sheet/cell 网格。
2. PDF 需要页面几何、矢量线甚至 OCR 才恢复网格。
3. 两条链在 Parser 层完全不同。
4. 生成 table ArtifactBlock 后重新统一。
5. Context 只看 table block，而 provenance 保留 extraction method。

## 为什么每一步存在

- 统一太早会让 PDF 假装拥有 Excel cell 模型。
- 统一太晚会让所有上层分别实现四套格式逻辑。
- 合适边界是源结构恢复完成后进入 Artifact IR。

## Boundary Variation

只改变一个条件：

> **允许 Desktop/LLM 层直接接收 python-docx/openpyxl/pdfplumber 原生对象。**

观察：

- 单格式 happy path 变短。
- 上层测试矩阵膨胀为能力×格式×解析库。
- Provider 替换、外部插件与多格式能力失去稳定依赖。

## Knowledge Model

- Adapter = Native format compiler frontend。
- Provider = Runtime integration wrapper。
- 判断边界是否健康：上层是否需要 import 某个格式解析库。

## Gap

- 非确定性视觉解析的 evidence/confidence schema。
- write/create 的独立实现边界。
- 性能/资源 profile。

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
