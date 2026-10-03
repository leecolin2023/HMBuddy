# D — Deep Read：Adapter / Parsing Boundary：Native Structure、OCR 与 COM

> SenseWright：**Deep Read V6.4 / Coverage-Preserving**  
> HMBuddy Source Baseline：`14b79558cf25bba31a971fe144d83c145d9e7b46`  
> 当前状态：**已实现多格式读取与 OCR/COM fallback**

## 阅读任务

只恢复 HMBuddy 当前源码/Canonical Architecture 自己建立的认知结构，不独立批判、不用外部框架改写它。

> **格式差异、解析算法和原生 Office 机制应该在哪一层结束？**

## Raw Source

- `adapters/base.py`
- `adapters/docx.py`
- `adapters/pdf.py`
- `adapters/xlsx.py`
- `adapters/pptx.py`
- `adapters/ocr/`
- `adapters/doc_legacy.py`
- `adapters/xls.py`

## 认知拓扑

```text
Provider
→ Adapter
→ Native parser / OCR / COM
→ 结构恢复
→ Artifact
```

## 独立认知单元

1. Adapter 的责任是 Native format → Artifact，而不是路由或产品交互。
2. DOCX/XLSX/PPTX/PDF 使用不同库与不同结构恢复方式。
3. PDF OCR、矢量表格、XLS COM fallback 等属于解析实现细节。
4. 环境可用性、权限与 Provider priority 放在 Runtime/Provider，不应回流到上层。
5. Office/WPS COM 是结构化接口 hierarchy 中的 fallback，不等于所有办公操作都走 Computer Use。

## 认知发动机

解析层的目标是把不可控的格式/库差异约束在最底部，然后交付稳定 IR。越过这个边界，上层复杂度会按“功能 × 格式 × 解析库”乘法增长。

## 当前边界

- Adapter 不做 Agent Tool selection。
- Adapter 不拥有 Workspace policy。
- Adapter 不决定 Context budget。
- 未来 writer/patcher 不应因为目录方便就强行塞进 read adapter。

## Coverage Reconciliation

本篇覆盖的是与该概念有独立语义的：**角色、输入输出、控制权、调用关系、当前实现状态、明确非目标与演进接口**。未来概念只按 Canonical Architecture 恢复其目标语义，不把设计目标升级为当前事实。

## 压缩后的认知模型

- Adapter = Native format compiler frontend。
- Provider = Runtime wrapper；Artifact = IR。

Deep Read 到此只回答“HMBuddy 在说什么、为什么这样组织”。判断是否站得住交给同目录 Review。

下一步：[R-review.md](./R-review.md)
