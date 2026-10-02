"""Legacy DOC Plugin：包装现有 DocLegacyAdapter（规格第 20 节 Step 2，不重写解析逻辑）。"""
from __future__ import annotations

from adapters.doc_legacy import DocLegacyAdapter

from plugin_runtime.base_provider import CapabilityProviderBase
from plugin_runtime.contracts import PERMISSION_OFFICE_COM


class DocLegacyReadProvider(CapabilityProviderBase):
    capability_id = "artifact.read.full"
    provider_id = "hmbuddy.doc.core.com"
    extensions = tuple(['.doc'])
    priority = 100
    # BUG-001：.doc 只有 COM 一条路径，执行必须已授权 office.com；
    # 默认 Policy（仅 filesystem.read）下 Provider 不会进入 execute，
    # 更不会实际启动 Word/WPS。
    required_permissions = frozenset({PERMISSION_OFFICE_COM})

    def create_adapter(self, context):
        return DocLegacyAdapter(context.ocr_options)


class DocLegacyPlugin:
    """Plugin 入口：声明本插件提供的 Provider（与 plugin.json 一致，FR-M04）。"""

    def __init__(self) -> None:
        self._providers = [
            DocLegacyReadProvider(
                plugin_id="hmbuddy.doc.core", plugin_version="0.1.0"
            )
        ]

    def providers(self):
        return list(self._providers)
