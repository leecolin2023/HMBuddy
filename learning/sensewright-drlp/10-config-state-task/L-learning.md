# L — Learning：Config vs State vs Task：应用状态与任务状态

> SenseWright：System Learning V0.5.3  
> 路径：Ground → Run Once → Explain → Vary One Condition → Model → Use

## Ground Object

用户配置 model=qwen，公司环境变量覆盖为 deepseek；昨天还打开过一个 Workspace。

## Run Once

1. ConfigService 读取 defaults+file。
2. env 层覆盖 model=deepseek，并记录 source。
3. AppState 读取 recent workspace/task。
4. Home 可导航回昨天位置。
5. 如果未来 Agent 做到步骤 7/20，RecentTaskEntry 并不足以恢复执行。

## 为什么每一步存在

- Config 是 desired behavior，State 是 observed history。
- 部署 override 不能被 UI 静默覆盖。
- 持久化纯数据引用便于重启后重建运行对象。

## Boundary Variation

只改变一个条件：

> **把 Config、AppState、Recent Task 全塞进一个 hmbuddy.json 并统一原地覆盖。**

观察：

- 自动更新最近记录会频繁重写配置。
- 清理历史可能误删设置。
- 未来 Task checkpoint 会把配置文件变成事务日志。
- 分离是生命周期边界，不是目录洁癖。

## Knowledge Model

- Config = desired behavior；State = recent application history；Persistent Task = durable execution progress。
- Recent 解决“回到哪里”，Task Runtime 解决“从哪一步继续”。
- 先设计生命周期/一致性，再选 JSON/SQLite。

## Gap

- Phase 2.1 application services。
- 真实 Task schema/checkpoint。
- Plugin reload 原子切换。

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
