# L — Learning：Tool / Agent Loop：从问答到自主行动

> SenseWright：System Learning V0.5.3  
> 路径：Ground → Run Once → Explain → Vary One Condition → Model → Use

## Ground Object

用户说“在这个工作区找到最新授信方案，并总结期限和担保条件”，但没有先选文件。

## Run Once

1. 当前系统无法自主选择文件。
2. 最小 Agent 先调用 workspace.list。
3. 候选多时需要 outline/search，而不是全读。
4. 模型选择 Ref 后调用受控 read。
5. Tool Result 写入 Agent State，成为下一轮 Observation。
6. 模型基于证据回答并在 step budget 内停止。

## 为什么每一步存在

- 机制本质是 State→Action→Environment→Observation→State。
- Runtime 决定动作能否执行，Agent 决定想做什么。
- Tool Result 必须有限、结构化、可追踪。

## Boundary Variation

只改变一个条件：

> **只取消“用户先选文件”这一人工步骤，要求模型自己选。**

观察：

- 单 Artifact QA 立即不够。
- 出现文件列表/搜索工具、State、Action trace、budget 等新需求。
- Artifact/Plugin Runtime 仍然可复用。
- 说明 Agent 是控制权变化带来的工程需求，不是 UI 标签。

## Knowledge Model

- Agent Loop = State → Decide → Act → Observe → Update → Stop。
- Application/Agent 选 Tool/Capability，Runtime 继续管 Provider/Policy。
- 第一版应 read-only + bounded + traceable。

## Gap

- 模型可见 Tool schema。
- Agent State/termination。
- Workspace search/outline/range。
- 未来 side-effect confirmation。

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
