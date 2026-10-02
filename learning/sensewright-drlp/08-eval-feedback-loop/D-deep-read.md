# D — Deep Read：Eval / Feedback Loop：如何证明系统真的工作

> SenseWright：Deep Read V6.4 · Coverage-Preserving  
> HMBuddy 基线：`6eb16968c31b7fbbae377eadd6b670287d69b27a` · 状态：已实现多层 Eval + CI

## 任务

只恢复 HMBuddy 自身结构，不评价、不外推。核心问题：

> **为什么办公 Agent 的正确性不能只看“程序没报错”或“模型给了答案”？**

## Raw Source

- `evals/`
- `tests/`
- `evals/baseline-phase1.1.1-v0.1.json`
- `.github/workflows/ci.yml`
- `scripts/install_smoke.py`

## 认知拓扑

```text
规格/真实失败
→ fixture/case
→ Parser/Workspace/Context/Runtime 单层 Eval
→ 集成 Eval
→ baseline
→ CI + wheel smoke
→ 新失败回流
```

## 独立认知单元

1. Parser Eval 验证多格式结构。
2. Context Eval 独立验证事实是否进入模型与截断边界。
3. Plugin Runtime Eval 验证 Manifest/权限/fallback/外部插件/trace。
4. QA Eval 与 Mock Client 提供端到端烟测。
5. baseline 记录阶段验收与 known limitations。
6. CI 跨 Python/OS，wheel smoke 防止“源码树能跑但安装包不能跑”。

## 认知发动机

Eval 把“架构看起来合理”转换成“一个具体输入经过系统后必须留下可检查状态”。Agent 错误来源多层，必须先分层归因。

## 当前边界

- 测试数量不是质量分。
- 合成 fixture 不代表真实银行文档分布。
- 关键词 QA 只能做 smoke。
- CI 证明可重复，不证明产品价值。

## 压缩后的模型

> **Eval = Contract × Representative Inputs × Observable Assertions。**

这句话不能替代前面的机制。Deep Read 的目标是能替代理解性重读，但精确行为仍应回 Raw Source 核验。

## Acceptance Gate

- [x] 覆盖与本概念有关的当前实现/规格。
- [x] 没把未来能力写成现状。
- [x] 保留关键责任转移与边界。
- [x] 没用外部框架改写 HMBuddy 自己的设计。

下一步：[R-review.md](./R-review.md)
