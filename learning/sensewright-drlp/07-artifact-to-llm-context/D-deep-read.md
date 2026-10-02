# D — Deep Read：Artifact → LLM Context：模型上下文编译层

> SenseWright：Deep Read V6.4 · Coverage-Preserving  
> HMBuddy 基线：`6eb16968c31b7fbbae377eadd6b670287d69b27a` · 状态：已实现并完成 Context Hardening

## 任务

只恢复 HMBuddy 自身结构，不评价、不外推。核心问题：

> **为什么文件解析正确仍不等于 LLM 看到了正确内容？**

## Raw Source

- `llm/context.py`
- `llm/client.py`
- `evals/test_context.py`
- `evals/test_context_hardening.py`

## 认知拓扑

```text
Artifact
→ 按 block_type 序列化
→ 应用 chars/blocks/table rows 预算
→ 插入截断/OCR/缺失标记
→ ContextBuildResult
→ LLM
```

## 独立认知单元

1. Artifact 是程序 IR，Context 是模型实际可见的线性表示。
2. 默认 ContextPolicy 为 max_chars=20000、max_blocks=500、max_table_rows=200。
3. 截断通过 truncated/omitted_blocks/reason/warnings 与文本 marker 显式暴露。
4. 解析期表格截断与 Context 渲染截断都必须可见。
5. PDF 页级 requires_ocr 会进入 Context。
6. 绝对路径默认不进入模型输入。
7. SYSTEM_PROMPT 禁止在出现截断时声称完整审阅。

## 认知发动机

Parser correctness 只证明事实进入了 IR；Context 还要在有限窗口里忠实、有限、可解释地把 IR 暴露给模型。静默裁剪会让正确 Parser 产生错误答案。

## 当前边界

- 字符预算不是精确 token 预算。
- 当前主要是顺序前缀，不是 question-aware retrieval。
- Context 不负责解析源文件。
- warning 能诚实说明缺失，但不能自动找回被裁掉事实。

## 压缩后的模型

> **Artifact = 系统知道什么；Context = 模型这次真正看到什么。**

这句话不能替代前面的机制。Deep Read 的目标是能替代理解性重读，但精确行为仍应回 Raw Source 核验。

## Acceptance Gate

- [x] 覆盖与本概念有关的当前实现/规格。
- [x] 没把未来能力写成现状。
- [x] 保留关键责任转移与边界。
- [x] 没用外部框架改写 HMBuddy 自己的设计。

下一步：[R-review.md](./R-review.md)
