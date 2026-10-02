"""Permission / Policy（规格第 18 节）。

Plugin permission 是 HMBuddy Runtime Policy，不等价于操作系统安全沙箱：
Runtime 只保证"未声明的权限不会被 Runtime API 授予"，不提供 OS 级隔离。
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .contracts import PERMISSION_FILESYSTEM_READ
from .errors import PluginPermissionError


@dataclass
class PermissionPolicy:
    """Runtime 授权策略。

    默认只授予 filesystem.read（内置只读 Parser 所需，规格 18.1）；
    网络 / 进程执行 / 文件写 / COM 权限默认全部关闭（规格 18.2）。
    """

    granted: frozenset = field(default_factory=lambda: frozenset({PERMISSION_FILESYSTEM_READ}))

    def granted_permissions(self) -> frozenset:
        return self.granted

    def grants(self, permission: str) -> bool:
        return permission in self.granted

    def enforce(self, plugin_id: str, declared_permissions) -> frozenset:
        """返回该插件实际获得的权限交集；V0.1 中声明而未授予的权限不阻断
        只读执行，但被显式记录（AC-07 可观察性）。"""
        declared = frozenset(declared_permissions or ())
        return declared & self.granted

    def require(self, plugin_id: str, permission: str, declared_permissions) -> None:
        """Provider 请求使用某项权限时调用：未声明或未授权都显式报错。"""
        if permission not in (declared_permissions or ()):
            raise PluginPermissionError(
                plugin_id,
                [permission],
                declared_permissions,
            )
        if permission not in self.granted:
            raise PluginPermissionError(
                plugin_id,
                [f"{permission} (declared but not granted by policy)"],
                declared_permissions,
            )
