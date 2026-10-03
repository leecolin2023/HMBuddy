# L — Learning：Workspace：工作域、文件发现与信任边界

> SenseWright：**System Learning V0.5.3**  
> 路径：Ground → Run Once → Explain → Vary One Condition → Model → Use

## Ground Object

用户禁用唯一支持 .foo 的插件，同时当前 Workspace 已经打开。

## Run Once

1. Settings 修改 disabled_plugin_ids。
2. Controller 重建 AppRuntime。
3. 新 Runtime 生成新 CapabilityCatalog。
4. Controller 用原 root + 新 Catalog 重建 Workspace。
5. refs 刷新，.foo 不再作为可读 Artifact 出现在列表。

## Mechanism：为什么这样跑

- Workspace 的可发现能力必须与当前 Runtime 同源。
- 否则 Plugin Manager 显示 Disabled，Workspace 却仍展示可读文件，产品事实分裂。

## Boundary Variation

一次只改变一个高信息量条件：

> **只改变一个条件：用户通过系统文件选择器显式选中了已经被禁用的 .foo。**

结果：

- Workspace refs 里可能没有该文件。
- Controller 仍允许请求进入 ArtifactReader。
- Reader/Runtime 应给 CapabilityDisabledError 等明确错误，而不是假装“不支持格式”。

这个变化用来检查当前模型哪些仍成立、哪些削弱、哪些变成新问题，而不是做穷举。

## Knowledge Model

- Workspace = work scope + trust domain + runtime-derived discovery。
- Product/Application 不应维护第二套文件能力事实。

## Gaps

- 语义 Search/Index。
- 未来 Workspace-local Skills/Sessions 的组织。
- 网络盘/虚拟文件系统边界。

这些 Gap 只有在阻塞下一步时才进入实现，不为了“完整”全部提前建设。

## Prediction Check

如果把当前概念放到相邻场景，至少应能预测：

- 哪一层最先受到条件变化影响；
- 哪些 Contract 仍可复用；
- 哪些只是当前实现选择；
- 什么情况下需要回到 Architecture Change / Contract redesign。

## Project to Use

学习完本篇后，面对别的 Agent/办公系统，应先定位：**谁拥有控制权、状态在哪、实现细节在哪一层结束、上层依赖的稳定 Contract 是什么。**

下一步：[P-practice.md](./P-practice.md)
