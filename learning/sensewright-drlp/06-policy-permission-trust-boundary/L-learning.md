# L — Learning：Policy / Permission / Trust Boundary：运行时安全边界

> SenseWright：System Learning V0.5.3  
> 路径：Ground → Run Once → Explain → Vary One Condition → Model → Use

## Ground Object

读取旧 .doc，需要 Word/WPS COM；默认 Policy 只给 filesystem.read。

## Run Once

1. Workspace/Reader 校验路径。
2. Router 找到 doc Provider。
3. Runtime 读取 required_permissions。
4. 缺 office.com，execute 前抛 PluginPermissionError。
5. 错误不 fallback，COM 调用次数应为 0。

## 为什么每一步存在

- 事后日志无法阻止副作用。
- 动态 gate 让低权限路径可执行、高权限路径再申请。
- 安全错误若 fallback，可能被另一个 Provider 绕过。

## Boundary Variation

只改变一个条件：

> **只把 Policy 改成显式授予 office.com。**

观察：

- Manifest/Workspace/Provider 都不变。
- pre-check 通过后 Provider 才可进入 COM。
- 未声明的其他权限仍会被 dynamic gate 拒绝。

## Knowledge Model

- Trust Boundary = Workspace + Manifest declaration + Runtime grant + execution gate + trace。
- Declared ≠ Granted ≠ Used。
- 进入 Agent 写操作前，应先升级 side-effect safety。

## Gap

- 第三方插件隔离。
- 写操作范围化授权。
- 企业策略来源/审计。

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
