"""Capability Runtime（规格第 6/17/24 节 + Phase 1.1.1 修订）。

- 确定性路由（CapabilityRouter）；
- BUG-001：execute 前强校验 Provider 的 required_permissions，未授权抛
  PluginPermissionError；context.require_permission 提供动态权限受控接口；
- BUG-010：CapabilityResult.success=False 强制转为 ProviderExecutionError；
- BUG-012：fallback 使用显式 allowlist（ArtifactParseError /
  ProviderExecutionError；EncryptedArtifactError 属解析类错误，允许 fallback
  ——对 COM 类 Provider 有意义，禁止清单外的一切错误不 fallback）；
- BUG-015：started_at 在执行前记录；内存 trace 使用有界 deque。
"""
from __future__ import annotations

import logging
import time
import uuid
from collections import deque
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from typing import Optional

from workspace.errors import (
    ArtifactNotFoundError,
    ArtifactParseError,
    ArtifactRuntimeError,
    WorkspaceBoundaryError,
)

from .contracts import (
    CapabilityRequest,
    CapabilityResult,
    PluginContext,
)
from .errors import (
    CapabilityNotFoundError,
    PluginPermissionError,
    ProviderExecutionError,
    ProviderNotAvailableError,
    ProviderSelectionError,
)
from .policy import PermissionPolicy
from .registry import CapabilityRegistry
from .router import CapabilityRouter

logger = logging.getLogger("hmbuddy.plugin_runtime")

# BUG-012：fallback 显式 allowlist。
# 允许：解析类失败（含 EncryptedArtifactError——加密文件换 COM 类 Provider 有意义）
#       与 Provider 执行失败（含 success=False 转换）。
# 禁止：WorkspaceBoundaryError / ArtifactNotFoundError / PluginPermissionError /
#       CapabilityNotFoundError / ProviderNotAvailableError / ProviderSelectionError
#       （以及未来 UserCancelled / PolicyViolation / InvalidRequest）。
FALLBACK_ALLOWED_ERRORS = (ArtifactParseError, ProviderExecutionError)

DEFAULT_MAX_TRACES = 200


@dataclass
class CapabilityTrace:
    request_id: str
    capability: str
    artifact_id: str
    plugin_id: str
    provider_id: str
    started_at: str
    duration_ms: float
    status: str
    warnings: list[str] = field(default_factory=list)
    error_type: str | None = None
    fallback_from: str | None = None

    def to_dict(self) -> dict:
        return {
            "request_id": self.request_id,
            "capability": self.capability,
            "artifact_id": self.artifact_id,
            "plugin_id": self.plugin_id,
            "provider_id": self.provider_id,
            "started_at": self.started_at,
            "duration_ms": round(self.duration_ms, 2),
            "status": self.status,
            "warnings": list(self.warnings),
            "error_type": self.error_type,
            "fallback_from": self.fallback_from,
        }


