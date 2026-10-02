"""Capability Catalog（BUG-002 / 规格 5.2、22 节）。

向 Workspace 等只关心"当前能不能处理某扩展名"的组件提供轻量能力视图；
Workspace 不再维护静态支持格式表（AC-H14），也不感知插件实现。
"""
from __future__ import annotations


class CapabilityCatalog:
    """基于 CapabilityRegistry 的能力目录。"""

    def __init__(self, registry, capability: str = "artifact.read.full"):
        self._registry = registry
        self._capability = capability

    def artifact_extensions(self) -> set[str]:
        """当前 Runtime 能读取的全部扩展名（小写、带点）。"""
        return set(self._registry.extensions_claimed())

    def can_handle_extension(self, extension: str) -> bool:
        ext = _normalize_ext(extension)
        return ext in self.artifact_extensions()

    def providers_for(self, extension: str) -> list:
        """声明支持该扩展名的 Provider（按 priority 有序）。"""
        ext = _normalize_ext(extension)
        return [
            provider
            for provider in self._registry.list_providers(self._capability)
            if ext in getattr(provider, "extensions", ())
        ]

    def artifact_type_for(self, extension: str) -> str:
        """由扩展名推导展示用类型名（去掉点号，小写）。"""
        return _normalize_ext(extension).lstrip(".")


class StaticExtensionCatalog:
    """固定扩展名集合的目录（测试 / UI / 离线场景使用）。"""

    def __init__(self, extensions):
        self._extensions = {_normalize_ext(item) for item in extensions}

    def artifact_extensions(self) -> set[str]:
        return set(self._extensions)

    def can_handle_extension(self, extension: str) -> bool:
        return _normalize_ext(extension) in self._extensions

    def providers_for(self, extension: str) -> list:
        return []

    def artifact_type_for(self, extension: str) -> str:
        return _normalize_ext(extension).lstrip(".")


def _normalize_ext(extension: str) -> str:
    ext = str(extension).lower().strip()
    if ext and not ext.startswith("."):
        ext = "." + ext
    return ext


_default_catalog = None


def get_default_catalog():
    """进程级默认目录：基于默认 Runtime 的 Registry（惰性装配）。"""
    global _default_catalog
    if _default_catalog is None:
        # 延迟导入避免 workspace.workspace ↔ plugin_runtime 的循环导入
        from . import get_default_runtime

        _default_catalog = CapabilityCatalog(get_default_runtime().registry)
    return _default_catalog


def reset_default_catalog() -> None:
    """测试 / Runtime 重建后复位。"""
    global _default_catalog
    _default_catalog = None
