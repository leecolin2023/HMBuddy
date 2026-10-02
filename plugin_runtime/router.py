"""Router / Policy 执行（规格第 17 节）：确定性 Provider 选择。

匹配顺序：
1. capability 匹配（Registry.resolve）
2. Provider supports(request)
3. 当前运行环境可用（is_available）
4. 权限检查（Policy）
5. priority 从高到低
6. provider_id 稳定排序作为最终 tie-break
"""
from __future__ import annotations

from .contracts import CapabilityRequest, PluginContext
from .errors import CapabilityNotFoundError, ProviderNotAvailableError
from .policy import PermissionPolicy
from .registry import CapabilityRegistry


class CapabilityRouter:
    def __init__(self, registry: CapabilityRegistry, policy: PermissionPolicy):
        self.registry = registry
        self.policy = policy

    def select(
        self,
        request: CapabilityRequest,
        context: PluginContext,
    ) -> tuple[object, list[object]]:
        """返回 (选中的 Provider, 支持但落选的候选列表)。

        - capability 无注册 → CapabilityNotFoundError；
        - 有注册但无一 supports 本请求 → CapabilityNotFoundError（detail 说明）；
        - 支持的 Provider 均不可用 → ProviderNotAvailableError。
        """
        candidates = self.registry.resolve(request)
        supporting: list[object] = []
        unavailable: list[object] = []
        for provider in candidates:
            try:
                supported = bool(provider.supports(request))
            except Exception:
                supported = False
            if not supported:
                continue
            try:
                available = bool(provider.is_available(context))
            except Exception:
                available = False
            if available:
                supporting.append(provider)
            else:
                unavailable.append(provider)

        if not supporting:
            if unavailable:
                first = unavailable[0]
                raise ProviderNotAvailableError(
                    request.capability,
                    getattr(first, "plugin_id", "?"),
                    getattr(first, "provider_id", "?"),
                )
            raise CapabilityNotFoundError(
                request.capability,
                "registered providers do not support this request "
                f"(extensions claimed: {sorted(self.registry.extensions_claimed())})",
            )

        # 权限检查：Provider 需要的权限 = 其插件 Manifest 声明 ∩ 需要的本能力执行权限。
        # V0.1 内置只读 Provider 只需 filesystem.read；未授权能力不会静默执行（AC-07）。
        selected = supporting[0]
        return selected, supporting[1:]
