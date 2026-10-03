# D — Deep Read：Eval / Feedback Loop：从失败模式到可回归证据

> SenseWright：**Deep Read V6.4 / Coverage-Preserving**  
> HMBuddy Source Baseline：`14b79558cf25bba31a971fe144d83c145d9e7b46`  
> 当前状态：**已实现多层 Eval、Phase baseline 与跨平台 CI**

## 阅读任务

只恢复 HMBuddy 当前源码/Canonical Architecture 自己建立的认知结构，不独立批判、不用外部框架改写它。

> **为什么 HMBuddy 的架构迭代必须用失败模式和验收证据驱动，而不是“看起来合理”？**

## Raw Source

- `evals/`
- `tests/`
- `evals/baseline-phase2.2-v0.1.json`
- `.github/workflows/ci.yml`
- `requirements/hmbuddy-architecture-baseline.md`

## 认知拓扑

```text
真实问题/规格
→ Atomic acceptance
→ unit/integration/static guard
→ baseline
→ CI source+wheel
→ 新失败回流
```

## 独立认知单元

1. Parser/Context/Runtime/Application/Desktop 分层测试。
2. Phase baseline 保存 AC、环境、known limitations 和测试计数。
3. 2.1.1 专门由集成缝隙推动，不新增功能。
4. 2.2 使用 AST/static guard 保证 Preview 不绕过 Artifact Runtime、Desktop 不残留 Tkinter。
5. CI 区分 Windows full suite 与 Linux cross-platform core，避免错误的平台期待。
6. Architecture Baseline 要求新抽象来自真实失败模式。

## 认知发动机

测试不是给架构盖章，而是把抽象的边界翻译成可执行证据。越是 Agent/插件系统，越需要证明“哪一层坏了”，否则所有问题都会被误判成模型问题。

## 当前边界

- 测试数量不是质量分。
- 合成 fixture 不替代真实 Office corpus。
- static guard 保护架构边界但不证明用户体验好。

## Coverage Reconciliation

本篇覆盖的是与该概念有独立语义的：**角色、输入输出、控制权、调用关系、当前实现状态、明确非目标与演进接口**。未来概念只按 Canonical Architecture 恢复其目标语义，不把设计目标升级为当前事实。

## 压缩后的认知模型

- 每个真实 failure 最终应变成最小回归证据。
- 分层 Eval 负责定位，端到端 Eval 负责用户任务。

Deep Read 到此只回答“HMBuddy 在说什么、为什么这样组织”。判断是否站得住交给同目录 Review。

下一步：[R-review.md](./R-review.md)
