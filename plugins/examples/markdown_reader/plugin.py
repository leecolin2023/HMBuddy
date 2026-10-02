"""最小外部插件示例（规格 G5 / 第 22 节）。

验收要求：新增本插件时不得修改 Capability Runtime、Registry、Router 和
既有插件代码。把本目录加入 HMBUDDY_PLUGIN_PATH 即被自动发现，读取 .md
时按 priority=100 覆盖内置文本插件（priority=50）。
"""
from __future__ import annotations

from pathlib import Path

from plugin_runtime.base_provider import CapabilityProviderBase
from plugin_runtime.contracts import CapabilityResult
from workspace.artifact import Artifact, ArtifactBlock


class MarkdownReadProvider(CapabilityProviderBase):
    capability_id = "artifact.read.full"
    provider_id = "example.markdown.reader.plain"
    extensions = (".md",)
    priority = 100

    def create_adapter(self, context):
        return None  # 外部插件可以完全不依赖内置 Adapter

    def execute(self, request, context):
        path = Path(context.resolved_path)
        text = path.read_text(encoding="utf-8-sig")
        blocks = []
        for index, raw_line in enumerate(text.replace("\r\n", "\n").split("\n")):
            line = raw_line.strip()
            if not line:
                continue
            blocks.append(
                ArtifactBlock("", "paragraph", line, {"line_index": index}, {})
            )
        artifact = Artifact(
            artifact_id=str(request.options.get("artifact_id") or ""),
            name=path.name,
            path=str(path),
            artifact_type="md",
            metadata={"line_count": len(blocks), "title": path.stem, "origin": "external-plugin"},
            content=text.strip(),
            blocks=blocks,
            provenance={},
        )
        return CapabilityResult(
            success=True,
            value=artifact,
            provider_id=self.provider_id,
            plugin_id=self.plugin_id,
            plugin_version=self.plugin_version,
        )


class MarkdownReaderPlugin:
    def __init__(self) -> None:
        self._providers = [
            MarkdownReadProvider(
                plugin_id="example.markdown.reader", plugin_version="0.1.0"
            )
        ]

    def providers(self):
        return list(self._providers)
