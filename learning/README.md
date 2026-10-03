# Learning

HMBuddy 的学习资料。

## Canonical learning protocol

2026-10-03 起，学习方法切换为：

- HMBuddy × SenseWright Technical Learning Protocol V1.0：./sensewright-drlp/00-learning-method.md

最高原则：

> **没有最低篇幅，没有最高篇幅，没有固定章节数量。一个概念只有在陌生读者能够解释它、跟踪一次真实运行、预测一个相邻条件变化，并能够开始真实实施，而不需要自行脑补关键步骤时，才算完成。**

## First quality baseline

当前只重建一个概念作为质量样板：

- Pi AgentSession / Tool Calling Vertical Slice：./sensewright-drlp/00-quality-baseline-pi-agentsession-tool-calling/README.md

状态：

~~~text
D/R: SOURCE-GROUNDED
L: MECHANISM-VALIDATED
P: EXECUTION-READY, HMBuddy runtime pending
~~~

Pi upstream 的机制已有 checked deterministic test 作为真实执行证据；HMBuddy VNext-01 尚未在本仓库实际跑完 T1–T4，因此暂不标记 QUALITY-BASELINE。

## Legacy learning map

原 SenseWright D → R → L → P 概念地图 V0.2 基于旧 V0.2 “Pi-like Minimal Harness” 架构批量形成。

它当前有两个问题：

1. 架构已被 Pi-native V1.0 取代；
2. 大量 D/R/L/P 产物压缩过度，更接近概念卡片，而不是陌生人可读的学习材料。

因此继续保留作为：

- 历史材料；
- 旧代码索引；
- 可迁移算法线索；

但不再作为当前学习质量标准。

在首个质量样板完成真实 HMBuddy Practice 验证之前，不批量重写旧 23 个概念。

## Current architecture

当前 Canonical Architecture：

- ../requirements/hmbuddy-architecture-baseline.md

学习方向：

~~~text
Pi-owned concept
→ read real Pi source
→ understand why
→ trace a real execution
→ vary one condition
→ practice through Pi public seam
→ map remaining HMBuddy Office gap

HMBuddy-owned Office concept
→ read current HMBuddy code / tests
→ run real Office case
→ inspect structure / state / failure
→ implement / validate / troubleshoot
~~~
