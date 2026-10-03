# D — Deep Read：Artifact Write Lifecycle：Version、Patch、Validate、Diff

> SenseWright：**Deep Read V6.4 / Coverage-Preserving**  
> HMBuddy Source Baseline：`14b79558cf25bba31a971fe144d83c145d9e7b46`  
> 当前状态：**Canonical future Office capability；尚未实现**

## 阅读任务

只恢复 HMBuddy 当前源码/Canonical Architecture 自己建立的认知结构，不独立批判、不用外部框架改写它。

> **为什么 HMBuddy 走向真正 Office Agent 的关键跃迁是可验证写入，而不是先做 Multi-Agent？**

## Raw Source

- `requirements/hmbuddy-architecture-baseline.md`
- `workspace/artifact.py`
- `plugin_runtime/contracts.py`

## 认知拓扑

```text
Artifact base version
→ ArtifactPatch operations(locator)
→ Capability Provider
→ New Artifact Version
→ Validate
→ ArtifactDiff
→ User/Agent continue
```

## 独立认知单元

1. 架构总纲明确把 read-only→可验证写入视为关键跃迁。
2. 不推荐 update_docx(file,instruction) 黑盒接口。
3. ArtifactPatch 应包含 artifact_id、base_version、operations、metadata。
4. operations 基于 Locator 做 replace/insert/delete/update_cell 等。
5. 写后形成新 ArtifactVersion，再 Validate，再产生 ArtifactDiff。
6. 现有 ArtifactLocator 应被复用，而不是另起定位模型。

## 认知发动机

持续办公任务的价值来自‘同一成果反复修改并可核验’。Patch/Version/Diff 把模型语义决策与确定性文件修改分开，也提供审计、冲突与用户确认基础。

## 当前边界

- 写操作必须在 Workspace/Policy 内。
- Version/Locator 冲突需要明确失败，不可静默覆盖。
- 不同 Office 格式可有不同 Provider，但 Patch 顶层语义应尽量稳定。

## Coverage Reconciliation

本篇覆盖的是与该概念有独立语义的：**角色、输入输出、控制权、调用关系、当前实现状态、明确非目标与演进接口**。未来概念只按 Canonical Architecture 恢复其目标语义，不把设计目标升级为当前事实。

## 压缩后的认知模型

- Write = Patch against Version → New Version → Validate → Diff。

Deep Read 到此只回答“HMBuddy 在说什么、为什么这样组织”。判断是否站得住交给同目录 Review。

下一步：[R-review.md](./R-review.md)
