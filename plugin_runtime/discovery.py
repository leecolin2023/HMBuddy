"""Plugin Discovery（规格第 14 节）。

发现 ≠ 加载（FR-D03）：本模块只查找并校验 Manifest，不执行任何插件代码。
- 内置插件：仓库 plugins/ 下的直接子目录（examples/ 除外）；
- 外部插件：HMBUDDY_PLUGIN_PATH（os.pathsep 分隔多个目录）或显式传入目录。
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from .errors import PluginCompatibilityError, PluginManifestError
from .manifest import MANIFEST_FILENAME, PluginManifest, load_manifest

PLUGIN_ENV_VAR = "HMBUDDY_PLUGIN_PATH"
EXAMPLE_DIR_NAME = "examples"


@dataclass
class DiscoveredPlugin:
    manifest: PluginManifest
    plugin_dir: Path
    source: str  # builtin | external


@dataclass
class DiscoveryReport:
    builtins: list[DiscoveredPlugin] = field(default_factory=list)
    externals: list[DiscoveredPlugin] = field(default_factory=list)
    errors: list[tuple[str, str]] = field(default_factory=list)  # (location, error)

    @property
    def all_plugins(self) -> list[DiscoveredPlugin]:
        return self.builtins + self.externals


def _scan_dir(plugin_dir: Path, source: str, report: DiscoveryReport) -> None:
    """扫描一个目录下的插件子目录；单个损坏插件不影响其他插件（FR-D03）。"""
    if not plugin_dir.is_dir():
        report.errors.append((str(plugin_dir), "plugin directory does not exist"))
        return
    for entry in sorted(plugin_dir.iterdir()):
        if not entry.is_dir():
            continue
        if source == "builtin" and entry.name == EXAMPLE_DIR_NAME:
            continue  # examples/ 是外部插件样例，不随内置发现自动加载
        manifest_path = entry / MANIFEST_FILENAME
        if not manifest_path.is_file():
            continue
        try:
            manifest = load_manifest(manifest_path)
        except (PluginManifestError, PluginCompatibilityError) as exc:
            # FR-D03：Manifest 无效 / 不兼容都不执行插件代码、不影响其他插件，
            # 错误进入报告供 Plugin Manager 展示
            report.errors.append((str(manifest_path), str(exc)))
            continue
        discovered = DiscoveredPlugin(
            manifest=manifest, plugin_dir=entry, source=source
        )
        (report.builtins if source == "builtin" else report.externals).append(discovered)


def builtin_plugins_root() -> Path:
    """仓库 plugins/ 目录（plugin_runtime/discovery.py 的上一级）。"""
    return Path(__file__).resolve().parent.parent / "plugins"


def discover_builtin(report: DiscoveryReport | None = None) -> DiscoveryReport:
    """FR-D01：发现 HMBuddy 自带插件，不手工逐个 import。"""
    report = report or DiscoveryReport()
    _scan_dir(builtin_plugins_root(), "builtin", report)
    return report


def external_plugin_dirs_from_env(env=None) -> list[Path]:
    env = os.environ if env is None else env
    raw = env.get(PLUGIN_ENV_VAR, "")
    dirs: list[Path] = []
    for item in raw.split(os.pathsep):
        item = item.strip()
        if item:
            dirs.append(Path(item).expanduser())
    return dirs


def discover_external(
    directories: list[Path] | None = None,
    env=None,
    report: DiscoveryReport | None = None,
) -> DiscoveryReport:
    """FR-D02：从外部插件目录发现插件（HMBUDDY_PLUGIN_PATH 或显式目录）。"""
    report = report or DiscoveryReport()
    if not directories:
        directories = external_plugin_dirs_from_env(env)
    for directory in directories:
        _scan_dir(Path(directory).expanduser(), "external", report)
    return report
