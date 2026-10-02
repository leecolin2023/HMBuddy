"""Plugin Manifest（规格第 9 节）。

首版 Manifest 使用 JSON（plugin.json）——规格第 9 节明确允许为减少运行依赖
选择 JSON，且内网离线环境不必为此引入 PyYAML。实现统一只用一种格式。
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .contracts import KNOWN_PERMISSIONS, SUPPORTED_API_VERSION
from .errors import PluginCompatibilityError, PluginManifestError

MANIFEST_FILENAME = "plugin.json"

_PLUGIN_ID_RE = re.compile(r"^[a-z][a-z0-9]*(\.[a-z][a-z0-9_-]*){1,5}$")
_SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")


@dataclass
class CapabilityDeclaration:
    """Manifest 中的一条能力声明（FR-M04）。"""

    id: str
    priority: int = 100


@dataclass
class PluginManifest:
    id: str
    name: str
    version: str
    api_version: int
    entrypoint_module: str
    entrypoint_class: str
    extensions: list[str] = field(default_factory=list)
    capabilities: list[CapabilityDeclaration] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    platforms: list[str] = field(default_factory=list)
    python_requires: str = ""
    description: str = ""
    # 以下为 Runtime 附加信息，不属于 Manifest 本体
    source: str = "builtin"  # builtin | external
    plugin_dir: Path | None = None

    def capability_ids(self) -> list[str]:
        return [item.id for item in self.capabilities]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "api_version": self.api_version,
            "entrypoint": {
                "module": self.entrypoint_module,
                "class": self.entrypoint_class,
            },
            "accepts": {"extensions": list(self.extensions)},
            "capabilities": [
                {"id": item.id, "priority": item.priority}
                for item in self.capabilities
            ],
            "permissions": list(self.permissions),
            "platforms": list(self.platforms),
            "runtime": {"python": self.python_requires},
            "description": self.description,
            "source": self.source,
            "plugin_dir": str(self.plugin_dir) if self.plugin_dir else None,
        }


def _require(data: dict, key: str, path: Path) -> Any:
    if key not in data or data[key] in (None, ""):
        raise PluginManifestError(
            f"manifest {path}: missing required field {key!r}"
        )
    return data[key]


def parse_manifest(data: dict, path: Path | None = None) -> PluginManifest:
    """校验并构造 Manifest（规格 T1 覆盖的全部非法情形在此报错）。"""
    display = str(path or "<manifest>")

    plugin_id = str(_require(data, "id", display))
    if not _PLUGIN_ID_RE.match(plugin_id):
        raise PluginManifestError(
            f"manifest {display}: invalid plugin id {plugin_id!r} "
            "(expected dotted lowercase, e.g. hmbuddy.docx.core)"
        )

    name = str(_require(data, "name", display))

    version = str(_require(data, "version", display))
    if not _SEMVER_RE.match(version):
        raise PluginManifestError(
            f"manifest {display}: invalid version {version!r} "
            "(expected SemVer major.minor.patch)"
        )

    api_version = _require(data, "api_version", display)
    if not isinstance(api_version, int) or isinstance(api_version, bool):
        raise PluginManifestError(
            f"manifest {display}: api_version must be an integer"
        )
    if api_version != SUPPORTED_API_VERSION:
        # FR-L01：不兼容的 API Version 在校验阶段即拒绝
        raise PluginCompatibilityError(
            f"manifest {display}: api_version {api_version} is not supported "
            f"(runtime supports {SUPPORTED_API_VERSION})",
            plugin_id=plugin_id,
        )

    entrypoint = data.get("entrypoint")
    if not isinstance(entrypoint, dict):
        raise PluginManifestError(f"manifest {display}: missing entrypoint mapping")
    entrypoint_module = str(_require(entrypoint, "module", display))
    entrypoint_class = str(_require(entrypoint, "class", display))

    accepts = data.get("accepts") or {}
    if not isinstance(accepts, dict):
        raise PluginManifestError(f"manifest {display}: accepts must be a mapping")
    extensions_raw = accepts.get("extensions") or []
    if not isinstance(extensions_raw, list) or not extensions_raw:
        raise PluginManifestError(
            f"manifest {display}: accepts.extensions must be a non-empty list"
        )
    extensions = []
    for item in extensions_raw:
        ext = str(item).lower()
        if not ext.startswith(".") or len(ext) < 2:
            raise PluginManifestError(
                f"manifest {display}: invalid extension {item!r} (expected like '.docx')"
            )
        extensions.append(ext)

    capabilities_raw = data.get("capabilities") or []
    if not isinstance(capabilities_raw, list) or not capabilities_raw:
        raise PluginManifestError(
            f"manifest {display}: capabilities must be a non-empty list"
        )
    capabilities: list[CapabilityDeclaration] = []
    seen_capabilities: set[str] = set()
    for item in capabilities_raw:
        if isinstance(item, str):
            item = {"id": item}
        if not isinstance(item, dict) or "id" not in item:
            raise PluginManifestError(
                f"manifest {display}: each capability needs an id"
            )
        capability_id = str(item["id"])
        if capability_id in seen_capabilities:
            raise PluginManifestError(
                f"manifest {display}: duplicate capability {capability_id!r}"
            )
        seen_capabilities.add(capability_id)
        priority = item.get("priority", 100)
        if not isinstance(priority, int) or isinstance(priority, bool):
            raise PluginManifestError(
                f"manifest {display}: capability {capability_id!r} priority must be int"
            )
        capabilities.append(CapabilityDeclaration(id=capability_id, priority=priority))

    permissions_raw = data.get("permissions") or []
    if not isinstance(permissions_raw, list):
        raise PluginManifestError(f"manifest {display}: permissions must be a list")
    permissions: list[str] = []
    for item in permissions_raw:
        permission = str(item)
        if permission not in KNOWN_PERMISSIONS:
            raise PluginManifestError(
                f"manifest {display}: unknown permission {permission!r}; "
                f"known: {sorted(KNOWN_PERMISSIONS)}"
            )
        if permission not in permissions:
            permissions.append(permission)

    platforms_raw = data.get("platforms") or []
    platforms = [str(item).lower() for item in platforms_raw] if isinstance(platforms_raw, list) else []

    runtime_section = data.get("runtime") or {}
    python_requires = str(runtime_section.get("python", "")) if isinstance(runtime_section, dict) else ""

    return PluginManifest(
        id=plugin_id,
        name=name,
        version=version,
        api_version=api_version,
        entrypoint_module=entrypoint_module,
        entrypoint_class=entrypoint_class,
        extensions=extensions,
        capabilities=capabilities,
        permissions=permissions,
        platforms=platforms,
        python_requires=python_requires,
        description=str(data.get("description", "")),
    )


def load_manifest(path: Path) -> PluginManifest:
    """从 plugin.json 文件读取并校验 Manifest（FR-D03：无效 Manifest 不执行插件代码）。"""
    path = Path(path)
    if not path.is_file():
        raise PluginManifestError(f"manifest file not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise PluginManifestError(f"manifest {path}: invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise PluginManifestError(f"manifest {path}: top level must be an object")
    manifest = parse_manifest(data, path)
    manifest.plugin_dir = path.parent
    return manifest
