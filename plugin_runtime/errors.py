"""Plugin Runtime 基础异常（规格第 23 节 Error Model）。

在 Phase 1 的 ArtifactRuntimeError 之上叠加插件运行时错误；
ArtifactRuntimeError 的领域语义保持不变（上层 Desktop / CLI 兼容依赖）。
"""
from __future__ import annotations

from workspace.errors import ArtifactRuntimeError


class PluginRuntimeError(ArtifactRuntimeError):
    """插件运行时基础异常。"""

    def __init__(self, message: str, *, plugin_id: str | None = None):
        self.plugin_id = plugin_id
        super().__init__(message)


class PluginManifestError(PluginRuntimeError):
    """Manifest 缺失字段 / 非法值 / 未知权限等。"""


class PluginCompatibilityError(PluginRuntimeError):
    """api_version 等与 Runtime 不兼容（FR-L01）。"""


class PluginLoadError(PluginRuntimeError):
    """Entrypoint 不存在、类不符合 Contract、构造/加载失败（FR-L02）。"""


class DuplicatePluginError(PluginRuntimeError):
    """重复 plugin_id / provider 注册冲突（FR-L04），不静默覆盖。"""


class CapabilityNotFoundError(PluginRuntimeError):
    """Capability 无任何可用 Provider（ER-P01）。"""

    def __init__(self, capability: str, detail: str = ""):
        self.capability = capability
        message = f"no provider available for capability {capability!r}"
        if detail:
            message += f": {detail}"
        super().__init__(message)


class ProviderNotAvailableError(PluginRuntimeError):
    """有 Provider 但当前环境不可用（ER-P02）。"""

    def __init__(self, capability: str, plugin_id: str, provider_id: str):
        self.capability = capability
        self.plugin_id = plugin_id
        self.provider_id = provider_id
        super().__init__(
            f"provider {provider_id!r} (plugin {plugin_id!r}) "
            f"is not available for capability {capability!r}"
        )


class PluginPermissionError(PluginRuntimeError):
    """权限未声明 / 未授权（T8）。"""

    def __init__(self, plugin_id: str, missing_permissions, declared_permissions=None):
        self.plugin_id = plugin_id
        self.missing_permissions = tuple(missing_permissions)
        self.declared_permissions = tuple(declared_permissions or ())
        super().__init__(
            f"plugin {plugin_id!r} declares permissions {self.declared_permissions} "
            f"but policy grants only a subset; missing: {self.missing_permissions}"
        )


class ProviderExecutionError(PluginRuntimeError):
    """Provider 执行期非领域异常（ER-P03：保留 plugin/provider/capability/cause）。"""

    def __init__(
        self,
        message: str,
        *,
        plugin_id: str,
        provider_id: str,
        capability: str,
        cause=None,
    ):
        self.provider_id = provider_id
        self.capability = capability
        self.cause = cause
        super().__init__(message, plugin_id=plugin_id)
