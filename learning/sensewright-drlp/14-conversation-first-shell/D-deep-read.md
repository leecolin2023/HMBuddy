# D — Deep Read：Conversation-first Desktop Shell：Product Layer 与 Human-in-the-loop

> SenseWright：**Deep Read V6.4 / Coverage-Preserving**  
> HMBuddy Source Baseline：`14b79558cf25bba31a971fe144d83c145d9e7b46`  
> 当前状态：**Phase 2.2 已实现（PySide6）**

## 阅读任务

只恢复 HMBuddy 当前源码/Canonical Architecture 自己建立的认知结构，不独立批判、不用外部框架改写它。

> **为什么桌面从“文件管理器 + QA Tab”改成 Sidebar + Conversation + Contextual Preview，而 Kernel 可以完全不变？**

## Raw Source

- `requirements/phase-2.2-desktop-ux-shell-redesign-v0.1.md`
- `desktop/shell.py`
- `desktop/widgets/sidebar.py`
- `desktop/widgets/conversation.py`
- `tests/test_phase2_2_desktop_qt.py`

## 认知拓扑

```text
Sidebar work navigation
→ Conversation current work
→ on-demand Preview
→ Controller/Application
→ unchanged Runtime/Domain
```

## 独立认知单元

1. Phase 2.2 只替换 Presentation Shell，不新增 Kernel primitive。
2. Sidebar 负责 Workspace/Recent/Search/Plugins/Settings 导航，不再把 Home/Workspace 当固定一级功能页。
3. Conversation Surface 包含 Header、Message Stream、File Card、Status Notice、Composer。
4. Preview 默认隐藏，作为上下文工作面按需打开。
5. PySide6 替换 Tkinter，旧 UI 完全移除，避免双 UI 长期维护。
6. Conversation-first 是产品心理模型变化，不等于已经有持久 Session。

## 认知发动机

产品 UI 的信息架构可以先向 Agent 产品收敛，而不提前实现 Agent Kernel。这样 UI 为未来 Session/Tool Activity 预留形态，同时 Runtime 仍保持稳定。

## 当前边界

- 新建会话只清临时 UI 状态。
- 搜索只匹配元数据，不做 RAG。
- 当前 QA 仍需要 active Artifact。
- Conversation transcript 不持久化。

## Coverage Reconciliation

本篇覆盖的是与该概念有独立语义的：**角色、输入输出、控制权、调用关系、当前实现状态、明确非目标与演进接口**。未来概念只按 Canonical Architecture 恢复其目标语义，不把设计目标升级为当前事实。

## 压缩后的认知模型

- Conversation-first 是 Product surface；Agent autonomy 是 Kernel control loop。两者独立演进。

Deep Read 到此只回答“HMBuddy 在说什么、为什么这样组织”。判断是否站得住交给同目录 Review。

下一步：[R-review.md](./R-review.md)
