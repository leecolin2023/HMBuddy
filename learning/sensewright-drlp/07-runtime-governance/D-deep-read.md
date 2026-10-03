# D — Deep Read：Runtime Governance：Policy、Availability、Fallback、Trace

> SenseWright：**Deep Read V6.4 / Coverage-Preserving**  
> HMBuddy Source Baseline：`14b79558cf25bba31a971fe144d83c145d9e7b46`  
> 当前状态：**已实现**

## 阅读任务

只恢复 HMBuddy 当前源码/Canonical Architecture 自己建立的认知结构，不独立批判、不用外部框架改写它。

> **如何让“可插拔”不变成不可控：执行前应该由谁决定能不能跑、失败是否能换实现、发生过什么？**

## Raw Source

- `plugin_runtime/policy.py`
- `plugin_runtime/runtime.py`
- `plugin_runtime/router.py`
- `plugin_runtime/availability.py`
- `plugin_runtime/errors.py`

## 认知拓扑

```text
Request
→ supports
→ availability
→ permission pre-check
→ execute
→ allowlisted fallback
→ trace/result
```

## 独立认知单元

1. Availability 检查平台、Python/依赖等环境条件。
2. Policy 默认最小权限，required_permissions 在 execute 前强校验。
3. 动态 permission gate 支持仅在具体分支申请 COM 等权限。
4. Fallback 只允许解析类/Provider execution 类错误；Workspace/Permission 等错误不能换 Provider 掩盖。
5. Trace 记录 request/provider/duration/status/error/fallback_from，且内存队列有界。
6. Policy 是 Runtime 合作型治理，不是 OS sandbox。

## 认知发动机

可插拔系统的真正价值不在能装插件，而在控制权仍留在 Runtime：谁执行、允许什么、如何失败、如何解释都必须由统一层掌握。

## 当前边界

- 同进程恶意代码可绕过 Policy。
- 未来 ASK/Approval 需要 Product/Extension 配合。
- Trace 不是 Session checkpoint。

## Coverage Reconciliation

本篇覆盖的是与该概念有独立语义的：**角色、输入输出、控制权、调用关系、当前实现状态、明确非目标与演进接口**。未来概念只按 Canonical Architecture 恢复其目标语义，不把设计目标升级为当前事实。

## 压缩后的认知模型

- Declared ≠ Granted ≠ Used。
- Runtime Governance 的核心是统一控制权。

Deep Read 到此只回答“HMBuddy 在说什么、为什么这样组织”。判断是否站得住交给同目录 Review。

下一步：[R-review.md](./R-review.md)
