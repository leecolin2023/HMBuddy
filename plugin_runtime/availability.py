"""Availability 检查（BUG-008 / 规格 11 节）。

Manifest 的 platforms 与 runtime.python 必须真实参与路由；
Provider 还可通过 probe_dependencies() 声明依赖探针。
不满足时由 Router 抛 ProviderNotAvailableError，不进入 execute。
"""
from __future__ import annotations

import re
import sys

_PLATFORM_ALIASES = {
    "windows": ("win32", "cygwin"),
    "linux": ("linux",),
    "darwin": ("darwin",),
}


def platform_unavailable_reason(platforms) -> str | None:
    """manifest.platforms 与当前平台不符时返回原因，否则 None。"""
    normalized = [str(item).lower() for item in (platforms or [])]
    if not normalized:
        return None
    current = sys.platform.lower()
    for platform_name in normalized:
        for alias in _PLATFORM_ALIASES.get(platform_name, (platform_name,)):
            if current.startswith(alias):
                return None
    return f"platform {current!r} not in manifest platforms {normalized}"


def _parse_spec(python_requires: str):
    """解析 ">=X.Y" / ">=X.Y.Z" 约束 → (version_tuple, precision)；其他形式返回 (None, 0)。"""
    matched = re.fullmatch(
        r">=\s*(\d+)(?:\.(\d+))?(?:\.(\d+))?", (python_requires or "").strip()
    )
    if not matched:
        return None, 0
    version = (
        int(matched.group(1)),
        int(matched.group(2) or 0),
        int(matched.group(3) or 0),
    )
    precision = 1 + sum(1 for group in (matched.group(2), matched.group(3)) if group)
    return version, precision


def python_unavailable_reason(python_requires: str) -> str | None:
    """manifest.runtime.python 与当前解释器不符时返回原因，否则 None。"""
    required, precision = _parse_spec(python_requires)
    if required is None:
        return None
    current = sys.version_info[:3]
    if current[:precision] >= required[:precision]:
        return None
    return (
        f"python {sys.version.split()[0]} does not satisfy "
        f"runtime.python {python_requires!r}"
    )
