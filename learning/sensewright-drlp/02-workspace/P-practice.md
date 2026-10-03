# P — Practice：Workspace：工作域、文件发现与信任边界

> SenseWright：**Practice V0.2 / Knowledge → Execution**

## Real Engineering Scenario

写一个集成案例验证插件启停后 Workspace、File Picker、Reader 三处能力事实同步。

## Engineering Model

- EffectiveConfig → AppRuntime → Catalog → Workspace → Reader。

## End-to-End Implementation

1. 准备 .foo 外部插件与文件。
2. 启用后打开 Workspace，断言 .foo 可见。
3. 禁用插件并触发 save_settings。
4. 断言当前 Workspace refs 立即移除 .foo。
5. 显式路径读取 .foo，断言 CapabilityDisabledError。
6. 重新启用并 rescan，断言恢复。

## One Concrete Path

```text
AppRuntime Catalog → Workspace(root,catalog) → 发现 ArtifactRef → workspace_id/relative_path → ArtifactReader boundary check → Capability Runtime
```

真正执行时，应把一个具体输入沿链路跑完并记录中间状态，而不是只完成目录/类定义。

## Verify

- Plugin Manager/Workspace/File Picker/Reader 看到同一事实。
- 不调用全局 default catalog。

## Failure & Troubleshooting

|现象|优先检查|
|---|---|
|UI 与 Runtime 能力不一致|检查 Controller 是否注入 app_runtime.catalog。|
|Rescan 后旧 refs 未变化|检查 Workspace 是否随 Runtime 重建。|

## Engineering Artifacts

本练习结束时至少留下：

- 对应 Contract / schema /边界说明；
- 最小实现或实验代码；
- 正向 + 关键失败路径测试；
- 一份真实可观察结果（trace / ContextResult / ViewModel / Session record / Diff 等）；
- 对“概念不变量”和“HMBuddy 当前实现选择”的区分。

## Generalize

完成后不要只记 HMBuddy 的文件名。应能迁移回答：换一个格式、Provider、UI、模型或业务场景时，**哪些层不变、哪些层应该替换、什么变化会迫使 Contract 升级**。

本概念 D → R → L → P 闭环完成。
