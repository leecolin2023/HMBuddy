"""Workspace：工作目录边界 + 文件发现（规格 8.1 / 第 9 节 + BUG-002/007/014 修订）。

- 只负责发现文件与生成 ArtifactRef，不负责解析内容；
- 支持格式不再由本模块静态维护（AC-H14）：当前 Runtime 能否处理某扩展名
  由 Capability Catalog（plugin_runtime/catalog.py）决定——安装新插件后
  Workspace 自动识别新格式（AC-H02）；
- 生成的 ArtifactRef 携带 workspace_id 信任域标记（BUG-007 / AC-H07）。
"""
from __future__ import annotations

import os
import stat as stat_module
from datetime import datetime, timezone
from pathlib import Path

from .artifact import ArtifactRef, make_artifact_id, make_workspace_id
from .errors import WorkspaceBoundaryError

_TEMP_NAMES = {".ds_store", "desktop.ini", "thumbs.db"}
_TEMP_SUFFIXES = (".tmp", ".temp", ".crdownload", ".partial")


class Workspace:
    """代表当前允许系统操作的本地工作目录。"""

    def __init__(self, root_path, extension_catalog=None):
        root = Path(root_path).expanduser().resolve()
        if not root.exists():
            raise FileNotFoundError(f"workspace root does not exist: {root!r}")
        if not root.is_dir():
            raise NotADirectoryError(f"workspace root is not a directory: {root!r}")
        self.root_path = root
        self.workspace_id = make_workspace_id(root)
        if extension_catalog is None:
            # 延迟导入避免循环依赖；默认目录来自当前 Runtime 的 Registry（BUG-002）
            from plugin_runtime.catalog import get_default_catalog

            extension_catalog = get_default_catalog()
        self.catalog = extension_catalog

    @property
    def supported_extensions(self) -> set[str]:
        """当前可发现的扩展名集合（由 Capability Catalog 派生，只读视图）。"""
        return self.catalog.artifact_extensions()

    @staticmethod
    def is_temp_or_hidden(name: str) -> bool:
        """FR-W03：临时文件 / 隐藏文件不得被识别为有效 Artifact。"""
        lowered = name.lower()
        if name.startswith("."):
            return True
        if name.startswith("~$"):
            return True
        if lowered in _TEMP_NAMES:
            return True
        if lowered.endswith(_TEMP_SUFFIXES):
            return True
        if name.startswith("~") and lowered.endswith(".tmp"):
            return True
        return False

    @staticmethod
    def _has_hidden_attribute(st) -> bool:
        attrs = getattr(st, "st_file_attributes", 0)
        hidden_flag = getattr(stat_module, "FILE_ATTRIBUTE_HIDDEN", 0x2)
        return bool(attrs & hidden_flag) if attrs else False

    def list_artifacts(self) -> list[ArtifactRef]:
        """FR-W01：递归遍历工作目录，返回当前 Runtime 可处理的 ArtifactRef
        （按路径稳定排序；扩展名合法性由 Capability Catalog 决定）。"""
        refs: list[ArtifactRef] = []
        for dirpath, dirnames, filenames in os.walk(self.root_path):
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            for filename in filenames:
                if self.is_temp_or_hidden(filename):
                    continue
                file_path = Path(dirpath) / filename
                try:
                    st = file_path.stat()
                except OSError:
                    continue
                if self._has_hidden_attribute(st):
                    continue
                extension = file_path.suffix.lower()
                if not extension or not self.catalog.can_handle_extension(extension):
                    continue
                relative = file_path.relative_to(self.root_path).as_posix()
                refs.append(
                    ArtifactRef(
                        artifact_id=make_artifact_id(file_path),
                        name=filename,
                        path=str(file_path),
                        extension=extension.lstrip("."),
                        size=st.st_size,
                        modified_at=datetime.fromtimestamp(
                            st.st_mtime, tz=timezone.utc
                        ),
                        artifact_type=self.catalog.artifact_type_for(extension),
                        workspace_id=self.workspace_id,
                        relative_path=relative,
                    )
                )
        refs.sort(key=lambda ref: ref.path)
        return refs

    def resolve_path(self, path) -> Path:
        """FR-W04 / ER-05：把路径解析为 Workspace 内的绝对路径，越界即报错。"""
        candidate = Path(path).expanduser()
        if not candidate.is_absolute():
            candidate = self.root_path / candidate
        resolved = candidate.resolve()
        if resolved != self.root_path and self.root_path not in resolved.parents:
            raise WorkspaceBoundaryError(resolved, self.root_path)
        return resolved

    def __repr__(self) -> str:  # pragma: no cover
        return f"Workspace(root_path={str(self.root_path)!r})"
