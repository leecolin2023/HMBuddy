# L — Learning：Plugin Runtime：发现、装载、注册、路由与执行

> SenseWright：System Learning V0.5.3  
> 路径：Ground → Run Once → Explain → Vary One Condition → Model → Use

## Ground Object

.md 同时有内置 Provider 与 priority 更高的外部 Provider。

## Run Once

1. Discovery 找到两个 Manifest。
2. Loader 校验并物化 Provider。
3. Registry 在 artifact.read.full 下登记候选。
4. Router 做 supports/availability。
5. 高 priority Provider 先执行。
6. 解析类失败可 fallback；权限/边界错误立即停止。

## 为什么每一步存在

- 非法 Manifest 应在代码执行前被拒绝。
- Registry 与 Router 分开，区分“有哪些实现”和“当前选哪个”。
- Runtime 掌握执行才能统一权限、fallback 与 trace。

## Boundary Variation

只改变一个条件：

> **把外部 Provider priority 从 100 改成 40。**

观察：

- 两个 Provider 都继续存在。
- 首选切换为内置 priority 50。
- Application/Facade 完全不变。
- priority 是 Runtime policy。

## Knowledge Model

- Manifest=声明；Discovery=找到；Loader=进入代码；Registry=目录；Router=选择；Runtime=执行治理。
- 插件化不只是动态 import，而是完整控制面。
- 新增能力必须贯穿 Workspace、Runtime、权限、错误、Eval。

## Gap

- Plugin Manager/reload。
- 不可信插件隔离。
- 质量/成本策略。

## 迁移到别的项目时怎么问

- 这个概念在系统里拥有哪一段控制权？
- 它的输入输出是否是稳定 Contract，还是某个实现对象？
- 改变刚才这个条件后，哪些结论仍成立、哪些立即失效？
- 失败时能否定位到本层，而不是统一归因给“模型不行”？

## Acceptance Gate

- [x] 概念已映射到真实 HMBuddy 对象。
- [x] 至少一条具体链路完整跑过。
- [x] 解释了关键步骤为何存在。
- [x] 只变化一个高信息量条件。
- [x] 明确当前模型的适用边界。

下一步：[P-practice.md](./P-practice.md)
