# D — Deep Read：Application Runtime Composition：Controller 与单一运行时事实

> SenseWright：**Deep Read V6.4 / Coverage-Preserving**  
> HMBuddy Source Baseline：`14b79558cf25bba31a971fe144d83c145d9e7b46`  
> 当前状态：**Phase 2.1/2.1.1 已实现**

## 阅读任务

只恢复 HMBuddy 当前源码/Canonical Architecture 自己建立的认知结构，不独立批判、不用外部框架改写它。

> **Application 层如何把 Config、State、Plugin Runtime、Workspace、LLM 组装成一个一致的产品运行环境？**

## Raw Source

- `application/plugins.py`
- `desktop/controller.py`
- `desktop/app.py`
- `tests/test_phase2_1_1_hardening.py`

## 认知拓扑

```text
Resolve Paths
→ Load Config/State
→ Resolve EffectiveConfig
→ assemble_app_runtime
→ Catalog + Plugin Views + LLM
→ AppController
→ PySide6 Shell
```

## 独立认知单元

1. desktop/app.py 是 Composition Root：启动日志、bootstrap Controller、创建 QApplication/Shell、可选恢复 Workspace。
2. bootstrap_controller 一次性解析显式 env，后续不重新偷偷读取另一套环境上下文。
3. AppRuntime 聚合 RuntimeAssembly、EffectiveConfig、CapabilityCatalog、LLM Client/status。
4. Controller 是无 Qt 的应用动作层：open workspace/artifact、settings、plugins、recent、temporary conversation。
5. 2.1.1 的核心是消除 Catalog、Config、Workspace identity、Plugin status 等‘两套事实源’。
6. Settings/Rescan 后重建 AppRuntime、Reader、Workspace，保持同步。

## 认知发动机

Composition Root 的任务是把很多正确组件组装成一个一致系统。架构 bug 往往不是单个模块错，而是 Product、Application、Runtime 各自拿了不同实例/配置。

## 当前边界

- Controller 不是 Kernel Session/AgentLoop。
- Application 层可以编排，但不复制 Domain/Runtime 规则。
- GUI 不应成为 Composition Root 的隐藏第二套装配路径。

## Coverage Reconciliation

本篇覆盖的是与该概念有独立语义的：**角色、输入输出、控制权、调用关系、当前实现状态、明确非目标与演进接口**。未来概念只按 Canonical Architecture 恢复其目标语义，不把设计目标升级为当前事实。

## 压缩后的认知模型

- Composition Root = 把配置意图编译成一组一致的 live objects。

Deep Read 到此只回答“HMBuddy 在说什么、为什么这样组织”。判断是否站得住交给同目录 Review。

下一步：[R-review.md](./R-review.md)
