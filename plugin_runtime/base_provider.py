"""Provider 基类：实现 CapabilityProvider 协议的公共部分。

插件 Provider 继承本类，只需提供 capability_id / provider_id / extensions /
create_adapter()。supports() 做扩展名匹配（格式只是匹配条件之一，P2）。
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from workspace.artifact import Artifact

from .contracts import (
    CAPABILITY_READ_FULL,
    CapabilityProvider,  # noqa: F401  (随包再导出，方便插件单点导入)
    CapabilityRequest,
    CapabilityResult,
    PluginContext,
)


class CapabilityProviderBase:
    """CapabilityProvider 的公共实现基类。"""

    capability_id: str = CAPABILITY_READ_FULL
    provider_id: str = ""
    plugin_id: str = ""
    plugin_version: str = ""
    priority: int = 100
    extensions: tuple[str, ...] = ()
    # 由 Loader 从 Manifest 注入（FR-M05 / AC-07 可观察）
    declared_permissions: tuple[str, ...] = ()

    def __init__(self, plugin_id: str = "", plugin_version: str = ""):
        if plugin_id:
            self.plugin_id = plugin_id
        if plugin_version:
            self.plugin_version = plugin_version
        # Adapter 按运行配置（OcrOptions 等）分别缓存，避免跨请求串配置
        self._adapters: dict[str, object] = {}

    # -- CapabilityProvider 协议 ------------------------------------------

    def supports(self, request: CapabilityRequest) -> bool:
        if request.capability != self.capability_id:
            return False
        ref = request.artifact_ref
        if ref is None:
            return False
        extension = (ref.extension or "").lower()
        if extension and not extension.startswith("."):
            extension = "." + extension
        return extension in self.extensions

    def is_available(self, context: PluginContext) -> bool:
        return True

    def execute(
        self,
        request: CapabilityRequest,
        context: PluginContext,
    ) -> CapabilityResult:
        """执行读取：使用 Reader 已校验的路径（FR-S01），返回统一 Artifact（P4）。"""
        if context.resolved_path is None:
            raise RuntimeError(
                f"provider {self.provider_id!r} requires context.resolved_path"
            )
        artifact_id = str(request.options.get("artifact_id") or "")
        artifact: Artifact = self.get_adapter(context).read(
            Path(context.resolved_path), artifact_id
        )
        return CapabilityResult(
            success=True,
            value=artifact,
            provider_id=self.provider_id,
            plugin_id=self.plugin_id,
            plugin_version=self.plugin_version,
            metadata={},
        )

    # -- 插件侧扩展点 ------------------------------------------------------

    def create_adapter(self, context: PluginContext):
        """构造底层实现（Adapter / API / COM）；由具体插件提供。"""
        raise NotImplementedError

    def get_adapter(self, context: PluginContext):
        """Adapter 惰性构造并缓存——Adapter 只是插件内部的一种实现技术（规格第 31 节）。"""
        key = _config_key(context.ocr_options)
        if key not in self._adapters:
            self._adapters[key] = self.create_adapter(context)
        return self._adapters[key]


def _config_key(ocr_options) -> str:
    if ocr_options is None:
        return "default"
    if hasattr(ocr_options, "__dict__"):
        return repr(sorted(vars(ocr_options).items(), key=lambda kv: kv[0]))
    return repr(ocr_options)
