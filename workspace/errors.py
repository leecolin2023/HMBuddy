"""Phase 1 显式错误类型（规格第 18 节 ER-01 ~ ER-05）。

不允许静默失败：所有读取异常都必须落入明确的错误类型，便于上层区分
Parser Error / Context Error / LLM Error。
"""
from __future__ import annotations


class ArtifactRuntimeError(Exception):
    """Local Office Artifact Runtime 基础异常。"""


class UnsupportedArtifactTypeError(ArtifactRuntimeError):
    """ER-01：不支持的文件格式。"""

    def __init__(self, path, extension: str | None = None):
        self.path = str(path)
        self.extension = extension
        super().__init__(
            f"unsupported artifact type: {self.path!r} (extension={extension!r})"
        )


class ArtifactNotFoundError(ArtifactRuntimeError):
    """文件不存在或不是普通文件。"""

    def __init__(self, path):
        self.path = str(path)
        super().__init__(f"artifact not found: {self.path!r}")


class WorkspaceBoundaryError(ArtifactRuntimeError):
    """ER-05：路径逃逸 Workspace 根目录。"""

    def __init__(self, path, root):
        self.path = str(path)
        self.root = str(root)
        super().__init__(
            f"path escapes workspace root {self.root!r}: {self.path!r}"
        )


class ArtifactTooLargeError(ArtifactRuntimeError):
    """ER-04：文件超过大小阈值，不强行加载。"""

    def __init__(self, path, size: int, max_size: int):
        self.path = str(path)
        self.size = size
        self.max_size = max_size
        super().__init__(
            f"artifact too large: {self.path!r} ({size} bytes > max {max_size} bytes)"
        )


class ArtifactParseError(ArtifactRuntimeError):
    """ER-02：文件解析失败，记录 path / adapter / 原始错误。"""

    def __init__(self, path, adapter: str | None = None, cause=None):
        self.path = str(path)
        self.adapter = adapter
        self.cause = cause
        message = f"artifact parse error: {self.path!r} (adapter={adapter!r})"
        if cause is not None:
            message += f": {cause!r}"
        super().__init__(message)


class EncryptedArtifactError(ArtifactParseError):
    """ER-03：文件被加密或密码保护。"""

    def __init__(self, path, adapter: str | None = None, reason=None):
        self.reason = reason
        super().__init__(path, adapter=adapter, cause=reason)
