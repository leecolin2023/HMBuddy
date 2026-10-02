"""Plugin Loader（规格第 15 节）。

- FR-L01：API Version 校验在 Manifest 阶段已完成，不兼容直接拒绝；
- FR-L02：Entrypoint 不存在 / 类不符合 Contract → 标记 load_failed；
- FR-L03：单插件加载失败不影响整体（由 Runtime 装配层逐个 try）；
- FR-L04：重复 plugin_id 拒绝并记录冲突来源。
"""
from __future__ import annotations

import importlib
import importlib.util
import sys
import uuid
from dataclasses import dataclass, field

from .discovery import DiscoveredPlugin
from .errors import DuplicatePluginError, PluginLoadError


@dataclass
class LoadedPlugin:
    plugin: object
    discovered: DiscoveredPlugin


@dataclass
class LoadReport:
    loaded: list[LoadedPlugin] = field(default_factory=list)
    failures: list[tuple[str, str]] = field(default_factory=list)  # (plugin 标识, 原因)

    @property
    def ok(self) -> bool:
        return not self.failures


def _load_builtin_class(manifest) -> type:
    """内置插件：按 entrypoint.module 常规包导入。"""
    try:
        module = importlib.import_module(manifest.entrypoint_module)
    except Exception as exc:
        raise PluginLoadError(
            f"plugin {manifest.id!r}: cannot import module "
            f"{manifest.entrypoint_module!r}: {exc!r}"
        ) from exc
    return getattr(module, manifest.entrypoint_class, None)


def _load_external_class(manifest, plugin_dir) -> type:
    """外部插件：按文件路径加载（不依赖 sys.path，模块名随机化避免冲突）。"""
    file_name = manifest.entrypoint_module.split(".")[-1] or "plugin"
    module_path = plugin_dir / f"{file_name}.py"
    if not module_path.is_file():
        raise PluginLoadError(
            f"plugin {manifest.id!r}: entrypoint file not found: {module_path}"
        )
    spec = importlib.util.spec_from_file_location(
        f"hmbuddy_external_plugin_{uuid.uuid4().hex}", module_path
    )
    if spec is None or spec.loader is None:
        raise PluginLoadError(f"plugin {manifest.id!r}: cannot create import spec")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        raise PluginLoadError(
            f"plugin {manifest.id!r}: import failed for {module_path}: {exc!r}"
        ) from exc
    return getattr(module, manifest.entrypoint_class, None)


def load_plugin(discovered: DiscoveredPlugin) -> LoadedPlugin:
    """加载单个插件：实例化 Plugin 类并校验 Contract（FR-L02）。"""
    manifest = discovered.manifest
    if discovered.source == "external":
        plugin_class = _load_external_class(manifest, discovered.plugin_dir)
    else:
        plugin_class = _load_builtin_class(manifest)

    if plugin_class is None:
        raise PluginLoadError(
            f"plugin {manifest.id!r}: entrypoint class "
            f"{manifest.entrypoint_class!r} not found in {manifest.entrypoint_module!r}"
        )

    try:
        instance = plugin_class()
    except Exception as exc:
        raise PluginLoadError(
            f"plugin {manifest.id!r} constructor failed: {exc!r}"
        ) from exc

    providers = getattr(instance, "providers", None)
    if not callable(providers):
        raise PluginLoadError(
            f"plugin {manifest.id!r}: entrypoint class "
            f"{manifest.entrypoint_class!r} does not satisfy the Plugin contract "
            "(missing providers())"
        )
    try:
        provider_list = list(providers())
    except Exception as exc:
        raise PluginLoadError(
            f"plugin {manifest.id!r} providers() failed: {exc!r}"
        ) from exc

    if not provider_list:
        raise PluginLoadError(f"plugin {manifest.id!r}: providers() returned nothing")

    declared_capabilities = set(manifest.capability_ids())
    for provider in provider_list:
        missing = [
            attr
            for attr in ("capability_id", "provider_id", "supports", "is_available", "execute")
            if not hasattr(provider, attr)
        ]
        if missing:
            raise PluginLoadError(
                f"plugin {manifest.id!r}: provider {provider!r} missing {missing}"
            )
        # FR-M04：Provider 只能提供 Manifest 已声明的能力
        if getattr(provider, "capability_id", "") not in declared_capabilities:
            raise PluginLoadError(
                f"plugin {manifest.id!r}: provider {provider.provider_id!r} "
                f"claims capability {getattr(provider, 'capability_id', '')!r} "
                f"which is not declared in the manifest"
            )
        provider.plugin_id = provider.plugin_id or manifest.id
        provider.plugin_version = provider.plugin_version or manifest.version
        # 权限声明随 Provider 下发，供 Runtime Policy 计算 effective grant（AC-07）
        provider.declared_permissions = tuple(manifest.permissions)

    return LoadedPlugin(plugin=instance, discovered=discovered)


def check_duplicate_plugin_id(loaded: list[LoadedPlugin]) -> None:
    """FR-L04：重复 plugin_id 拒绝加载，不静默覆盖。"""
    seen: dict[str, DiscoveredPlugin] = {}
    for item in loaded:
        plugin_id = item.discovered.manifest.id
        if plugin_id in seen:
            raise DuplicatePluginError(
                f"duplicate plugin id {plugin_id!r}: "
                f"{seen[plugin_id].plugin_dir} and {item.discovered.plugin_dir}",
                plugin_id=plugin_id,
            )
        seen[plugin_id] = item.discovered
