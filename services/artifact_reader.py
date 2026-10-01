"""ArtifactReader（规格第 10 节 + Step 6）：read_artifact 单一入口。

职责：
- FR-A01 单一入口：上层禁止直接依赖具体 Adapter；
- FR-A02 自动路由：按扩展名选择 Adapter（判断只存在于本层，见 P2）；
- FR-A04 保留 provenance：读取时间、耗时、sha256 等；
- 第 18 节错误处理：ER-01 ~ ER-05 全部落到显式错误类型；
- 第 23 节 Logging：每次读取记录 artifact_id/path/type/adapter/size/耗时/状态/错误。
"""
from __future__ import annotations

import hashlib
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

from adapters import default_adapters
from adapters.base import ArtifactAdapter
from workspace.artifact import Artifact, ArtifactRef, make_artifact_id
from workspace.errors import (
    ArtifactNotFoundError,
    ArtifactParseError,
    ArtifactRuntimeError,
    ArtifactTooLargeError,
    EncryptedArtifactError,
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


class ArtifactReader:
    """path_or_ref → 路由 → Adapter → Artifact。"""

    def __init__(
        self,
        workspace: Workspace | None = None,
        adapters: list[ArtifactAdapter] | None = None,
        max_file_size: int = DEFAULT_MAX_FILE_SIZE,
    ):
        self.workspace = workspace
        self.adapters: list[ArtifactAdapter] = (
            list(adapters) if adapters is not None else default_adapters()
        )
        self.max_file_size = max_file_size

    def read_artifact(self, path_or_ref, mode: str = "full") -> Artifact:
        if mode != "full":
            raise ValueError(
                f"read mode {mode!r} is not implemented yet; only 'full' is "
                f"supported (reserved for future: {', '.join(RESERVED_MODES)})"
            )

        if isinstance(path_or_ref, ArtifactRef):
            raw_path = Path(path_or_ref.path)
            artifact_id: str | None = path_or_ref.artifact_id
        else:
            raw_path = Path(path_or_ref)
            artifact_id = None

        # ER-05：Workspace 边界检查
        if self.workspace is not None:
            resolved = self.workspace.resolve_path(raw_path)
        else:
            resolved = raw_path.expanduser().resolve()

        if not resolved.exists() or not resolved.is_file():
            raise ArtifactNotFoundError(resolved)

        # ER-04：超大文件
        size = resolved.stat().st_size
        if size > self.max_file_size:
            raise ArtifactTooLargeError(resolved, size, self.max_file_size)

        # FR-A02：路由（.docx→DocxAdapter 等）
        adapter = self._route(resolved)
        if artifact_id is None:
            artifact_id = make_artifact_id(resolved)

        started = time.perf_counter()
        try:
            artifact = adapter.read(resolved, artifact_id)
        except Exception as exc:
            duration_ms = (time.perf_counter() - started) * 1000
            if isinstance(exc, ArtifactRuntimeError):
                # EncryptedArtifactError / 越界等已是明确错误类型，直接记录并上抛
                self._log(
                    "error", resolved, adapter, size, duration_ms,
                    artifact_id=artifact_id, error=exc,
                )
                raise
            wrapped = ArtifactParseError(
                resolved, adapter=type(adapter).__name__, cause=exc
            )
            self._log(
                "error", resolved, adapter, size, duration_ms,
                artifact_id=artifact_id, error=wrapped,
            )
            raise wrapped from exc

        duration_ms = (time.perf_counter() - started) * 1000
        artifact.provenance.update(
            {
                "read_at": datetime.now(timezone.utc).isoformat(),
                "parse_duration_ms": round(duration_ms, 2),
                "file_sha256": _file_sha256(resolved),
            }
        )
        self._log(
            "ok", resolved, adapter, size, duration_ms, artifact_id=artifact_id
        )
        return artifact

    def _route(self, path: Path) -> ArtifactAdapter:
        for adapter in self.adapters:
            if adapter.supports(path):
                return adapter
        # ER-01：不支持格式，不静默失败
        raise UnsupportedArtifactTypeError(path, path.suffix.lower())

    def _log(
        self,
        status: str,
        path: Path,
        adapter: ArtifactAdapter,
        file_size: int,
        duration_ms: float,
        *,
        artifact_id: str | None,
        error: Exception | None = None,
    ) -> None:
        fields = (
            f"path={path} type={adapter.artifact_type} "
            f"adapter={type(adapter).__name__} artifact_id={artifact_id or '-'} "
            f"file_size={file_size} parse_duration_ms={duration_ms:.1f} "
            f"parse_status={status}"
        )
        if error is not None:
            fields += f" error={error!r}"
            logger.error("artifact_read %s", fields)
        else:
            logger.info("artifact_read %s", fields)


_default_reader: ArtifactReader | None = None


def read_artifact(
    path_or_ref,
    mode: str = "full",
    *,
    workspace: Workspace | None = None,
    adapters: list[ArtifactAdapter] | None = None,
    max_file_size: int = DEFAULT_MAX_FILE_SIZE,
) -> Artifact:
    """模块级单一入口（FR-A01）。

    workspace=None 时按普通文件路径读取；传入 Workspace 时强制边界检查。
    """
    global _default_reader
    if workspace is None and adapters is None and max_file_size == DEFAULT_MAX_FILE_SIZE:
        if _default_reader is None:
            _default_reader = ArtifactReader()
        return _default_reader.read_artifact(path_or_ref, mode)
    return ArtifactReader(
        workspace=workspace, adapters=adapters, max_file_size=max_file_size
    ).read_artifact(path_or_ref, mode)
