# HMBuddy Concept Learning Map — SenseWright D → R → L → P

这是一套从 HMBuddy 自身代码、规格和失败模式长出来的 Agent 工程学习库。

方法协议：[00-learning-method.md](./00-learning-method.md)

|#|概念|状态|四步|
|---:|---|---|---|
|1|[Workspace：工作空间、发现边界与信任域](./01-workspace/)|已实现|[D](./01-workspace/D-deep-read.md) · [R](./01-workspace/R-review.md) · [L](./01-workspace/L-learning.md) · [P](./01-workspace/P-practice.md)|
|2|[Artifact / ArtifactBlock：统一中间表示](./02-artifact/)|已实现|[D](./02-artifact/D-deep-read.md) · [R](./02-artifact/R-review.md) · [L](./02-artifact/L-learning.md) · [P](./02-artifact/P-practice.md)|
|3|[Adapter / Parsing Boundary：格式解析隔离层](./03-adapter-parsing-boundary/)|已实现|[D](./03-adapter-parsing-boundary/D-deep-read.md) · [R](./03-adapter-parsing-boundary/R-review.md) · [L](./03-adapter-parsing-boundary/L-learning.md) · [P](./03-adapter-parsing-boundary/P-practice.md)|
|4|[Stable Facade + Capability：稳定入口与能力语义](./04-stable-facade-capability/)|artifact.read.full 已实现，其他 capability 仅预留|[D](./04-stable-facade-capability/D-deep-read.md) · [R](./04-stable-facade-capability/R-review.md) · [L](./04-stable-facade-capability/L-learning.md) · [P](./04-stable-facade-capability/P-practice.md)|
|5|[Plugin Runtime：发现、装载、注册、路由与执行](./05-plugin-runtime/)|已实现并完成 Contract Hardening|[D](./05-plugin-runtime/D-deep-read.md) · [R](./05-plugin-runtime/R-review.md) · [L](./05-plugin-runtime/L-learning.md) · [P](./05-plugin-runtime/P-practice.md)|
|6|[Policy / Permission / Trust Boundary：运行时安全边界](./06-policy-permission-trust-boundary/)|Runtime Policy 已实现；不是 OS Sandbox|[D](./06-policy-permission-trust-boundary/D-deep-read.md) · [R](./06-policy-permission-trust-boundary/R-review.md) · [L](./06-policy-permission-trust-boundary/L-learning.md) · [P](./06-policy-permission-trust-boundary/P-practice.md)|
|7|[Artifact → LLM Context：模型上下文编译层](./07-artifact-to-llm-context/)|已实现并完成 Context Hardening|[D](./07-artifact-to-llm-context/D-deep-read.md) · [R](./07-artifact-to-llm-context/R-review.md) · [L](./07-artifact-to-llm-context/L-learning.md) · [P](./07-artifact-to-llm-context/P-practice.md)|
|8|[Eval / Feedback Loop：如何证明系统真的工作](./08-eval-feedback-loop/)|已实现多层 Eval + CI|[D](./08-eval-feedback-loop/D-deep-read.md) · [R](./08-eval-feedback-loop/R-review.md) · [L](./08-eval-feedback-loop/L-learning.md) · [P](./08-eval-feedback-loop/P-practice.md)|
|9|[Human-in-the-loop Desktop：薄应用层与人工控制点](./09-human-in-the-loop-desktop/)|Phase 2 已实现；Phase 2.1 尚为规格|[D](./09-human-in-the-loop-desktop/D-deep-read.md) · [R](./09-human-in-the-loop-desktop/R-review.md) · [L](./09-human-in-the-loop-desktop/L-learning.md) · [P](./09-human-in-the-loop-desktop/P-practice.md)|
|10|[Config vs State vs Task：应用状态与任务状态](./10-config-state-task/)|Phase 2.1 已有规格，尚未见 application/ 实现|[D](./10-config-state-task/D-deep-read.md) · [R](./10-config-state-task/R-review.md) · [L](./10-config-state-task/L-learning.md) · [P](./10-config-state-task/P-practice.md)|
|11|[Tool / Agent Loop：从问答到自主行动](./11-tool-agent-loop/)|未来能力；当前明确不实现|[D](./11-tool-agent-loop/D-deep-read.md) · [R](./11-tool-agent-loop/R-review.md) · [L](./11-tool-agent-loop/L-learning.md) · [P](./11-tool-agent-loop/P-practice.md)|
|12|[Persistent Task / Recovery：任务中断、恢复与幂等](./12-persistent-task-recovery/)|未来能力；Recent Task 目前只是导航入口|[D](./12-persistent-task-recovery/D-deep-read.md) · [R](./12-persistent-task-recovery/R-review.md) · [L](./12-persistent-task-recovery/L-learning.md) · [P](./12-persistent-task-recovery/P-practice.md)|

## 阅读原则

建议按 01 → 12 走完整依赖链。若想先理解 HMBuddy 的核心 IR，可以先读 02 Artifact，再回到 01 Workspace。

前 8 个概念主要解释当前 Runtime；09–10 进入桌面与应用基础；11–12 明确属于未来 Agent Runtime，不会把设计练习写成已实现功能。

每完成一个概念，都应真正执行其 P 文档中的实验/改造，并把结果与 Eval 回填到仓库，而不是只阅读 Markdown。
