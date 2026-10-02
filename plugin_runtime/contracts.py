"""Core Contract（规格 G1 / 第 10-13 节）：插件可依赖的最小稳定协议。

插件可以扩展实现，但不得自行改变本模块定义的契约。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Protocol, runtime_checkable

from workspace.artifact import Artifact, ArtifactRef, ArtifactLocator

__all__ = [
    "Artifact",
    "ArtifactRef",
    "ArtifactLocator",
    "CAPABILITY_READ_FULL",
    "IMPLEMENTED_CAPABILITIES",
    "RESERVED_CAPABILITY_NAMESPACES",
    "SUPPORTED_API_VERSION",
    "KNOWN_PERMISSIONS",
    "CapabilityRequest",
    "CapabilityResult",
    "PluginContext",
    "CapabilityProvider",
    "Plugin",
]

# ---------------------------------------------------------------------------
# Capability 命名规范（规格第 8 节）：<domain>.<verb>[.<mode>]
# ---------------------------------------------------------------------------

CAPABILITY_READ_FULL = "artifact.read.full"

# Phase 1.1 V0.1 必须实现的能力；其余仅定义命名规范
IMPLEMENTED_CAPABILITIES = (CAPABILITY_READ_FULL,)

# 预留 namespace（不实现，禁止插件自创语义重复的别名如 docx.read / artifact.open）
RESERVED_CAPABILITY_NAMESPACES = (
    "artifact.read.outline",
    "artifact.read.range",
    "artifact.search",
    "artifact.create",
    "artifact.update",
    "artifact.patch",
    "artifact.compare",
    "artifact.validate",
    "artifact.render",
    "artifact.convert",
    "artifact.ocr",
)

# Runtime 支持的插件 API 版本（FR-M03）
SUPPORTED_API_VERSION = 1

# 权限名称（FR-M05）
PERMISSION_FILESYSTEM_READ = "filesystem.read"
PERMISSION_FILESYSTEM_WRITE = "filesystem.write"
PERMISSION_NETWORK = "network"
PERMISSION_PROCESS_EXECUTE = "process.execute"
PERMISSION_OFFICE_COM = "office.com"
PERMISSION_WPS_COM = "wps.com"
KNOWN_PERMISSIONS = frozenset(
    {
        PERMISSION_FILESYSTEM_READ,
        PERMISSION_FILESYSTEM_WRITE,
        PERMISSION_NETWORK,
        PERMISSION_PROCESS_EXECUTE,
        PERMISSION_OFFICE_COM,
        PERMISSION_WPS_COM,
    }
)


# ---------------------------------------------------------------------------
# ArtifactLocator（规格第 13 节）：核心定义在 workspace.artifact，此处再导出
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# CapabilityRequest / CapabilityResult（规格第 11、12 节）
# ---------------------------------------------------------------------------


@dataclass
class CapabilityRequest:
    """调用方表达"要什么能力"，而不是"调用哪个 Adapter"。

    禁止把 Adapter 实例、python-docx Document 等实现对象放入 Request。
    """

    capability: str
    artifact_ref: Optional[ArtifactRef] = None
    locator: Optional[ArtifactLocator] = None
    options: dict = field(default_factory=dict)


@dataclass
class CapabilityResult:
    """统一包装执行结果。

    artifact.read.full 的 value 必须是 Artifact（P4），不得返回
    python-docx Document / openpyxl Workbook 等实现对象。
    """

    success: bool
    value: object | None
    provider_id: str
    plugin_id: str
    warnings: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    plugin_version: str = ""
    error: str | None = None


# ---------------------------------------------------------------------------
# PluginContext（规格 G1）
# ---------------------------------------------------------------------------


@dataclass
class PluginContext:
    """Runtime 提供给 Provider 的执行环境。

    resolved_path 是 Reader 已经过 Workspace 边界校验的路径（FR-S01）——
    Provider 应使用它，而不是直接信任外部传入路径。
    granted_permissions 是 Policy 实际授权的权限集合。
    require_permission(permission) 是受控的动态权限接口（BUG-001/4.3 节）：
    Provider 在准备进入 COM / 网络 / 写操作前必须调用它，未授权即抛
    PluginPermissionError。
    """

    resolved_path: Optional[Path] = None
    workspace_root: Optional[Path] = None
    ocr_options: Any = None
    granted_permissions: frozenset = frozenset({PERMISSION_FILESYSTEM_READ})
    plugin_dir: Optional[Path] = None
    require_permission: Optional[Any] = None
    services: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Provider / Plugin 协议（规格第 10 节）
# ---------------------------------------------------------------------------


@runtime_checkable
class CapabilityProvider(Protocol):
    provider_id: str
    plugin_id: str

    def supports(self, request: CapabilityRequest) -> bool: ...

    def is_available(self, context: PluginContext) -> bool: ...

    def execute(
        self,
        request: CapabilityRequest,
        context: PluginContext,
    ) -> CapabilityResult: ...


@runtime_checkable
class Plugin(Protocol):
    manifest: Any

    def providers(self) -> list: ...
