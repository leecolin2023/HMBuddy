"""Plain Text Core Plugin：包装现有 TextAdapter（规格第 20 节 Step 2，不重写解析逻辑）。"""
from __future__ import annotations

from adapters.text import TextAdapter

from plugin_runtime.base_provider import CapabilityProviderBase


class TextReadProvider(CapabilityProviderBase):
    capability_id = "artifact.read.full"
    provider_id = "hmbuddy.text.core.plain"
    extensions = tuple(['.txt', '.md', '.markdown', '.rst', '.csv', '.tsv', '.log'])
    priority = 50

    def create_adapter(self, context):
        return TextAdapter(context.ocr_options)


class TextPlugin:
    """Plugin 入口：声明本插件提供的 Provider（与 plugin.json 一致，FR-M04）。"""

    def __init__(self) -> None:
        self._providers = [
            TextReadProvider(
                plugin_id="hmbuddy.text.core", plugin_version="0.1.0"
            )
        ]

    def providers(self):
        return list(self._providers)
