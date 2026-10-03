# D — Deep Read：Tool / ToolRegistry：模型动作接口与 Capability 的桥

> SenseWright：**Deep Read V6.4 / Coverage-Preserving**  
> HMBuddy Source Baseline：`14b79558cf25bba31a971fe144d83c145d9e7b46`  
> 当前状态：**Canonical future Kernel primitive；未实现**

## 阅读任务

只恢复 HMBuddy 当前源码/Canonical Architecture 自己建立的认知结构，不独立批判、不用外部框架改写它。

> **为什么 Agent 应看到少量 read_file/search_files，而不是几十个 artifact.* capability 或 read_docx/read_pdf？**

## Raw Source

- `requirements/hmbuddy-architecture-baseline.md`
- `plugin_runtime/contracts.py`
- `services/artifact_reader.py`

## 认知拓扑

```text
Model Tool Call
→ ToolRegistry schema/validation
→ Tool handler
→ Facade/Capability Runtime
→ ToolResult
```

## 独立认知单元

1. Tool 面向模型；Capability 面向 Runtime；Provider/Adapter 面向实现。
2. 推荐首批 Tool：list_files、search_files、read_file、create_file、edit_file、validate_file。
3. read_file 可以内部选择 full/range/outline capability。
4. ToolRegistry 负责 schema、lookup、参数校验、执行入口。
5. Agent 不知道 Provider。

## 认知发动机

模型需要的是稳定、语义清晰、数量有限的动作空间；Runtime 需要的是细粒度可路由能力。Tool 层负责把两者解耦。

## 当前边界

- Tool 不直接读文件。
- 不要每种格式一个 Tool。
- ToolResult 应是有限纯数据/Artifact ref，不返回任意 Python object。

## Coverage Reconciliation

本篇覆盖的是与该概念有独立语义的：**角色、输入输出、控制权、调用关系、当前实现状态、明确非目标与演进接口**。未来概念只按 Canonical Architecture 恢复其目标语义，不把设计目标升级为当前事实。

## 压缩后的认知模型

- Tool = model-facing action；Capability = runtime-facing service intent。

Deep Read 到此只回答“HMBuddy 在说什么、为什么这样组织”。判断是否站得住交给同目录 Review。

下一步：[R-review.md](./R-review.md)
