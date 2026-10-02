# D — Deep Read：Artifact / ArtifactBlock：统一中间表示

> SenseWright：Deep Read V6.4 · Coverage-Preserving  
> HMBuddy 基线：`6eb16968c31b7fbbae377eadd6b670287d69b27a` · 状态：已实现

## 任务

只恢复 HMBuddy 自身结构，不评价、不外推。核心问题：

> **为什么多种 Office/PDF 文件要先编译成统一 Artifact，而不是把第三方库对象直接交给上层？**

## Raw Source

- `workspace/artifact.py`
- `adapters/base.py`
- `adapters/docx.py`
- `adapters/pdf.py`
- `adapters/xlsx.py`
- `adapters/pptx.py`
- `llm/context.py`

## 认知拓扑

```text
Native Office/PDF
→ 格式 Parser / Adapter
→ ArtifactBlock + metadata + locator
→ Artifact + provenance
→ Context / Desktop / Future Search-Compare-Update
```

## 独立认知单元

1. ArtifactRef 表示“存在但尚未读取”，Artifact 表示已经进入 HMBuddy 内部模型。
2. Artifact 的结构事实以 blocks 为主，content 只是扁平预览。
3. ArtifactBlock 用统一顶层字段表示 heading/paragraph/table/slide 等，同时允许 location/metadata 保留必要格式差异。
4. block_id 是本次解析顺序 ID；ArtifactLocator 才用于格式特有的稳定定位。
5. Core 保存 Locator 但不解释它，解释权归对应格式插件。
6. LLM Context 只看 Artifact，不需要知道 python-docx/openpyxl/pdfplumber。

## 认知发动机

Artifact 是整个系统的“腰部 IR”：下方解析技术可以变化，上方 LLM、UI、Search、Compare 可以独立演进。没有 IR，格式差异会扩散到所有功能。

## 当前边界

- 统一不等于纯文本化，复杂结构继续保留。
- metadata 是开放 dict，扩展性高但也有 schema 漂移风险。
- Locator 是 Update 的前提，不等于完整写回契约。
- 路径型 artifact_id 不是内容哈希或全局对象 ID。

## 压缩后的模型

> **Artifact = HMBuddy 的办公文档 IR，不是 Prompt。**

这句话不能替代前面的机制。Deep Read 的目标是能替代理解性重读，但精确行为仍应回 Raw Source 核验。

## Acceptance Gate

- [x] 覆盖与本概念有关的当前实现/规格。
- [x] 没把未来能力写成现状。
- [x] 保留关键责任转移与边界。
- [x] 没用外部框架改写 HMBuddy 自己的设计。

下一步：[R-review.md](./R-review.md)
