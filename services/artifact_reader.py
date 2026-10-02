"""ArtifactReader（规格第 10/21 节 + Phase 1.1 Stable Facade）。

迁移后调用关系（规格第 31 节）：
    read_artifact() → CapabilityRuntime → CapabilityRegistry → Router → Provider

Reader 只保留：读前校验（mode / 边界 / 存在性 / 大小）、Request 构造、
provenance 补充与日志。本模块不 import 任何具体 Adapter（AC-01）——
格式实现全部由插件注册进入 Registry。
"""
from __future__ import annotations

import hashlib
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

from plugin_runtime import (
    CapabilityRuntime,
    assemble_runtime,
    get_default_runtime,
)
from plugin_runtime.base_provider import CapabilityProviderBase
from plugin_runtime.contracts import (
    CAPABILITY_READ_FULL,
    CapabilityRequest,
    CapabilityResult,
    PluginContext,
)
from plugin_runtime.discovery import DiscoveryReport
from plugin_runtime.errors import (
    CapabilityNotFoundError,
    ProviderExecutionError,
)
from plugin_runtime.loader import LoadReport
from plugin_runtime.policy import PermissionPolicy
from plugin_runtime.registry import CapabilityRegistry
from workspace.artifact import Artifact, ArtifactRef, make_artifact_id
from workspace.errors import (
    ArtifactNotFoundError,
    ArtifactParseError,
    ArtifactRuntimeError,
    ArtifactTooLargeError,
    UnsupportedArtifactTypeError,
    WorkspaceBoundaryError,
)
from workspace.workspace import Workspace

logger = logging.getLogger("hmbuddy.artifact_reader")

# ER-04：超大文件阈值（默认 50 MB），未来再做分段读取
DEFAULT_MAX_FILE_SIZE = 50 * 1024 * 1024

# 规格 15 节：为未来预留的读取模式，第一阶段只实现 full
RESERVED_MODES = ("metadata", "outline", "range", "sheet", "slide", "page", "search")


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class _AdapterCompatProvider(CapabilityProviderBase):
    """兼容层：把调用方显式传入的 Adapter 实例包装成 Provider。

    仅用于旧调用方式 ArtifactReader(adapters=[...])；正常路径下
    Provider 由插件注册提供（AC-01：本模块不引用具体 Adapter 类）。
    """

    def __init__(self, adapter, ocr_options=None):
        CapabilityProviderBase.__init__(self)
        self._compat_adapter = adapter
        self.capability_id = CAPABILITY_READ_FULL
        self.provider_id = f"compat.{type(adapter).__name__}"
        self.plugin_id = "compat"
        self.priority = 100
        self.extensions = tuple(getattr(adapter, "supported_extensions", ()) or ())
        self.declared_permissions = ("filesystem.read",)

    def create_adapter(self, context):
        return self._compat_adapter


def _build_compat_runtime(adapters) -> tuple[CapabilityRuntime, DiscoveryReport, LoadReport]:
    registry = CapabilityRegistry()
    for adapter in adapters:
        registry.register(_AdapterCompatProvider(adapter))
    runtime = CapabilityRuntime(registry)
    return runtime, DiscoveryReport(), LoadReport()


