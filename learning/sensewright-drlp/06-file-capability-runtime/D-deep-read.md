# D — Deep Read：File Capability Runtime：Manifest、Plugin、Provider、Registry、Router

> SenseWright：**Deep Read V6.4 / Coverage-Preserving**  
> HMBuddy Source Baseline：`14b79558cf25bba31a971fe144d83c145d9e7b46`  
> 当前状态：**已实现并硬化**

## 阅读任务

只恢复 HMBuddy 当前源码/Canonical Architecture 自己建立的认知结构，不独立批判、不用外部框架改写它。

> **为什么文件能力插件要经历声明、发现、加载、注册、路由和执行多个阶段？**

## Raw Source

- `plugin_runtime/manifest.py`
- `plugin_runtime/discovery.py`
- `plugin_runtime/loader.py`
- `plugin_runtime/registry.py`
- `plugin_runtime/router.py`
- `plugin_runtime/runtime.py`
- `plugins/`

## 认知拓扑

```text
plugin.json
→ Discovery
→ Manifest validation
→ Loader
→ Provider instances
→ Registry
→ Router
→ Runtime execute
```

## 独立认知单元

1. Manifest 在执行插件代码前声明 identity/API/capabilities/extensions/permissions/platform。
2. Discovery 与 Loader 分离，使非法声明可在代码执行前被拒绝。
3. Loader 把 Manifest 作为 Provider 身份/priority/extensions 等权威来源。
4. Registry 记录已验证 Provider；Router 在请求时判断 supports/availability/priority。
5. Runtime 负责执行、权限、fallback、trace。
6. Capability Plugin 只扩展文件/Artifact 能力，不承担 Session/Memory/MCP 等 Agent 行为。

## 认知发动机

插件生命周期本质是逐步扩大信任：发现目录→相信声明→执行代码→允许参与选择→真正执行。每一步失败语义都不同。

## 当前边界

- 进程内插件不是安全隔离。
- Capability Plugin ≠ Agent Extension。
- priority ≠ 质量评分。

## Coverage Reconciliation

本篇覆盖的是与该概念有独立语义的：**角色、输入输出、控制权、调用关系、当前实现状态、明确非目标与演进接口**。未来概念只按 Canonical Architecture 恢复其目标语义，不把设计目标升级为当前事实。

## 压缩后的认知模型

- Capability Plugin 管“某能力如何实现”；Agent Extension 管“Agent 如何行为”。

Deep Read 到此只回答“HMBuddy 在说什么、为什么这样组织”。判断是否站得住交给同目录 Review。

下一步：[R-review.md](./R-review.md)
