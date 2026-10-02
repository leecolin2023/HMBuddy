"""Router / Policy 执行（规格第 17 节 + BUG-008/011 修订）：确定性 Provider 选择。

匹配顺序：
1. capability 匹配（Registry.resolve）
2. Provider supports(request)
3. 当前运行环境可用（platform / python / 依赖探针，availability_reason）
4. 权限检查（Policy）
5. priority 从高到低
6. provider_id 稳定排序作为最终 tie-break

BUG-011：supports / availability 的异常不再被静默吞掉——记录进选择诊断；
若因此无任何可用候选，抛 ProviderSelectionError 而非普通 CapabilityNotFound。
"""
from __future__ import annotations

from .contracts import CapabilityRequest, PluginContext
from .errors import (
    CapabilityNotFoundError,
    ProviderNotAvailableError,
    ProviderSelectionError,
)
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
    ) -> tuple[object, list[object], list[dict]]:
        """返回 (选中的 Provider, 支持但落选的候选列表, 选择诊断)。

        - capability 无注册 → CapabilityNotFoundError；
        - 有注册但无一 supports 本请求 → CapabilityNotFoundError（detail 说明）；
        - 选择阶段出现异常且无可用候选 → ProviderSelectionError（BUG-011）；
        - 支持的 Provider 均不可用 → ProviderNotAvailableError（附原因）。
        """
        candidates = self.registry.resolve(request)
        supporting: list[object] = []
        unavailable: list[tuple[object, str]] = []
        diagnostics: list[dict] = []

        for provider in candidates:
            try:
                supported = bool(provider.supports(request))
            except Exception as exc:
                diagnostics.append(
                    self._diagnostic(provider, "supports", exc)
                )
                continue
            if not supported:
                continue

            try:
                reason = self._availability_reason(provider, context)
            except Exception as exc:
                diagnostics.append(
                    self._diagnostic(provider, "availability", exc)
                )
                continue
            if reason:
                unavailable.append((provider, reason))
                continue
            supporting.append(provider)

        if not supporting:
            if diagnostics:
                raise ProviderSelectionError(request.capability, diagnostics)
            if unavailable:
                first, reason = unavailable[0]
                raise ProviderNotAvailableError(
                    request.capability,
                    getattr(first, "plugin_id", "?"),
                    getattr(first, "provider_id", "?"),
                    reason=reason,
                )
            raise CapabilityNotFoundError(
                request.capability,
                "registered providers do not support this request "
                f"(extensions claimed: {sorted(self.registry.extensions_claimed())})",
            )

        # 权限检查：Provider 需要的权限 = 其插件 Manifest 声明 ∩ 需要的本能力执行权限。
        # V0.1 内置只读 Provider 只需 filesystem.read；未授权能力不会静默执行（AC-07）。
        selected = supporting[0]
        return selected, supporting[1:], diagnostics

    @staticmethod
    def _availability_reason(provider, context: PluginContext) -> str | None:
        if hasattr(provider, "availability_reason"):
            return provider.availability_reason(context)
        # 兼容只实现布尔 is_available 的第三方 Provider
        return None if provider.is_available(context) else "unavailable (is_available=False)"

    @staticmethod
    def _diagnostic(provider, stage: str, exc: Exception) -> dict:
        return {
            "plugin_id": getattr(provider, "plugin_id", "?"),
            "provider_id": getattr(provider, "provider_id", "?"),
            "stage": stage,
            "error_type": type(exc).__name__,
            "message": str(exc)[:300],
        }
