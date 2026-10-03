# D — Deep Read：Plugin Manager / System Status：把 Runtime 事实翻译成产品可解释性

> SenseWright：**Deep Read V6.4 / Coverage-Preserving**  
> HMBuddy Source Baseline：`14b79558cf25bba31a971fe144d83c145d9e7b46`  
> 当前状态：**Phase 2.1 已实现，2.1.1/2.2 加固产品视图**

## 阅读任务

只恢复 HMBuddy 当前源码/Canonical Architecture 自己建立的认知结构，不独立批判、不用外部框架改写它。

> **为什么 Plugin Manager 不能自己维护插件清单，而必须投影 Runtime 的真实状态？**

## Raw Source

- `application/plugins.py`
- `desktop/pages/plugins.py`
- `desktop/widgets/sidebar.py`
- `tests/test_phase2_1_plugins.py`
- `evals/baseline-phase2.2-v0.1.json`

## 认知拓扑

```text
Discovery/LoadReport/Registry/Policy
→ PluginView + ProviderView
→ Plugin Manager
→ SystemStatus
→ User action enable/disable/rescan
```

## 独立认知单元

1. PluginView 是产品投影，不是第二套 plugin domain。
2. 2.1.1 从“一个 Provider 一行”改成“一 Plugin 一行 + Provider 明细”。
3. 状态覆盖 Enabled/Disabled/Load Failed/Incompatible/Unavailable。
4. Declared/Effective permissions 与 availability reason 可见。
5. SystemStatus 把 LLM、plugin errors、model dir、last workspace 压缩成用户可解释状态。
6. 2.2 将 Plugin Manager 改成 Card/Rich Row，并把系统状态降为 Sidebar Status Dot。

## 认知发动机

运行时对象往往过于技术化，Product View 的作用是解释它们，而不是复制它们。只要 UI 自己维护一套状态，最终就会和 Runtime 漂移。

## 当前边界

- UI enable/disable 写 AppConfig，不修改 plugin.json。
- Plugin Manager 不负责授予高权限。
- Status Dot 是解释入口，不是监控平台。

## Coverage Reconciliation

本篇覆盖的是与该概念有独立语义的：**角色、输入输出、控制权、调用关系、当前实现状态、明确非目标与演进接口**。未来概念只按 Canonical Architecture 恢复其目标语义，不把设计目标升级为当前事实。

## 压缩后的认知模型

- Product View 是 Runtime facts 的 projection，不是新事实源。

Deep Read 到此只回答“HMBuddy 在说什么、为什么这样组织”。判断是否站得住交给同目录 Review。

下一步：[R-review.md](./R-review.md)
