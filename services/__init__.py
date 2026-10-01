"""services 包：面向上层的 Artifact 服务（单一入口 read_artifact）。"""
from .artifact_reader import ArtifactReader, read_artifact

__all__ = ["ArtifactReader", "read_artifact"]
