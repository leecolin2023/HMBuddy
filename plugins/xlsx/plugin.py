"""XLSX Core Plugin：包装现有 XlsxAdapter（规格第 20 节 Step 2，不重写解析逻辑）。"""
from __future__ import annotations

from adapters.xlsx import XlsxAdapter

from plugin_runtime.base_provider import CapabilityProviderBase


class XlsxReadProvider(CapabilityProviderBase):
    capability_id = "artifact.read.full"
    provider_id = "hmbuddy.xlsx.core.openpyxl"
    extensions = tuple(['.xlsx'])
    priority = 100

    def create_adapter(self, context):
        return XlsxAdapter(context.ocr_options)


class XlsxPlugin:
    """Plugin 入口：声明本插件提供的 Provider（与 plugin.json 一致，FR-M04）。"""

    def __init__(self) -> None:
        self._providers = [
            XlsxReadProvider(
                plugin_id="hmbuddy.xlsx.core", plugin_version="0.1.0"
            )
        ]

    def providers(self):
        return list(self._providers)
