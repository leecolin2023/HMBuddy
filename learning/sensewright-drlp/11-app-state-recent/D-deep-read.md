# D — Deep Read：AppState / Recent Workspace / Recent Activity：轻量恢复而非 Task 域

> SenseWright：**Deep Read V6.4 / Coverage-Preserving**  
> HMBuddy Source Baseline：`14b79558cf25bba31a971fe144d83c145d9e7b46`  
> 当前状态：**Phase 2.1 已实现，2.1.1 统一 Workspace ID 与隐私语义**

## 阅读任务

只恢复 HMBuddy 当前源码/Canonical Architecture 自己建立的认知结构，不独立批判、不用外部框架改写它。

> **为什么最近活动只能表示“从哪里重新进入”，不能被当成任务执行状态？**

## Raw Source

- `application/state.py`
- `application/recent.py`
- `desktop/controller.py`
- `tests/test_phase2_1_state.py`
- `tests/test_phase2_1_1_hardening.py`

## 认知拓扑

```text
User activity
→ AppState metadata
→ RecentWorkspace / RecentActivity
→ stable entry_id/workspace_id
→ UI resume_view
→ re-enter Product surface
```

## 独立认知单元

1. Config 与 State 独立持久化。
2. RecentWorkspace 使用 Core make_workspace_id，跨重启稳定。
3. RecentActivityEntry 只有 activity_type、workspace/artifact path、title、resume_view 等导航元数据。
4. QA Activity 不再保存用户问题正文，降低内网敏感信息落盘。
5. entry_id 用于稳定 UI 选择，不依赖列表 index。
6. 损坏 state 可归档并重建，不阻断核心 Runtime。
7. 明确禁止在 State 中出现 Session/Tool stack/Prompt/Answer/Provider/Thread。

## 认知发动机

AppState 解决桌面产品的连续性，不解决 Agent 执行的一致性。它必须足够轻，坏了可以重建；真正 Session 则是未来 Kernel durable state。

## 当前边界

- Recent Activity ≠ Session。
- resume_view ≠ checkpoint。
- State 不存正文与隐藏模型状态。

## Coverage Reconciliation

本篇覆盖的是与该概念有独立语义的：**角色、输入输出、控制权、调用关系、当前实现状态、明确非目标与演进接口**。未来概念只按 Canonical Architecture 恢复其目标语义，不把设计目标升级为当前事实。

## 压缩后的认知模型

- AppState = rebuildable product history；Session = durable agent work context。

Deep Read 到此只回答“HMBuddy 在说什么、为什么这样组织”。判断是否站得住交给同目录 Review。

下一步：[R-review.md](./R-review.md)
