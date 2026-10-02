# D — Deep Read：Workspace：工作空间、发现边界与信任域

> SenseWright：Deep Read V6.4 · Coverage-Preserving  
> HMBuddy 基线：`6eb16968c31b7fbbae377eadd6b670287d69b27a` · 状态：已实现

## 任务

只恢复 HMBuddy 自身结构，不评价、不外推。核心问题：

> **为什么办公助手需要 Workspace，而不是把任意文件路径直接交给解析器？**

## Raw Source

- `workspace/workspace.py`
- `workspace/artifact.py`
- `plugin_runtime/catalog.py`
- `services/artifact_reader.py`
- `evals/test_workspace.py`
- `requirements/phase-1.1.1-plugin-runtime-contract-hardening-v0.1.md`

## 认知拓扑

```text
用户选择 root
→ Workspace canonicalize + workspace_id
→ CapabilityCatalog 给出当前可处理扩展名
→ 扫描并过滤隐藏/临时文件
→ 生成 ArtifactRef
→ ArtifactReader 再校验 workspace_id / resolve_path
→ 进入 Capability Runtime
```

## 独立认知单元

1. Workspace 的第一职责是定义允许系统操作的本地 root，而不是简单记住“当前文件夹”。
2. Workspace 只发现文件并生成 ArtifactRef，不读取正文；发现与解析被拆成两个阶段。
3. 支持扩展名由 CapabilityCatalog 从 Runtime Registry 派生，因此插件新增格式后 Workspace 能自动发现，不再维护静态白名单。
4. ArtifactRef 带 workspace_id 与 relative_path，Ref 因而携带来源信任域，而不是只有裸绝对路径。
5. resolve_path() 把相对/绝对路径统一收敛到 root 内；ArtifactReader 对来自 Workspace 的 Ref 再做一次 trust-domain 校验。
6. Workspace 当前不是语义搜索、任务状态或远程文档库抽象，这些被刻意留给后续层。

## 认知发动机

Workspace 的核心不是“列文件”，而是把无限开放的本地文件系统收缩为 Agent/应用可操作的明确工作域。没有这层，后续自主选文件、权限、恢复都没有稳定边界。

## 当前边界

- 应用级信任边界，不是 OS sandbox。
- artifact_id 由路径生成，移动/重命名后会变化。
- 当前是本地文件系统实现，不等于未来所有 Workspace provider。
- 能发现什么不等于任务应该选择什么；语义选择属于 Search/Agent。

## 压缩后的模型

> **Workspace = Root Authority + Discovery + Ref Trust Domain。**

这句话不能替代前面的机制。Deep Read 的目标是能替代理解性重读，但精确行为仍应回 Raw Source 核验。

## Acceptance Gate

- [x] 覆盖与本概念有关的当前实现/规格。
- [x] 没把未来能力写成现状。
- [x] 保留关键责任转移与边界。
- [x] 没用外部框架改写 HMBuddy 自己的设计。

下一步：[R-review.md](./R-review.md)
