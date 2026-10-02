"""Capability Runtime（规格第 6/17/24 节）：execute(CapabilityRequest)。

- 确定性路由（CapabilityRouter）；
- 可观察的 Fallback（P6）：首选 Provider 失败时可尝试后续候选，trace 记录
  fallback_from；禁止对 Workspace 越界 / 文件不存在 / 权限错误静默 fallback；
- 每次执行记录 Trace（规格第 24 节字段）。
"""
from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field, replace
from typing import Optional

from workspace.errors import (
    ArtifactNotFoundError,
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
)
from .policy import PermissionPolicy
from .registry import CapabilityRegistry
from .router import CapabilityRouter

logger = logging.getLogger("hmbuddy.plugin_runtime")

# 允许 fallback 的错误类型（规格 FR-R03 禁止清单之外）
FALLABLE_ERRORS = (ProviderExecutionError,)


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
    ):
        self.registry = registry
        self.policy = policy or PermissionPolicy()
        self.router = CapabilityRouter(self.registry, self.policy)
        self.traces: list[CapabilityTrace] = []

    def execute(
        self,
        request: CapabilityRequest,
        context: Optional[PluginContext] = None,
    ) -> CapabilityResult:
        """执行能力请求。

        - 领域错误中禁止 fallback 的类型（Workspace 越界 / 文件不存在 / 权限，
          规格 FR-R03）原样上抛；
        - 其余失败（ArtifactParseError、ProviderExecutionError 等）按优先级
          链尝试下一个 Provider，trace 记录 fallback_from（P6 可观察）；
        - 非领域异常包装为 ProviderExecutionError（ER-P03）。
        """
        context = context or PluginContext()
        request_id = uuid.uuid4().hex[:12]
        artifact_id = str(request.options.get("artifact_id") or "-")

        selected, remaining = self.router.select(request, context)
        chain = [selected, *remaining]
        fallback_from: str | None = None
        last_error: Exception | None = None

        for provider in chain:
            started = time.perf_counter()
            # 按 Policy 计算该插件实际获得的权限（AC-07），Provider 可从 context 读取
            declared = getattr(provider, "declared_permissions", None)
            provider_context = context
            if declared is not None:
                provider_context = replace(
                    context,
                    granted_permissions=self.policy.enforce(
                        getattr(provider, "plugin_id", "?"), declared
                    ),
                )
            try:
                result = provider.execute(request, provider_context)
                duration_ms = (time.perf_counter() - started) * 1000
                self._record_trace(
                    request_id, request, artifact_id, provider,
                    started, duration_ms, "ok",
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
            ) as exc:
                # FR-R03 禁止清单：这些错误不允许静默 fallback
                self._record_failure_trace(
                    request_id, request, artifact_id, provider, started, exc,
                    fallback_from=fallback_from,
                )
                raise
            except ArtifactRuntimeError as exc:
                # 领域错误（含 PluginRuntimeError 家族）：可 fallback 的失败
                duration_ms = (time.perf_counter() - started) * 1000
                self._record_failure_trace(
                    request_id, request, artifact_id, provider, started, exc,
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
            except Exception as exc:
                # ER-P03：非领域异常包装，保留 plugin/provider/capability/cause
                duration_ms = (time.perf_counter() - started) * 1000
                wrapped = ProviderExecutionError(
                    f"provider {provider.provider_id!r} failed: {exc!r}",
                    plugin_id=getattr(provider, "plugin_id", "?"),
                    provider_id=getattr(provider, "provider_id", "?"),
                    capability=request.capability,
                    cause=exc,
                )
                self._record_failure_trace(
                    request_id, request, artifact_id, provider, started, wrapped,
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

    def _record_trace(
        self,
        request_id: str,
        request: CapabilityRequest,
        artifact_id: str,
        provider,
        started: float,
        duration_ms: float,
        status: str,
        warnings: list[str] | None = None,
        error_type: str | None = None,
        fallback_from: str | None = None,
    ) -> None:
        from datetime import datetime, timezone

        trace = CapabilityTrace(
            request_id=request_id,
            capability=request.capability,
            artifact_id=artifact_id,
            plugin_id=getattr(provider, "plugin_id", "?"),
            provider_id=getattr(provider, "provider_id", "?"),
            started_at=datetime.now(timezone.utc).isoformat(),
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
        started: float,
        exc: Exception,
        fallback_from: str | None,
    ) -> None:
        self._record_trace(
            request_id,
            request,
            artifact_id,
            provider,
            started,
            (time.perf_counter() - started) * 1000,
            "error",
            error_type=type(exc).__name__,
            fallback_from=fallback_from,
        )