class CapabilityRuntime:
    def __init__(
        self,
        registry: CapabilityRegistry,
        policy: PermissionPolicy | None = None,
        max_traces: int = DEFAULT_MAX_TRACES,
    ):
        self.registry = registry
        self.policy = policy or PermissionPolicy()
        self.router = CapabilityRouter(self.registry, self.policy)
        # BUG-015：内存 trace 有界（结构化日志始终完整输出）
        self.traces: deque[CapabilityTrace] = deque(maxlen=max_traces)
        self.last_selection_diagnostics: list[dict] = []

    def execute(
        self,
        request: CapabilityRequest,
        context: Optional[PluginContext] = None,
    ) -> CapabilityResult:
        """执行能力请求。

        - 越界 / 不存在 / 权限 / 选择失败等禁止 fallback 的错误原样上抛；
        - allowlist 内的失败按优先级链尝试下一个 Provider（P6 可观察）；
        - 非领域异常包装为 ProviderExecutionError（ER-P03）。
        """
        context = context or PluginContext()
        request_id = uuid.uuid4().hex[:12]
        artifact_id = str(request.options.get("artifact_id") or "-")

        selected, remaining, diagnostics = self.router.select(request, context)
        self.last_selection_diagnostics = diagnostics
        chain = [selected, *remaining]
        fallback_from: str | None = None
        last_error: Exception | None = None

        for provider in chain:
            started_clock = time.perf_counter()
            # BUG-015：started_at 必须是真实开始时间
            started_at = datetime.now(timezone.utc)

            plugin_id = getattr(provider, "plugin_id", "?")
            declared = getattr(provider, "declared_permissions", ()) or ()

            # BUG-001：Provider 声明的执行所需权限在 execute 前强校验
            required = set(getattr(provider, "required_permissions", ()) or ())
            missing = sorted(p for p in required if not self.policy.grants(p))
            if missing:
                error = PluginPermissionError(
                    plugin_id,
                    [f"{p} (required by provider, not granted by policy)" for p in missing],
                    declared,
                )
                self._record_failure_trace(
                    request_id, request, artifact_id, provider,
                    started_at, started_clock, error,
                    fallback_from=fallback_from,
                )
                raise error

            # 按 Policy 计算该插件实际获得的权限（AC-07），并挂接动态权限接口
            granted = self.policy.enforce(plugin_id, declared)
            provider_context = replace(
                context,
                granted_permissions=granted,
                require_permission=self._dynamic_gate(plugin_id, declared, granted),
            )

            try:
                result = provider.execute(request, provider_context)
                duration_ms = (time.perf_counter() - started_clock) * 1000
                # BUG-010：success=False 不得记录为 ok
                if getattr(result, "success", True) is False:
                    raise ProviderExecutionError(
                        f"provider {provider.provider_id!r} returned success=False"
                        + (f": {getattr(result, 'error', None) or ''}".rstrip(": ")),
                        plugin_id=plugin_id,
                        provider_id=getattr(provider, "provider_id", "?"),
                        capability=request.capability,
                    )
                self._record_trace(
                    request_id, request, artifact_id, provider,
                    started_at, started_clock, duration_ms, "ok",
                    warnings=result.warnings, fallback_from=fallback_from,
                )
                result.metadata.setdefault("trace", {
                    "request_id": request_id,
                    "fallback_from": fallback_from,
                    "duration_ms": round(duration_ms, 2),
                })
                return result
            except (
                WorkspaceBoundaryError,
                ArtifactNotFoundError,
                PluginPermissionError,
                CapabilityNotFoundError,
                ProviderNotAvailableError,
                ProviderSelectionError,
            ) as exc:
                # FR-R03 / BUG-012 禁止清单：不允许 fallback
                self._record_failure_trace(
                    request_id, request, artifact_id, provider,
                    started_at, started_clock, exc,
                    fallback_from=fallback_from,
                )
                raise
            except ArtifactRuntimeError as exc:
                if isinstance(exc, FALLBACK_ALLOWED_ERRORS):
                    duration_ms = (time.perf_counter() - started_clock) * 1000
                    self._record_failure_trace(
                        request_id, request, artifact_id, provider,
                        started_at, started_clock, exc,
                        fallback_from=fallback_from,
                    )
                    logger.warning(
                        "capability_execute fallback capability=%s provider=%s "
                        "fallback_from=%s error=%r",
                        request.capability, provider.provider_id, fallback_from, exc,
                    )
                    last_error = exc
                    fallback_from = provider.provider_id
                    continue
                # allowlist 之外的领域错误：不 fallback
                self._record_failure_trace(
                    request_id, request, artifact_id, provider,
                    started_at, started_clock, exc,
                    fallback_from=fallback_from,
                )
                raise
            except Exception as exc:
                # ER-P03：非领域异常包装，保留 plugin/provider/capability/cause
                duration_ms = (time.perf_counter() - started_clock) * 1000
                wrapped = ProviderExecutionError(
                    f"provider {provider.provider_id!r} failed: {exc!r}",
                    plugin_id=plugin_id,
                    provider_id=getattr(provider, "provider_id", "?"),
                    capability=request.capability,
                    cause=exc,
                )
                self._record_failure_trace(
                    request_id, request, artifact_id, provider,
                    started_at, started_clock, wrapped,
                    fallback_from=fallback_from,
                )
                last_error = wrapped
                fallback_from = provider.provider_id
                continue

        raise last_error if last_error is not None else ProviderExecutionError(
            f"no provider executed for capability {request.capability!r}",
            plugin_id="?",
            provider_id="?",
            capability=request.capability,
        )

    # ------------------------------------------------------------------

    def _dynamic_gate(self, plugin_id: str, declared, granted):
        """BUG-001/4.3：动态权限受控接口，挂到 provider_context.require_permission。"""
        from plugin_runtime.errors import PluginPermissionError

        def require(permission: str) -> None:
            if permission not in declared:
                raise PluginPermissionError(
                    plugin_id, [f"{permission} (not declared in manifest)"], declared
                )
            if permission not in granted:
                raise PluginPermissionError(
                    plugin_id,
                    [f"{permission} (declared but not granted by policy)"],
                    declared,
                )

        return require

    def _record_trace(
        self,
        request_id: str,
        request: CapabilityRequest,
        artifact_id: str,
        provider,
        started_at: datetime,
        started_clock: float,
        duration_ms: float,
        status: str,
        warnings: list[str] | None = None,
        error_type: str | None = None,
        fallback_from: str | None = None,
    ) -> None:
        trace = CapabilityTrace(
            request_id=request_id,
            capability=request.capability,
            artifact_id=artifact_id,
            plugin_id=getattr(provider, "plugin_id", "?"),
            provider_id=getattr(provider, "provider_id", "?"),
            started_at=started_at.isoformat(),
            duration_ms=duration_ms,
            status=status,
            warnings=list(warnings or []),
            error_type=error_type,
            fallback_from=fallback_from,
        )
        self.traces.append(trace)
        logger.info(
            "capability_execute %s",
            " ".join(f"{k}={v}" for k, v in trace.to_dict().items()),
        )

    def _record_failure_trace(
        self,
        request_id: str,
        request: CapabilityRequest,
        artifact_id: str,
        provider,
        started_at: datetime,
        started_clock: float,
        exc: Exception,
        fallback_from: str | None,
    ) -> None:
        self._record_trace(
            request_id,
            request,
            artifact_id,
            provider,
            started_at,
            started_clock,
            (time.perf_counter() - started_clock) * 1000,
            "error",
            error_type=type(exc).__name__,
            fallback_from=fallback_from,
        )
