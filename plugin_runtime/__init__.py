"""Plugin Runtime 装配层（规格 Step 4 / G2）：发现 → 加载 → 注册 → Runtime。

Core 不通过静态列表知道具体实现；上层只面向 execute(CapabilityRequest)。
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

    @property
    def ok(self) -> bool:
        return not self.discovery.errors and not self.load_report.failures


def assemble_runtime(
    *,
    external_plugin_dirs: list[Path] | None = None,
    use_env_plugin_path: bool = True,
    policy: PermissionPolicy | None = None,
) -> RuntimeAssembly:
    """执行完整的 发现 → 加载 → 注册 流程，输出可观察的装配报告。

    单个插件失败被隔离记录（FR-L03），不阻断其他插件。
    """
    discovery = discover_builtin()
    dirs = list(external_plugin_dirs or [])
    if use_env_plugin_path:
        dirs = external_plugin_dirs_from_env() + dirs
    discover_external(dirs, report=discovery)

    registry = CapabilityRegistry()
    load_report = LoadReport()
    seen_plugin_ids: set[str] = set()

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
        try:
            loaded = load_plugin(discovered)
        except PluginRuntimeError as exc:
            load_report.failures.append((plugin_id, str(exc)))
            continue
        seen_plugin_ids.add(plugin_id)
        load_report.loaded.append(loaded)
        for provider in loaded.plugin.providers():
            try:
                registry.register(provider)
            except (PluginRuntimeError, ValueError) as exc:
                load_report.failures.append(
                    (plugin_id, f"provider registration failed: {exc}")
                )

    runtime = CapabilityRuntime(registry, policy)
    return RuntimeAssembly(
        runtime=runtime,
        discovery=discovery,
        load_report=load_report,
        registry=registry,
    )


_default_assembly: RuntimeAssembly | None = None


def get_default_runtime(force_reload: bool = False) -> RuntimeAssembly:
    """进程级默认 Runtime（内置插件 + HMBUDDY_PLUGIN_PATH 外部插件）。

    测试需要隔离时传 force_reload=True 或自行 assemble_runtime()。
    """
    global _default_assembly
    if _default_assembly is None or force_reload:
        _default_assembly = assemble_runtime()
    return _default_assembly
