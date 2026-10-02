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
    # BUG-004 / AC-H04：保存已校验的 Provider 实例；Registry 只允许注册这一批，
    # 不得再次调用 plugin.providers()（防止二次物化绕过校验）。
    providers: list = field(default_factory=list)


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
    """外部插件加载（BUG-013 / AC-H13）。

    - 单文件插件：entrypoint.module 无点号 → plugin_dir/<module>.py；
    - 标准包插件：entrypoint.module 含点号（如 hmbuddy_plugin.plugin）→
      以 plugin_dir/<首段>/ 为包根加载，支持包内相对 import；
      模块名随机化避免跨插件冲突，不污染 sys.path。
    """
    module_name = manifest.entrypoint_module
    if "." not in module_name:
        module_path = plugin_dir / f"{module_name}.py"
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

    # 标准 package 插件：以 <plugin_dir>/<首段>/ 为包根
    package_root_name = module_name.split(".", 1)[0]
    package_dir = plugin_dir / package_root_name
    init_file = package_dir / "__init__.py"
    if not init_file.is_file():
        raise PluginLoadError(
            f"plugin {manifest.id!r}: package entrypoint expects "
            f"{init_file} with __init__.py"
        )
    package_name = f"hmbuddy_ext_pkg_{uuid.uuid4().hex}"
    package_spec = importlib.util.spec_from_file_location(
        package_name,
        init_file,
        submodule_search_locations=[str(package_dir)],
    )
    if package_spec is None or package_spec.loader is None:
        raise PluginLoadError(f"plugin {manifest.id!r}: cannot create package spec")
    package_module = importlib.util.module_from_spec(package_spec)
    sys.modules[package_name] = package_module
    try:
        package_spec.loader.exec_module(package_module)
    except Exception as exc:
        raise PluginLoadError(
            f"plugin {manifest.id!r}: package import failed for {init_file}: {exc!r}"
        ) from exc

    subpath = module_name.split(".", 1)[1]
    try:
        submodule = importlib.import_module(f"{package_name}.{subpath}")
    except Exception as exc:
        raise PluginLoadError(
            f"plugin {manifest.id!r}: cannot import submodule "
            f"{module_name!r}: {exc!r}"
        ) from exc
    return getattr(submodule, manifest.entrypoint_class, None)


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
    validated_providers = []
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
        # BUG-003 / AC-H03：Manifest 是唯一权威源，强制注入覆盖 Provider 自设字段
        capability_declaration = next(
            item
            for item in manifest.capabilities
            if item.id == getattr(provider, "capability_id", "")
        )
        provider.plugin_id = manifest.id
        provider.plugin_version = manifest.version
        provider.priority = capability_declaration.priority
        provider.extensions = tuple(manifest.extensions)
        provider.declared_permissions = tuple(manifest.permissions)
        provider.platforms = tuple(manifest.platforms)
        provider.python_requires = manifest.python_requires
        validated_providers.append(provider)

    return LoadedPlugin(plugin=instance, discovered=discovered, providers=validated_providers)


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
