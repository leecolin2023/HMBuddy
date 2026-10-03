# P — Practice：Application Runtime Composition：Controller 与单一运行时事实

> SenseWright：**Practice V0.2 / Knowledge → Execution**

## Real Engineering Scenario

对一次 Settings change 画并测试完整重建图，确保没有组件继续持有旧 Catalog/LLM。

## Engineering Model

- Config mutation → effective resolution → assembly replacement → dependent object refresh。

## End-to-End Implementation

1. 打开 Workspace。
2. 记录旧 runtime/catalog id。
3. 改变 plugin config。
4. save_settings。
5. 断言 runtime/catalog/reader/workspace refs 都更新。
6. 检查 UI view。

## One Concrete Path

```text
Resolve Paths → Load Config/State → Resolve EffectiveConfig → assemble_app_runtime → Catalog + Plugin Views + LLM → AppController → PySide6 Shell
```

真正执行时，应把一个具体输入沿链路跑完并记录中间状态，而不是只完成目录/类定义。

## Verify

- 不存在两套能力事实。
- 显式 env 沿用。

## Failure & Troubleshooting

|现象|优先检查|
|---|---|
|设置页正确但 Workspace 不变|有 stale object。|
|测试注入 env 与运行结果不同|某层又读 os.environ。|

## Engineering Artifacts

本练习结束时至少留下：

- 对应 Contract / schema /边界说明；
- 最小实现或实验代码；
- 正向 + 关键失败路径测试；
- 一份真实可观察结果（trace / ContextResult / ViewModel / Session record / Diff 等）；
- 对“概念不变量”和“HMBuddy 当前实现选择”的区分。

## Generalize

完成后不要只记 HMBuddy 的文件名。应能迁移回答：换一个格式、Provider、UI、模型或业务场景时，**哪些层不变、哪些层应该替换、什么变化会迫使 Contract 升级**。

本概念 D → R → L → P 闭环完成。
