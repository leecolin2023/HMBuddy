"""PPTX Core Plugin：包装现有 PptxAdapter（规格第 20 节 Step 2，不重写解析逻辑）。"""
from __future__ import annotations

from adapters.pptx import PptxAdapter

from plugin_runtime.base_provider import CapabilityProviderBase


class PptxReadProvider(CapabilityProviderBase):
    capability_id = "artifact.read.full"
    provider_id = "hmbuddy.pptx.core.python-pptx"
    extensions = tuple(['.pptx'])
    priority = 100

    def create_adapter(self, context):
        return PptxAdapter(context.ocr_options)


class PptxPlugin:
    """Plugin 入口：声明本插件提供的 Provider（与 plugin.json 一致，FR-M04）。"""

    def __init__(self) -> None:
        self._providers = [
            PptxReadProvider(
                plugin_id="hmbuddy.pptx.core", plugin_version="0.1.0"
            )
        ]

    def providers(self):
        return list(self._providers)
