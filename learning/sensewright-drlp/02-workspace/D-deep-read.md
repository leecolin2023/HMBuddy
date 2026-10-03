# D — Deep Read：Workspace：工作域、文件发现与信任边界

> SenseWright：**Deep Read V6.4 / Coverage-Preserving**  
> HMBuddy Source Baseline：`14b79558cf25bba31a971fe144d83c145d9e7b46`  
> 当前状态：**已实现并在 Phase 2.1.1 与 AppRuntime Catalog 对齐**

## 阅读任务

只恢复 HMBuddy 当前源码/Canonical Architecture 自己建立的认知结构，不独立批判、不用外部框架改写它。

> **Workspace 为什么既是工作上下文，又是文件访问安全作用域？**

## Raw Source

- `workspace/workspace.py`
- `workspace/artifact.py`
- `plugin_runtime/catalog.py`
- `desktop/controller.py`
- `tests/test_phase2_1_1_hardening.py`

## 认知拓扑

```text
AppRuntime Catalog
→ Workspace(root,catalog)
→ 发现 ArtifactRef
→ workspace_id/relative_path
→ ArtifactReader boundary check
→ Capability Runtime
```

## 独立认知单元

1. Workspace 固定 canonical root，并生成稳定 workspace_id。
2. 它只负责文件发现与边界，不负责解析正文。
3. 可处理扩展名来自当前 AppRuntime 的 CapabilityCatalog，而不是全局硬编码。
4. ArtifactRef 携带 workspace_id 与 relative_path，形成来源信任域。
5. Phase 2.1.1 修复了 Application Runtime 与默认 Runtime 两套 Catalog 的问题：Controller 打开 Workspace 时显式注入当前 catalog。
6. Plugin enable/disable/rescan 后，已打开 Workspace 会用新 Catalog 重建并刷新 refs。

## 认知发动机

Workspace 把“Agent 可以做什么”先缩小为“在这个工作域内对这些对象做什么”。它既是产品上的持续工作容器，也是 Kernel 的访问边界。

## 当前边界

- 不是 OS sandbox。
- 不是语义搜索引擎。
- 不是 Session Store。
- 路径型 artifact/workspace identity 有本地文件系统假设。

## Coverage Reconciliation

本篇覆盖的是与该概念有独立语义的：**角色、输入输出、控制权、调用关系、当前实现状态、明确非目标与演进接口**。未来概念只按 Canonical Architecture 恢复其目标语义，不把设计目标升级为当前事实。

## 压缩后的认知模型

- Workspace = work scope + trust domain + runtime-derived discovery。
- Product/Application 不应维护第二套文件能力事实。

Deep Read 到此只回答“HMBuddy 在说什么、为什么这样组织”。判断是否站得住交给同目录 Review。

下一步：[R-review.md](./R-review.md)
