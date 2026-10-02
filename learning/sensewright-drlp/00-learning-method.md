# HMBuddy × SenseWright 学习协议

本目录严格使用 SenseWright 当前四个一级认知模式：

- **D — Deep Read V6.4**：直接读 Raw Source，恢复认知拓扑；本学习库默认 Coverage-Preserving。
- **R — Vibe Review V0.10**：重新从 Raw Source 独立审阅；Coverage before Materiality。
- **L — System Learning V0.5.3**：Ground → Run Once → Explain → Vary One Condition → Model → Use。
- **P — Practice V0.2**：真实场景 → Engineering Model → End-to-End → Concrete Path → Verify → Troubleshoot。

## 固定纪律

```text
Raw HMBuddy Source
  ├─ D：恢复“现在怎么做”
  └─ R：独立判断“当前任务下站不站得住”
          ↓
       L：让机制跑起来，并只改变一个高信息量条件
          ↓
       P：编译成可以实施、验证、排错的工程路径
```

- D 与 R 彼此隔离，不把 sibling output 当 evidence。
- L/P 可以参考前序，但 Reference ≠ Evidence。
- Future concept 必须明确标记“尚未实现”。
- 不因追求“完整 Agent 架构”提前加入 Planner、Memory、Multi-Agent。
- 每个概念的 P 都必须有 feedback loop；没有验证与失败路径，不算完成 Practice。

学习基线：HMBuddy `6eb16968c31b7fbbae377eadd6b670287d69b27a`。
