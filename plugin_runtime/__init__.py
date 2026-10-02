"""Plugin Runtime 装配层（规格 Step 4 / G2 + BUG-004 修订）：发现 → 加载 → 注册 → Runtime。

Core 不通过静态列表知道具体实现；上层只面向 execute(CapabilityRequest)。
Registry 只注册 Loader 已校验的那批 Provider 实例（AC-H04），
禁止再次调用 plugin.providers()。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .contracts import PluginContext  # noqa: F401
from .discovery import (
    DiscoveryReport,
    discover_builtin,
    discover_external,
    external_plugin_dirs_from_env,
)
from .errors import PluginLoadError, PluginRuntimeError
from .loader import LoadReport, load_plugin
from .policy import PermissionPolicy
from .registry import CapabilityRegistry
from .runtime import CapabilityRuntime


@dataclass
class RuntimeAssembly:
    runtime: CapabilityRuntime
    discovery: DiscoveryReport
    load_report: LoadReport
    registry: CapabilityRegistry
    # Phase 2.1：被用户配置禁用的插件（已发现、未加载、不进 Effective Registry）
    disabled: list[DiscoveredPlugin] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.discovery.errors and not self.load_report.failures

    def disabled_extensions(self) -> set[str]:
        """被禁用插件声明的扩展名集合（用于 ER-06 精确提示）。"""
        extensions: set[str] = set()
        for discovered in self.disabled:
            extensions.update(discovered.manifest.extensions)
        return extensions


def assemble_runtime(
    *,
    external_plugin_dirs: list[Path] | None = None,
    use_env_plugin_path: bool = True,
    policy: PermissionPolicy | None = None,
    max_traces: int | None = None,
    disabled_plugin_ids: set[str] | None = None,
) -> RuntimeAssembly:
    """执行完整的 发现 → 校验 Manifest → 应用禁用名单 → 加载 → 注册 流程，
    输出可观察的装配报告（Phase 2.1 规格第 28 节 Rescan 链路）。

    单个插件失败被隔离记录（FR-L03），不阻断其他插件。
    """
    disabled_ids = {str(item) for item in (disabled_plugin_ids or set())}
    discovery = discover_builtin()
    dirs = list(external_plugin_dirs or [])
    if use_env_plugin_path:
        dirs = external_plugin_dirs_from_env() + dirs
    discover_external(dirs, report=discovery)

    registry = CapabilityRegistry()
    load_report = LoadReport()
    seen_plugin_ids: set[str] = set()
    disabled: list[DiscoveredPlugin] = []

    for discovered in discovery.all_plugins:
        plugin_id = discovered.manifest.id
        if plugin_id in seen_plugin_ids:
            # FR-L04：重复 plugin_id 拒绝并记录冲突来源，不静默覆盖
            load_report.failures.append(
                (
                    plugin_id,
                    f"duplicate plugin id (conflict with an already-loaded plugin; "
                    f"current dir: {discovered.plugin_dir})",
                )
            )
            continue
        if plugin_id in disabled_ids:
            # Phase 2.1：Disabled 插件仍可 Discovery / 展示 Manifest，
            # 但不进入 Effective Registry、不参与 Routing（规格第 24 节）
            disabled.append(discovered)
            continue
        try:
            loaded = load_plugin(discovered)
        except PluginRuntimeError as exc:
            load_report.failures.append((plugin_id, str(exc)))
            continue
        seen_plugin_ids.add(plugin_id)
        load_report.loaded.append(loaded)
        # BUG-004 / AC-H04：只注册 Loader 校验过的同一批 Provider 实例
        for provider in loaded.providers:
            try:
                registry.register(provider)
            except (PluginRuntimeError, ValueError) as exc:
                load_report.failures.append(
                    (plugin_id, f"provider registration failed: {exc}")
                )

    runtime_kwargs = {"policy": policy}
    if max_traces is not None:
        runtime_kwargs["max_traces"] = max_traces
    runtime = CapabilityRuntime(registry, **runtime_kwargs)
    return RuntimeAssembly(
        runtime=runtime,
        discovery=discovery,
        load_report=load_report,
        registry=registry,
        disabled=disabled,
    )


_default_assembly: RuntimeAssembly | None = None


def get_default_runtime(force_reload: bool = False) -> RuntimeAssembly:
    """进程级默认 Runtime（内置插件 + HMBUDDY_PLUGIN_PATH 外部插件）。

    测试需要隔离时传 force_reload=True 或自行 assemble_runtime()。
    """
    global _default_assembly
    if _default_assembly is None or force_reload:
        _default_assembly = assemble_runtime()
        # Runtime 重建后默认 Capability Catalog 必须随之复位（BUG-002）
        from .catalog import reset_default_catalog

        reset_default_catalog()
    return _default_assembly
