"""Capability Registry（规格第 16 节）。

内部索引按 capability 组织，支持多 Provider、priority 与确定性排序；
不把"扩展名 → 具体适配器类"作为唯一索引模型。
"""
from __future__ import annotations

from .contracts import CapabilityRequest
from .errors import CapabilityNotFoundError, DuplicatePluginError


class CapabilityRegistry:
    def __init__(self) -> None:
        # capability_id → [provider, ...]（保持注册顺序，resolve 时排序）
        self._by_capability: dict[str, list] = {}
        # (capability_id, provider_id) → provider，用于重复检测
        self._by_provider: dict[tuple[str, str], object] = {}
        # plugin_id → [provider, ...]
        self._by_plugin: dict[str, list] = {}

    # ------------------------------------------------------------------
    # 注册
    # ------------------------------------------------------------------

    def register(self, provider) -> None:
        capability_id = getattr(provider, "capability_id", "")
        provider_id = getattr(provider, "provider_id", "")
        if not capability_id or not provider_id:
            raise ValueError(
                "provider must define capability_id and provider_id: "
                f"{provider!r}"
            )
        key = (capability_id, provider_id)
        if key in self._by_provider:
            existing = self._by_provider[key]
            raise DuplicatePluginError(
                f"duplicate provider registration: capability={capability_id!r} "
                f"provider_id={provider_id!r} "
                f"(already registered by plugin "
                f"{getattr(existing, 'plugin_id', '?')!r}, "
                f"conflict from plugin {getattr(provider, 'plugin_id', '?')!r})",
                plugin_id=getattr(provider, "plugin_id", None),
            )
        self._by_provider[key] = provider
        self._by_capability.setdefault(capability_id, []).append(provider)
        self._by_plugin.setdefault(getattr(provider, "plugin_id", ""), []).append(provider)

    # ------------------------------------------------------------------
    # 查询
    # ------------------------------------------------------------------

    def list_capabilities(self) -> list[str]:
        return sorted(self._by_capability)

    def list_providers(self, capability: str) -> list:
        """返回该 capability 的候选 Provider：priority 从高到低，
        provider_id 字母序作为确定性 tie-break（FR-R02 / AC-05）。"""
        candidates = list(self._by_capability.get(capability, []))
        candidates.sort(key=lambda p: (-int(getattr(p, "priority", 100)), str(p.provider_id)))
        return candidates

    def list_all_providers(self) -> list:
        providers: list = []
        for capability in self.list_capabilities():
            providers.extend(self.list_providers(capability))
        return providers

    def providers_for_plugin(self, plugin_id: str) -> list:
        return list(self._by_plugin.get(plugin_id, []))

    def has_capability(self, capability: str) -> bool:
        return capability in self._by_capability

    def extensions_claimed(self) -> set[str]:
        """所有 Provider 声明的扩展名集合（用于 ER-01 兼容映射）。"""
        claimed: set[str] = set()
        for provider in self._by_provider.values():
            claimed.update(getattr(provider, "extensions", ()) or ())
        return claimed

    def resolve(self, request: CapabilityRequest) -> list:
        """按 priority 返回候选 Provider（不做 supports / availability 过滤，
        过滤属于 Router 职责，规格第 17 节）。capability 完全未知时抛错。"""
        if not self.has_capability(request.capability):
            raise CapabilityNotFoundError(
                request.capability,
                "capability is not registered by any plugin",
            )
        return self.list_providers(request.capability)