class ArtifactReader:
    """path_or_ref → CapabilityRequest → Runtime → Registry → Provider → Artifact。"""

    def __init__(
        self,
        workspace: Workspace | None = None,
        adapters: list | None = None,
        max_file_size: int = DEFAULT_MAX_FILE_SIZE,
        ocr_options=None,
        external_plugin_dirs: list[Path] | None = None,
        policy: PermissionPolicy | None = None,
    ):
        self.workspace = workspace
        self.ocr_options = ocr_options
        self.policy = policy
        self.max_file_size = max_file_size
        if adapters is not None:
            runtime, discovery, load_report = _build_compat_runtime(adapters)
            self.discovery = discovery
            self.load_report = load_report
        elif external_plugin_dirs is not None or policy is not None:
            # BUG-005 / AC-H05：显式插件目录或自定义 Policy 时，装配独立 Runtime
            assembly = assemble_runtime(
                external_plugin_dirs=external_plugin_dirs,
                policy=policy,
            )
            runtime = assembly.runtime
            self.discovery = assembly.discovery
            self.load_report = assembly.load_report
        else:
            assembly = get_default_runtime()
            runtime = assembly.runtime
            self.discovery = assembly.discovery
            self.load_report = assembly.load_report
        self.runtime: CapabilityRuntime = runtime

    def read_artifact(
        self,
        path_or_ref,
        mode: str = "full",
        workspace: Workspace | None = None,
    ) -> Artifact:
        # 方法级 workspace 参数优先于构造器（便于同一 Reader 处理不同信任域）
        effective_workspace = workspace if workspace is not None else self.workspace

        if mode != "full":
            raise ValueError(
                f"read mode {mode!r} is not implemented yet; only 'full' is "
                f"supported (reserved for future: {', '.join(RESERVED_MODES)})"
            )

        if isinstance(path_or_ref, ArtifactRef):
            raw_path = Path(path_or_ref.path)
            artifact_id: str | None = path_or_ref.artifact_id
            # BUG-007 / AC-H07：来自 Workspace 的 Ref 必须留在原信任域内
            ref_workspace_id = getattr(path_or_ref, "workspace_id", None)
            if ref_workspace_id is not None:
                current_id = (
                    effective_workspace.workspace_id if effective_workspace else None
                )
                if current_id != ref_workspace_id:
                    raise WorkspaceBoundaryError(
                        raw_path,
                        f"artifact ref belongs to workspace {ref_workspace_id!r}; "
                        "pass the originating Workspace to read it "
                        "(workspace trust boundary)",
                    )
        else:
            raw_path = Path(path_or_ref)
            artifact_id = None

        # ER-05：Workspace 边界检查（FR-S01：Provider 使用 Reader 校验后的路径）
        if effective_workspace is not None:
            resolved = effective_workspace.resolve_path(raw_path)
        else:
            resolved = raw_path.expanduser().resolve()

        if not resolved.exists() or not resolved.is_file():
            raise ArtifactNotFoundError(resolved)

        # ER-04：超大文件
        size = resolved.stat().st_size
        if size > self.max_file_size:
            raise ArtifactTooLargeError(resolved, size, self.max_file_size)

        if artifact_id is None:
            artifact_id = make_artifact_id(resolved)
        extension = resolved.suffix.lstrip(".").lower()
        artifact_type = extension or "unknown"
        artifact_ref = ArtifactRef(
            artifact_id=artifact_id,
            name=resolved.name,
            path=str(resolved),
            extension=extension,
            size=size,
            modified_at=datetime.fromtimestamp(resolved.stat().st_mtime, tz=timezone.utc),
            artifact_type=artifact_type,
        )

        request = CapabilityRequest(
            capability=CAPABILITY_READ_FULL,
            artifact_ref=artifact_ref,
            options={"artifact_id": artifact_id},
        )
        context = PluginContext(
            resolved_path=resolved,
            workspace_root=(
                effective_workspace.root_path if effective_workspace is not None else None
            ),
            ocr_options=self.ocr_options,
        )

        adapter_name = "-"
        started = time.perf_counter()
        try:
            result: CapabilityResult = self.runtime.execute(request, context)
        except CapabilityNotFoundError as exc:
            # ER-01 兼容：没有任何 Provider 认领该扩展名 → UnsupportedArtifactTypeError
            duration_ms = (time.perf_counter() - started) * 1000
            self._log_error(resolved, "-", size, duration_ms, artifact_id, exc)
            raise UnsupportedArtifactTypeError(resolved, resolved.suffix.lower()) from exc
        except ProviderExecutionError as exc:
            # ER-02 兼容：Provider 执行期失败本质是解析失败，落回 ArtifactParseError
            # （adapter 记为 provider_id，原始异常保留在因果链上）
            duration_ms = (time.perf_counter() - started) * 1000
            wrapped = ArtifactParseError(
                resolved, adapter=exc.provider_id, cause=exc.cause or exc
            )
            self._log_error(resolved, exc.provider_id, size, duration_ms, artifact_id, wrapped)
            raise wrapped from exc
        except ArtifactRuntimeError as exc:
            duration_ms = (time.perf_counter() - started) * 1000
            self._log_error(resolved, "-", size, duration_ms, artifact_id, exc)
            raise
        except Exception as exc:
            duration_ms = (time.perf_counter() - started) * 1000
            wrapped = ArtifactParseError(resolved, adapter="plugin-runtime", cause=exc)
            self._log_error(resolved, "-", size, duration_ms, artifact_id, wrapped)
            raise wrapped from exc

        artifact: Artifact = result.value
        if not isinstance(artifact, Artifact):
            raise ArtifactParseError(
                resolved,
                adapter=result.provider_id,
                cause=TypeError(
                    f"provider returned {type(artifact).__name__} instead of Artifact (P4)"
                ),
            )
        duration_ms = (time.perf_counter() - started) * 1000
        adapter_name = artifact.provenance.get("adapter", "-")

        # FR-A04 + 规格 24 节：provenance 增加 plugin / provider 信息
        artifact.provenance.update(
            {
                "plugin_id": result.plugin_id,
                "provider_id": result.provider_id,
                "plugin_version": result.plugin_version,
                "capability_trace": result.metadata.get("trace", {}),
                "read_at": datetime.now(timezone.utc).isoformat(),
                "parse_duration_ms": round(duration_ms, 2),
                "file_sha256": _file_sha256(resolved),
            }
        )
        self._log_ok(resolved, adapter_name, artifact.artifact_type, size, duration_ms, artifact_id, result)
        return artifact

    # ------------------------------------------------------------------

    def _log_ok(
        self, path: Path, adapter: str, artifact_type: str, file_size: int,
        duration_ms: float, artifact_id: str, result: CapabilityResult,
    ) -> None:
        logger.info(
            "artifact_read path=%s type=%s adapter=%s artifact_id=%s "
            "plugin_id=%s provider_id=%s file_size=%d parse_duration_ms=%.1f "
            "parse_status=ok",
            path, artifact_type, adapter, artifact_id,
            result.plugin_id, result.provider_id, file_size, duration_ms,
        )

    def _log_error(
        self, path: Path, adapter: str, file_size: int,
        duration_ms: float, artifact_id: str, error: Exception,
    ) -> None:
        logger.error(
            "artifact_read path=%s adapter=%s artifact_id=%s file_size=%d "
            "parse_duration_ms=%.1f parse_status=error error=%r",
            path, adapter, artifact_id, file_size, duration_ms, error,
        )


_default_reader: ArtifactReader | None = None


def read_artifact(
    path_or_ref,
    mode: str = "full",
    *,
    workspace: Workspace | None = None,
    adapters: list | None = None,
    max_file_size: int = DEFAULT_MAX_FILE_SIZE,
    ocr_options=None,
    policy: PermissionPolicy | None = None,
) -> Artifact:
    """Stable Facade（规格第 21 节）：Phase 1 / Phase 2 调用方式保持不变。

    workspace=None 时按普通文件路径读取；传入 Workspace 时强制边界检查。
    ocr_options 用于开启扫描件 OCR（默认关闭，模型仅从本地目录解析）。
    policy 用于放宽/收紧权限（默认仅 filesystem.read）。
    """
    global _default_reader
    if (
        workspace is None
        and adapters is None
        and ocr_options is None
        and policy is None
        and max_file_size == DEFAULT_MAX_FILE_SIZE
    ):
        if _default_reader is None:
            _default_reader = ArtifactReader()
        return _default_reader.read_artifact(path_or_ref, mode)
    return ArtifactReader(
        workspace=workspace,
        adapters=adapters,
        max_file_size=max_file_size,
        ocr_options=ocr_options,
        policy=policy,
    ).read_artifact(path_or_ref, mode)
