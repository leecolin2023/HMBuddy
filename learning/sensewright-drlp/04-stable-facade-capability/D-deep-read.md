# D — Deep Read：Stable Facade + Capability：稳定入口与能力语义

> SenseWright：Deep Read V6.4 · Coverage-Preserving  
> HMBuddy 基线：`6eb16968c31b7fbbae377eadd6b670287d69b27a` · 状态：artifact.read.full 已实现，其他 capability 仅预留

## 任务

只恢复 HMBuddy 自身结构，不评价、不外推。核心问题：

> **为什么上层应该表达“我要什么能力”，而不是指定哪个 Adapter/Plugin？**

## Raw Source

- `services/artifact_reader.py`
- `plugin_runtime/contracts.py`
- `plugin_runtime/registry.py`
- `plugin_runtime/router.py`
- `requirements/phase-1.1-pluggable-file-capability-runtime-v0.1.md`

## 认知拓扑

```text
Application 调 read_artifact
→ Facade 通用校验
→ CapabilityRequest(artifact.read.full)
→ Registry/Router 选择 Provider
→ Runtime
→ CapabilityResult
→ Artifact
```

## 独立认知单元

1. read_artifact() 是应用稳定入口，Desktop/CLI 不需要知道 Plugin Runtime 内部。
2. CapabilityRequest 描述要什么能力，不携带 Adapter 或第三方库对象。
3. Registry 以 capability 为一级索引，同一能力允许多个 Provider。
4. Router 负责 supports/availability/priority，不由调用方挑 Provider。
5. 当前真正实现的只有 artifact.read.full；outline/search/update 等是命名空间预留。
6. Facade 还负责通用前置校验与 provenance 收口。

## 认知发动机

Facade 保护调用方，Capability 保护实现方。调用语法稳定与请求语义稳定一起形成可替换性。

## 当前边界

- 未来应避免 mode 参数与 capability 形成两套事实源。
- 预留名字不是实现承诺。
- Capability 不负责选择 Provider。
- 不要退化成 docx.read 这类格式别名。

## 压缩后的模型

> **Facade = 应用稳定入口。**

这句话不能替代前面的机制。Deep Read 的目标是能替代理解性重读，但精确行为仍应回 Raw Source 核验。

## Acceptance Gate

- [x] 覆盖与本概念有关的当前实现/规格。
- [x] 没把未来能力写成现状。
- [x] 保留关键责任转移与边界。
- [x] 没用外部框架改写 HMBuddy 自己的设计。

下一步：[R-review.md](./R-review.md)
