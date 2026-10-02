# D — Deep Read：Plugin Runtime：发现、装载、注册、路由与执行

> SenseWright：Deep Read V6.4 · Coverage-Preserving  
> HMBuddy 基线：`6eb16968c31b7fbbae377eadd6b670287d69b27a` · 状态：已实现并完成 Contract Hardening

## 任务

只恢复 HMBuddy 自身结构，不评价、不外推。核心问题：

> **为什么 Plugin Runtime 需要 Manifest、Discovery、Loader、Registry、Router、Runtime 多个角色？**

## Raw Source

- `plugin_runtime/manifest.py`
- `plugin_runtime/discovery.py`
- `plugin_runtime/loader.py`
- `plugin_runtime/registry.py`
- `plugin_runtime/router.py`
- `plugin_runtime/runtime.py`
- `evals/test_external_plugin.py`

## 认知拓扑

```text
Plugin dir
→ Manifest 校验
→ Discovery
→ Loader
→ Provider 实例
→ Registry
→ Router
→ Runtime execute/fallback/trace
→ Result
```

## 独立认知单元

1. Manifest 在执行代码前声明 identity/version/api/capabilities/permissions/platform。
2. Discovery 只找插件与 Manifest。
3. Loader 在 Manifest 合法后加载 entrypoint，并把 Manifest 作为 Provider 权威声明。
4. Registry 按 capability 保存已验证 Provider。
5. Router 在请求时做 supports/availability/priority 选择。
6. Runtime 独占权限、执行、fallback allowlist 与 trace。

## 认知发动机

发现、相信声明、加载代码、参加路由、真正执行是不同的信任/状态转换；一个 plugins 字典无法表达这些失败模式。

## 当前边界

- 进程内插件不是 sandbox。
- priority 是确定性选择规则，不是质量评分。
- fallback 只针对显式 allowlist。
- API version 目前是 v1。

## 压缩后的模型

> **Manifest=声明；Discovery=找到；Loader=进入代码；Registry=目录；Router=选择；Runtime=执行治理。**

这句话不能替代前面的机制。Deep Read 的目标是能替代理解性重读，但精确行为仍应回 Raw Source 核验。

## Acceptance Gate

- [x] 覆盖与本概念有关的当前实现/规格。
- [x] 没把未来能力写成现状。
- [x] 保留关键责任转移与边界。
- [x] 没用外部框架改写 HMBuddy 自己的设计。

下一步：[R-review.md](./R-review.md)
