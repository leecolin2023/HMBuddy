"""Legacy XLS Plugin：包装现有 XlsAdapter（规格第 20 节 Step 2，不重写解析逻辑）。"""
from __future__ import annotations

from adapters.xls import XlsAdapter

from plugin_runtime.base_provider import CapabilityProviderBase


class XlsReadProvider(CapabilityProviderBase):
    capability_id = "artifact.read.full"
    provider_id = "hmbuddy.xls.core.xlrd"
    extensions = tuple(['.xls'])
    priority = 100

    def create_adapter(self, context):
        return XlsAdapter(context.ocr_options)


class XlsPlugin:
    """Plugin 入口：声明本插件提供的 Provider（与 plugin.json 一致，FR-M04）。"""

    def __init__(self) -> None:
        self._providers = [
            XlsReadProvider(
                plugin_id="hmbuddy.xls.core", plugin_version="0.1.0"
            )
        ]

    def providers(self):
        return list(self._providers)
