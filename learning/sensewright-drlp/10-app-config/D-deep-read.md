# D — Deep Read：AppConfig / EffectiveConfig：配置、来源优先级与本地数据目录

> SenseWright：**Deep Read V6.4 / Coverage-Preserving**  
> HMBuddy Source Baseline：`14b79558cf25bba31a971fe144d83c145d9e7b46`  
> 当前状态：**Phase 2.1 已实现，2.1.1 已加固 False/0 与显式 env**

## 阅读任务

只恢复 HMBuddy 当前源码/Canonical Architecture 自己建立的认知结构，不独立批判、不用外部框架改写它。

> **为什么“用户保存的配置”和“当前真正生效的配置”必须分开？**

## Raw Source

- `application/config.py`
- `tests/test_phase2_1_config.py`
- `tests/test_phase2_1_1_hardening.py`

## 认知拓扑

```text
Built-in Defaults
→ User config.json
→ Environment
→ Runtime Overrides
→ EffectiveConfig + source
→ Runtime Assembly/UI
```

## 独立认知单元

1. AppConfig 保存用户意图；EffectiveConfig 保存按优先级解析后的运行值。
2. 优先级是 Default < User < Environment < Runtime Argument。
3. EffectiveValue 同时保存 value/source/detail，UI 可以解释为什么某设置不生效。
4. Desktop bool/int 用 None 区分“未设置”和显式 False/0，2.1.1 修复了 truthy bug。
5. config.json 原子写，非法配置不阻断启动。
6. Secret 不落盘，只保存 api_key_env；运行时从环境取真正密钥。
7. per-user data dir 与源码/Workspace 分离。

## 认知发动机

配置系统的关键不是读 JSON，而是区分‘desired config’与‘effective runtime reality’。企业内网常有部署环境覆盖，用户界面必须能解释来源。

## 当前边界

- Config 不是 AppState。
- Runtime object 不持久化进 Config。
- 环境变量来源的值不能让 UI 假装已被用户设置覆盖。

## Coverage Reconciliation

本篇覆盖的是与该概念有独立语义的：**角色、输入输出、控制权、调用关系、当前实现状态、明确非目标与演进接口**。未来概念只按 Canonical Architecture 恢复其目标语义，不把设计目标升级为当前事实。

## 压缩后的认知模型

- AppConfig = desired settings；EffectiveConfig = resolved runtime truth。

Deep Read 到此只回答“HMBuddy 在说什么、为什么这样组织”。判断是否站得住交给同目录 Review。

下一步：[R-review.md](./R-review.md)
