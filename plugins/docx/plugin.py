"""DOCX Core Plugin：包装现有 DocxAdapter（规格第 20 节 Step 2，不重写解析逻辑）。"""
from __future__ import annotations

from adapters.docx import DocxAdapter

from plugin_runtime.base_provider import CapabilityProviderBase


class DocxReadProvider(CapabilityProviderBase):
    capability_id = "artifact.read.full"
    provider_id = "hmbuddy.docx.core.python-docx"
    extensions = tuple(['.docx'])
    priority = 100

    def create_adapter(self, context):
        return DocxAdapter(context.ocr_options)


class DocxPlugin:
    """Plugin 入口：声明本插件提供的 Provider（与 plugin.json 一致，FR-M04）。"""

    def __init__(self) -> None:
        self._providers = [
            DocxReadProvider(
                plugin_id="hmbuddy.docx.core", plugin_version="0.1.0"
            )
        ]

    def providers(self):
        return list(self._providers)
