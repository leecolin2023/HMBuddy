"""Provider 基类：实现 CapabilityProvider 协议的公共部分。

插件 Provider 继承本类，只需提供 capability_id / provider_id / extensions /
create_adapter()。Manifest 是唯一权威源（BUG-003）：plugin_id / plugin_version /
priority / extensions / declared_permissions 由 Loader 从 Manifest 强制注入，
Provider 只负责 supports / availability / execute。
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from workspace.artifact import Artifact

from .availability import platform_unavailable_reason, python_unavailable_reason
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
    # 以下字段由 Loader 依 Manifest 强制注入（BUG-003），Provider 不应自行设值
    plugin_id: str = ""
    plugin_version: str = ""
    priority: int = 100
    extensions: tuple[str, ...] = ()
    declared_permissions: tuple[str, ...] = ()
    platforms: tuple[str, ...] = ()
    python_requires: str = ""
    # Provider 实际执行所需权限（BUG-001）：Runtime 在 execute 前强校验
    required_permissions: frozenset = frozenset()

    def __init__(self, plugin_id: str = "", plugin_version: str = ""):
        if plugin_id:
            self.plugin_id = plugin_id
        if plugin_version:
            self.plugin_version = plugin_version
        # Adapter 按运行配置（OcrOptions / 授权权限集）分别缓存，避免跨请求串配置
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

    def availability_reason(self, context: PluginContext) -> str | None:
        """不可用时返回原因（可诊断，BUG-008/011）；可用返回 None。"""
        reason = platform_unavailable_reason(self.platforms)
        if reason:
            return reason
        reason = python_unavailable_reason(self.python_requires)
        if reason:
            return reason
        return self.probe_dependencies()

    def is_available(self, context: PluginContext) -> bool:
        return self.availability_reason(context) is None

    def probe_dependencies(self) -> str | None:
        """依赖探针钩子：依赖缺失时返回原因字符串；默认无额外依赖。"""
        return None

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
        adapter = self.get_adapter(context)
        gate = self._permission_gate(context)
        if hasattr(adapter, "set_permission_gate"):
            adapter.set_permission_gate(gate)
        artifact: Artifact = adapter.read(Path(context.resolved_path), artifact_id)
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
        key = _config_key(context)
        if key not in self._adapters:
            self._adapters[key] = self.create_adapter(context)
        return self._adapters[key]

    def _permission_gate(self, context: PluginContext):
        """动态权限受控接口（BUG-001 / 规格 4.3）：绑定到当前 Policy 授权集合。

        Adapter 在准备进入 COM / 网络 / 写操作前调用 gate(permission)；
        未授权即抛 PluginPermissionError。
        """
        from plugin_runtime.errors import PluginPermissionError

        def require(permission: str) -> None:
            if permission not in context.granted_permissions:
                raise PluginPermissionError(
                    self.plugin_id,
                    [f"{permission} (not granted by policy)"],
                    self.declared_permissions,
                )

        return require


def _config_key(context: PluginContext) -> str:
    ocr_options = context.ocr_options
    if ocr_options is None:
        ocr_key = "default"
    elif hasattr(ocr_options, "__dict__"):
        ocr_key = repr(sorted(vars(ocr_options).items(), key=lambda kv: kv[0]))
    else:
        ocr_key = repr(ocr_options)
    # 授权集合参与缓存键：不同 Policy 的 Reader 不得共享带权限 gate 的 Adapter
    granted_key = ",".join(sorted(context.granted_permissions))
    return f"{ocr_key}|granted={granted_key}"
