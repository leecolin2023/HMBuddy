# D — Deep Read：Artifact Preview：可读取、可表示、可预览是三件不同的事

> SenseWright：**Deep Read V6.4 / Coverage-Preserving**  
> HMBuddy Source Baseline：`14b79558cf25bba31a971fe144d83c145d9e7b46`  
> 当前状态：**Phase 2.2 已实现 Markdown/TXT Preview**

## 阅读任务

只恢复 HMBuddy 当前源码/Canonical Architecture 自己建立的认知结构，不独立批判、不用外部框架改写它。

> **为什么一个格式“Runtime 能读取”不等于“Desktop 已支持 Rich Preview”？**

## Raw Source

- `desktop/widgets/preview/renderers.py`
- `desktop/widgets/preview/pane.py`
- `tests/test_phase2_2_desktop_qt.py`
- `requirements/phase-2.2-desktop-ux-shell-redesign-v0.1.md`

## 认知拓扑

```text
ArtifactRef
→ ArtifactReader
→ Artifact
→ PreviewModel
→ Markdown/TXT/Unsupported renderer
```

## 独立认知单元

1. Preview 数据必须来自 Artifact，不允许 path→open/read_text。
2. Markdown/TXT 当前有 Presentation renderer；DOCX/PDF/XLSX/PPTX 可读但 Preview Unsupported。
3. PreviewModel 是面向 UI 的 Representation，和 Artifact Contract 分开。
4. Markdown 使用 Qt setMarkdown，不执行脚本、不加载远程资源。
5. AST guard 把“不绕过 Artifact Runtime”变成测试契约。

## 认知发动机

读取是 Domain 能力，预览是 Presentation 能力。把两者分开可以避免为了 UI 渲染反向污染 Artifact/Capability Runtime，也避免错误承诺“能 parse 就能高保真显示”。

## 当前边界

- Preview 不是 artifact.render capability。
- 当前 Markdown renderer 是 Qt 子集。
- Unsupported 不影响 QA/read。

## Coverage Reconciliation

本篇覆盖的是与该概念有独立语义的：**角色、输入输出、控制权、调用关系、当前实现状态、明确非目标与演进接口**。未来概念只按 Canonical Architecture 恢复其目标语义，不把设计目标升级为当前事实。

## 压缩后的认知模型

- Artifact 是事实；PreviewModel 是某个产品面的 Representation。

Deep Read 到此只回答“HMBuddy 在说什么、为什么这样组织”。判断是否站得住交给同目录 Review。

下一步：[R-review.md](./R-review.md)
