"""workspace 包：工作目录边界、文件发现与统一领域模型。"""
from .artifact import Artifact, ArtifactBlock, ArtifactLocator, ArtifactRef, make_artifact_id
from .errors import (
    ArtifactNotFoundError,
    ArtifactParseError,
    ArtifactRuntimeError,
    ArtifactTooLargeError,
    EncryptedArtifactError,
    UnsupportedArtifactTypeError,
    WorkspaceBoundaryError,
)
from .workspace import Workspace

__all__ = [
    "Artifact",
    "ArtifactBlock",
    "ArtifactLocator",
    "ArtifactRef",
    "make_artifact_id",
    "ArtifactRuntimeError",
    "UnsupportedArtifactTypeError",
    "ArtifactNotFoundError",
    "WorkspaceBoundaryError",
    "ArtifactTooLargeError",
    "ArtifactParseError",
    "EncryptedArtifactError",
    "Workspace",
]
