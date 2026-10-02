"""PDF Core Plugin：包装现有 PdfAdapter（规格第 20 节 Step 2，不重写解析逻辑）。"""
from __future__ import annotations

from adapters.pdf import PdfAdapter

from plugin_runtime.base_provider import CapabilityProviderBase


class PdfReadProvider(CapabilityProviderBase):
    capability_id = "artifact.read.full"
    provider_id = "hmbuddy.pdf.core.pdfplumber"
    extensions = tuple(['.pdf'])
    priority = 100

    def create_adapter(self, context):
        return PdfAdapter(context.ocr_options)


class PdfPlugin:
    """Plugin 入口：声明本插件提供的 Provider（与 plugin.json 一致，FR-M04）。"""

    def __init__(self) -> None:
        self._providers = [
            PdfReadProvider(
                plugin_id="hmbuddy.pdf.core", plugin_version="0.1.0"
            )
        ]

    def providers(self):
        return list(self._providers)
