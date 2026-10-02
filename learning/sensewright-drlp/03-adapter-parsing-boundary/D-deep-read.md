# D — Deep Read：Adapter / Parsing Boundary：格式解析隔离层

> SenseWright：Deep Read V6.4 · Coverage-Preserving  
> HMBuddy 基线：`6eb16968c31b7fbbae377eadd6b670287d69b27a` · 状态：已实现

## 任务

只恢复 HMBuddy 自身结构，不评价、不外推。核心问题：

> **文件格式差异应该在哪一层被吸收，为什么 Adapter 不是简单的读取函数集合？**

## Raw Source

- `adapters/base.py`
- `adapters/docx.py`
- `adapters/pdf.py`
- `adapters/xlsx.py`
- `adapters/pptx.py`
- `adapters/ocr/`
- `plugins/`
- `services/artifact_reader.py`

## 认知拓扑

```text
CapabilityRequest
→ Provider
→ Adapter
→ 第三方 Parser/OCR/COM
→ 结构恢复
→ Artifact
```

## 独立认知单元

1. 不同格式可以使用完全不同解析库，但输出都必须是 Artifact。
2. DOCX、PDF、XLSX、PPTX 的源结构恢复发生在 Adapter 内。
3. OCR、表格恢复、文本规范化属于解析域，不应泄漏成上层格式判断。
4. Plugin Provider 负责能力声明/可用性/权限，Adapter 负责解析本身。
5. ArtifactReader 正常路径不 import 具体 Adapter 类。
6. Reader 在进入 Adapter 前完成 Workspace/大小等通用校验。

## 认知发动机

Adapter 把第三方解析技术的不稳定性限制在底层，使上层变化原因从“某库 API 变了”收敛为“Artifact Contract 真要变”。

## 当前边界

- Adapter 不决定 Provider selection。
- Adapter 不负责 LLM budget。
- OCR 是解析策略，不是 UI/Context 分支。
- 未来 create/update 未必复用 read Adapter。

## 压缩后的模型

> **Adapter = Native format compiler frontend。**

这句话不能替代前面的机制。Deep Read 的目标是能替代理解性重读，但精确行为仍应回 Raw Source 核验。

## Acceptance Gate

- [x] 覆盖与本概念有关的当前实现/规格。
- [x] 没把未来能力写成现状。
- [x] 保留关键责任转移与边界。
- [x] 没用外部框架改写 HMBuddy 自己的设计。

下一步：[R-review.md](./R-review.md)
