# D — Deep Read：Stable Facade + Capability：应用意图与 Runtime 能力

> SenseWright：**Deep Read V6.4 / Coverage-Preserving**  
> HMBuddy Source Baseline：`14b79558cf25bba31a971fe144d83c145d9e7b46`  
> 当前状态：**artifact.read.full 已实现；其他能力为目标命名空间**

## 阅读任务

只恢复 HMBuddy 当前源码/Canonical Architecture 自己建立的认知结构，不独立批判、不用外部框架改写它。

> **为什么应用调用 Facade/Capability，而不是直接点名 Provider 或 Adapter？**

## Raw Source

- `services/artifact_reader.py`
- `plugin_runtime/contracts.py`
- `plugin_runtime/registry.py`
- `requirements/hmbuddy-architecture-baseline.md`

## 认知拓扑

```text
Application/Tool
→ Stable Facade
→ CapabilityRequest
→ Registry/Router
→ Provider
→ CapabilityResult
```

## 独立认知单元

1. Facade 对应用暴露稳定调用，例如 read_artifact。
2. Capability 表达要做什么，例如 artifact.read.full，而不是用哪个实现。
3. Registry 允许同一 capability 有多个 Provider。
4. Tool 与 Capability 在架构总纲中被严格区分：Tool 面向 Agent，Capability 面向 Runtime。
5. Facade 可以承担 Workspace/size 等通用前置校验，但不能变成所有文件功能的 God Service。

## 认知发动机

把“意图”和“实现”分开，才允许 Runtime 独立替换 Provider、执行权限和 fallback，而上层产品/Agent 不随之变化。

## 当前边界

- 预留 capability 名不等于已经有 Contract。
- mode 参数未来不能与 capability 双重控制语义。
- Agent 不应直接看全部底层 capability。

## Coverage Reconciliation

本篇覆盖的是与该概念有独立语义的：**角色、输入输出、控制权、调用关系、当前实现状态、明确非目标与演进接口**。未来概念只按 Canonical Architecture 恢复其目标语义，不把设计目标升级为当前事实。

## 压缩后的认知模型

- Facade = 应用稳定入口；Capability = Runtime 稳定意图；Tool = 模型动作接口。

Deep Read 到此只回答“HMBuddy 在说什么、为什么这样组织”。判断是否站得住交给同目录 Review。

下一步：[R-review.md](./R-review.md)
