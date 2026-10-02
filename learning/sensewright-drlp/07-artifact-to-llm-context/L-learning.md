# L — Learning：Artifact → LLM Context：模型上下文编译层

> SenseWright：System Learning V0.5.3  
> 路径：Ground → Run Once → Explain → Vary One Condition → Model → Use

## Ground Object

800 个 paragraph block，答案在第 700 个；默认预算只能容纳前部。

## Run Once

1. Parser 生成完整 800 blocks。
2. build_context 从头遍历。
3. 达到预算后 truncated=true。
4. 文本加入 [Context Truncated]。
5. 模型知道内容不完整，但答案事实没有进入本轮上下文。

## 为什么每一步存在

- Parser 与 answerability 是不同层。
- 扩大窗口只是调参，不能解决多文件相关性。
- 显式缺失是可信底线。

## Boundary Variation

只改变一个条件：

> **把 max_chars 改为 300，Artifact 和问题不变。**

观察：

- Artifact 完整性不变。
- Context 迅速截断。
- 模型证据量改变，而 Parser 测试仍可全绿。
- 说明 Context 必须独立测试。

## Knowledge Model

- Artifact = 系统知道什么；Context = 模型这次真正看到什么。
- Context correctness = faithful serialization + explicit incompleteness + bounded resources。
- 长文档应走 outline/search/range → focused context。

## Gap

- Question-aware selection。
- 多 Artifact composition。
- 复杂表格/图像表示。

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
