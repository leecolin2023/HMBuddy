# D — Deep Read：Policy / Permission / Trust Boundary：运行时安全边界

> SenseWright：Deep Read V6.4 · Coverage-Preserving  
> HMBuddy 基线：`6eb16968c31b7fbbae377eadd6b670287d69b27a` · 状态：Runtime Policy 已实现；不是 OS Sandbox

## 任务

只恢复 HMBuddy 自身结构，不评价、不外推。核心问题：

> **插件化以后，HMBuddy 的权限模型能保护什么，又不能保护什么？**

## Raw Source

- `plugin_runtime/policy.py`
- `plugin_runtime/runtime.py`
- `plugin_runtime/contracts.py`
- `workspace/workspace.py`
- `services/artifact_reader.py`

## 认知拓扑

```text
输入/Ref
→ Workspace boundary
→ Manifest permissions
→ Runtime required_permissions gate
→ effective permissions
→ dynamic gate
→ Provider
→ trace/context boundary
```

## 独立认知单元

1. Workspace 先限定路径与 Ref trust domain。
2. Manifest 必须声明 permissions。
3. PermissionPolicy 默认只授予 filesystem.read。
4. Provider required_permissions 在 execute 前强校验。
5. 动态 gate 支持某条内部路径临时申请 COM 等高权限。
6. 权限/边界错误不允许 fallback。
7. Context 默认不暴露绝对路径。

## 认知发动机

安全的关键不是“记录权限”，而是敏感动作必须经过 Runtime 掌握的执行前 gate。Phase 1.1.1 正是把权限从观察字段提升为阻断条件。

## 当前边界

- 同进程 Python 插件可以绕过 Runtime API，因此不是恶意代码防护。
- Workspace 也不能阻止恶意插件自行访问别处。
- write/network/process 未来需要更强用户确认与审计。
- Declared、Granted、Used 是三件不同的事。

## 压缩后的模型

> **Trust Boundary = Workspace + Manifest declaration + Runtime grant + execution gate + trace。**

这句话不能替代前面的机制。Deep Read 的目标是能替代理解性重读，但精确行为仍应回 Raw Source 核验。

## Acceptance Gate

- [x] 覆盖与本概念有关的当前实现/规格。
- [x] 没把未来能力写成现状。
- [x] 保留关键责任转移与边界。
- [x] 没用外部框架改写 HMBuddy 自己的设计。

下一步：[R-review.md](./R-review.md)
