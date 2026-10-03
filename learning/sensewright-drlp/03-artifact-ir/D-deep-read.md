# D — Deep Read：Artifact：Office 领域中间表示与稳定定位

> SenseWright：**Deep Read V6.4 / Coverage-Preserving**  
> HMBuddy Source Baseline：`14b79558cf25bba31a971fe144d83c145d9e7b46`  
> 当前状态：**已实现 ArtifactRef/Artifact/ArtifactBlock/ArtifactLocator；Version/Patch 未来**

## 阅读任务

只恢复 HMBuddy 当前源码/Canonical Architecture 自己建立的认知结构，不独立批判、不用外部框架改写它。

> **为什么 HMBuddy 必须保留 Artifact-native IR，而不能把所有 Office 文件转成字符串或 Markdown？**

## Raw Source

- `workspace/artifact.py`
- `adapters/base.py`
- `llm/context.py`
- `requirements/hmbuddy-architecture-baseline.md`

## 认知拓扑

```text
Native File
→ Adapter
→ ArtifactBlock + Locator
→ Artifact + Provenance
→ Context / Preview / Future Search-Write
```

## 独立认知单元

1. ArtifactRef 表示未读取对象，Artifact 表示已进入内部模型的工作成果。
2. ArtifactBlock 统一标题、段落、表格、文本框、幻灯片等顶层语义。
3. location/metadata 保留结构差异，避免最低公分母。
4. ArtifactLocator 是格式插件解释的稳定定位入口；block_id 只是解析顺序 ID。
5. Artifact.content 是预览/快速文本，不是结构事实源。
6. 未来写能力将在现有 IR 上增加 ArtifactVersion、ArtifactPatch、ArtifactDiff、ValidationResult。

## 认知发动机

Artifact 是 Office Agent 的 IR：它把复杂原生格式编译到一个可被模型、UI、工具和未来写回共同使用的稳定层，同时不丢掉 Office 结构。

## 当前边界

- Markdown 是一种 Representation，不是 Artifact。
- 开放 metadata 需要契约纪律。
- Locator 目前并未保证跨版本稳定重定位。
- 当前以 read 为主，写生命周期尚未落地。

## Coverage Reconciliation

本篇覆盖的是与该概念有独立语义的：**角色、输入输出、控制权、调用关系、当前实现状态、明确非目标与演进接口**。未来概念只按 Canonical Architecture 恢复其目标语义，不把设计目标升级为当前事实。

## 压缩后的认知模型

- Artifact = Office 工作成果的内部 IR。
- Representation 可以很多，事实源应只有一个。
- Locator 是未来可验证写入的桥。

Deep Read 到此只回答“HMBuddy 在说什么、为什么这样组织”。判断是否站得住交给同目录 Review。

下一步：[R-review.md](./R-review.md)
