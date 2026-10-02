# P — Practice：Workspace：工作空间、发现边界与信任域

> SenseWright：Practice V0.2  
> 目标：Knowledge Model → Executable Engineering Model

## Real Scenario

实现并验证一个新的 .foo 外部插件：不修改 Workspace/Core，.foo 自动出现在工作区；跨 Workspace Ref 必须被拒绝。

## Engineering Model

- Manifest/Provider 声明 .foo 与 artifact.read.full。
- Registry → CapabilityCatalog 自动暴露 .foo。
- Workspace 发现并生成带 workspace_id 的 Ref。
- Reader 做边界检查后执行 Runtime。

## End-to-End Implementation

1. 创建外部 plugin.json 与 Provider。
2. 用 assemble_runtime 装配独立 Runtime。
3. 从该 Registry 构造 Catalog 并创建 Workspace。
4. 断言 a.foo 被发现、临时/未知文件不被发现。
5. 读取 a.foo，检查 provenance。
6. 把 Ref 交给另一个 Workspace，断言 Provider 未执行。

## Concrete Path

```text
用户选择 root → Workspace canonicalize + workspace_id → CapabilityCatalog 给出当前可处理扩展名 → 扫描并过滤隐藏/临时文件 → 生成 ArtifactRef → ArtifactReader 再校验 workspace_id / resolve_path → 进入 Capability Runtime
```

本练习执行时需要额外记录真实输入、每一步输出/状态、最终 trace 或测试结果，而不是只保留架构图。

## Verify

- Core 扩展名表零修改。
- .foo 可发现可读取。
- provenance 指向外部插件。
- 跨 Workspace 抛 WorkspaceBoundaryError。

## Failure & Troubleshooting

|现象|优先检查|
|---|---|
|Runtime 能读但 Workspace 不显示|检查 Workspace 使用的 Catalog 是否来自同一 Registry。|
|跨 Workspace 仍能读|检查 Ref 是否携带 workspace_id，以及 Reader 是否收到 originating Workspace。|

## Operationalize

完成后至少保留：

- 实现或最小实验代码；
- 对应 Contract / schema；
- 正向与失败路径测试；
- 一份可观察结果（trace / provenance / checkpoint / ContextResult 等，视概念而定）；
- 对“当前实现选择”与“概念不变量”的区分说明。

## 完成标准

你应能同时回答：

1. HMBuddy 当前怎么做；
2. 为什么这样分层；
3. 一个关键条件变化后哪里失效；
4. 自己实现时从哪开始、怎样验证、怎样排错。

本概念 D → R → L → P 闭环完成。
