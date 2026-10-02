"""Recent Workspaces / Recent Activity（规格 G4-G5 / 第 16-19 节）。

模型与行为定义在 application/state.py（Config/State 分离、同一持久化单元），
本模块按规格第 7 节的模块建议名再导出，供页面与测试引用。
"""
from .state import (
    ACTIVITY_ARTIFACT,
    ACTIVITY_ARTIFACT_QA,
    ACTIVITY_TYPES,
    ACTIVITY_WORKSPACE,
    RecentActivityEntry,
    RecentWorkspace,
    clear_recent_workspaces,
    pin_workspace,
    record_activity,
    record_workspace_open,
    remove_workspace,
    sort_recent_workspaces,
    workspace_entry_for,
)

__all__ = [
    "ACTIVITY_ARTIFACT",
    "ACTIVITY_ARTIFACT_QA",
    "ACTIVITY_TYPES",
    "ACTIVITY_WORKSPACE",
    "RecentActivityEntry",
    "RecentWorkspace",
    "clear_recent_workspaces",
    "pin_workspace",
    "record_activity",
    "record_workspace_open",
    "remove_workspace",
    "sort_recent_workspaces",
    "workspace_entry_for",
]
