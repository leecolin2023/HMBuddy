"""AppState（规格第 14-18、35-37 节）：应用"最近发生过什么"的轻量状态。

- 与 Config 严格分离（独立文件、独立语义，AC-03）；
- 原子写（AC-05）、schema_version（AC-06）、损坏可恢复（ER-03）；
- 只保存可恢复的导航/Workspace 元数据，禁止正文/Prompt/密钥/任意对象（第 36 节）；
- 不建立 Session / Task 域（AC-12/13）：RecentActivityEntry 只是 UI 导航历史。
"""
from __future__ import annotations

import json
import logging
import os
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

LOGGER = logging.getLogger("hmbuddy.state")

STATE_SCHEMA_VERSION = 1

# RecentActivityEntry 合法类型（规格第 16 节）
ACTIVITY_WORKSPACE = "workspace"
ACTIVITY_ARTIFACT = "artifact"
ACTIVITY_ARTIFACT_QA = "artifact_qa"
ACTIVITY_TYPES = (ACTIVITY_WORKSPACE, ACTIVITY_ARTIFACT, ACTIVITY_ARTIFACT_QA)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class LastView:
    page: str = "home"
    workspace_path: str = ""
    artifact_path: str = ""


@dataclass
class RecentWorkspace:
    """最近工作区（规格第 18 节）：排序 Pinned → last_opened_at DESC，
    pinned 项不因 limit 自动淘汰。"""

    workspace_id: str
    path: str
    display_name: str
    last_opened_at: str
    pinned: bool = False
    last_artifact_path: str = ""


@dataclass
class RecentActivityEntry:
    """最近活动（规格第 16 节）：只表达"最近在哪做过什么、从哪重新进入"。

    禁止保存：Agent 执行状态、Tool Call Stack、LLM hidden state、
    完整 Prompt/Answer、Artifact 正文。
    """

    entry_id: str
    activity_type: str
    workspace_path: str = ""
    artifact_path: str = ""
    title: str = ""
    last_opened_at: str = ""
    resume_view: dict = field(default_factory=dict)


@dataclass
class AppState:
    schema_version: int = STATE_SCHEMA_VERSION
    last_view: LastView = field(default_factory=LastView)
    recent_workspaces: list[RecentWorkspace] = field(default_factory=list)
    recent_activity: list[RecentActivityEntry] = field(default_factory=list)


# ---------------------------------------------------------------------------
# 持久化（规格第 35 节）
# ---------------------------------------------------------------------------


def _parse_state(data: Any, errors: list[str]) -> AppState:
    state = AppState()
    if not isinstance(data, dict):
        errors.append("state 根节点必须是 JSON 对象")
        return state

    version = data.get("schema_version", STATE_SCHEMA_VERSION)
    if version != STATE_SCHEMA_VERSION:
        errors.append(f"state schema_version {version!r} != {STATE_SCHEMA_VERSION}")

    last_view = data.get("last_view") or {}
    if isinstance(last_view, dict):
        state.last_view = LastView(
            page=str(last_view.get("page") or "home"),
            workspace_path=str(last_view.get("workspace_path") or ""),
            artifact_path=str(last_view.get("artifact_path") or ""),
        )

    for item in data.get("recent_workspaces") or []:
        if not isinstance(item, dict):
            errors.append("recent_workspaces 含非法条目，已忽略")
            continue
        state.recent_workspaces.append(
            RecentWorkspace(
                workspace_id=str(item.get("workspace_id") or uuid.uuid4().hex[:12]),
                path=str(item.get("path") or ""),
                display_name=str(item.get("display_name") or ""),
                last_opened_at=str(item.get("last_opened_at") or ""),
                pinned=bool(item.get("pinned")),
                last_artifact_path=str(item.get("last_artifact_path") or ""),
            )
        )

    for item in data.get("recent_activity") or []:
        if not isinstance(item, dict):
            errors.append("recent_activity 含非法条目，已忽略")
            continue
        activity_type = str(item.get("activity_type") or "")
        if activity_type not in ACTIVITY_TYPES:
            errors.append(f"未知 activity_type {activity_type!r}，已忽略")
            continue
        state.recent_activity.append(
            RecentActivityEntry(
                entry_id=str(item.get("entry_id") or uuid.uuid4().hex[:12]),
                activity_type=activity_type,
                workspace_path=str(item.get("workspace_path") or ""),
                artifact_path=str(item.get("artifact_path") or ""),
                title=str(item.get("title") or ""),
                last_opened_at=str(item.get("last_opened_at") or ""),
                resume_view=dict(item.get("resume_view") or {}),
            )
        )
    return state


def load_state(path: Path) -> tuple[AppState, list[str]]:
    """加载 AppState；损坏时保留原文件（改名 .corrupt）并返回空 State（ER-03）。"""
    path = Path(path)
    errors: list[str] = []
    if not path.is_file():
        return AppState(), errors
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
        corrupt_path = path.with_suffix(path.suffix + ".corrupt")
        try:
            os.replace(path, corrupt_path)
            errors.append(
                f"state.json 损坏（已保留为 {corrupt_path.name}），使用空状态继续：{exc}"
            )
        except OSError:
            errors.append(f"state.json 损坏且无法归档：{exc}")
        LOGGER.warning("state corrupt: %s", exc)
        return AppState(), errors
    return _parse_state(data, errors), errors


def save_state(state: AppState, path: Path) -> None:
    """原子写（规格 35.1）。AppState 序列化只包含白名单字段（第 36 节）。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    payload = json.dumps(asdict(state), ensure_ascii=False, indent=2) + "\n"
    with open(tmp_path, "w", encoding="utf-8") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp_path, path)
    LOGGER.info("state saved path=%s", path)


# ---------------------------------------------------------------------------
# Recent 行为（规格第 18-19 节）
# ---------------------------------------------------------------------------


def _normalize_path(path: str | Path) -> str:
    """展开用户目录并规范化分隔符（保留大小写用于展示）。"""
    raw = str(path)
    if not raw:
        return ""
    return os.path.normpath(str(Path(raw).expanduser()))


def _path_key(path: str | Path) -> str:
    """路径比较键：Windows 大小写不敏感，POSIX 敏感；空路径比较为相等。"""
    normalized = _normalize_path(path)
    return os.path.normcase(normalized) if normalized else ""


def record_workspace_open(
    state: AppState,
    workspace_path: str | Path,
    *,
    limit: int = 10,
    display_name: str | None = None,
    opened_at: str | None = None,
) -> RecentWorkspace:
    """RW-01 Open：去重（按归一路径）、更新时间、置顶不淘汰（规格第 18 节）。"""
    normalized = _normalize_path(workspace_path)
    opened_at = opened_at or _utc_now_iso()
    normalized_key = _path_key(workspace_path)
    existing = next(
        (
            item
            for item in state.recent_workspaces
            if _path_key(item.path) == normalized_key
        ),
        None,
    )
    if existing is not None:
        existing.last_opened_at = opened_at
        if display_name:
            existing.display_name = display_name
        entry = existing
    else:
        entry = RecentWorkspace(
            workspace_id=uuid.uuid4().hex[:12],
            path=normalized,
            display_name=display_name or Path(normalized).name,
            last_opened_at=opened_at,
        )
        state.recent_workspaces.append(entry)

    _enforce_workspace_limit(state, limit)
    return entry


def _enforce_workspace_limit(state: AppState, limit: int) -> None:
    """pinned 不淘汰；非 pinned 按 last_opened_at 保留最近 N 个。"""
    unpinned = [item for item in state.recent_workspaces if not item.pinned]
    overflow = len(unpinned) - max(limit, 0)
    if overflow <= 0:
        return
    unpinned.sort(key=lambda item: item.last_opened_at)
    for stale in unpinned[:overflow]:
        state.recent_workspaces.remove(stale)


def sort_recent_workspaces(state: AppState) -> list[RecentWorkspace]:
    """排序：Pinned → last_opened_at DESC（规格第 18 节）。"""
    return sorted(
        state.recent_workspaces,
        key=lambda item: (not item.pinned, _sort_key_reverse(item.last_opened_at)),
    )


def _sort_key_reverse(iso: str) -> tuple:
    # ISO 时间字符串的字典序即时间序；DESC 通过取负实现
    try:
        parsed = datetime.fromisoformat(iso)
    except ValueError:
        parsed = datetime.min.replace(tzinfo=timezone.utc)
    stamp = parsed.timestamp()
    return (-stamp,)


def workspace_entry_for(state: AppState, workspace_path: str | Path):
    normalized_key = _path_key(workspace_path)
    return next(
        (
            item
            for item in state.recent_workspaces
            if _path_key(item.path) == normalized_key
        ),
        None,
    )


def pin_workspace(state: AppState, workspace_path: str | Path, pinned: bool = True) -> bool:
    entry = workspace_entry_for(state, workspace_path)
    if entry is None:
        return False
    entry.pinned = pinned
    return True


def remove_workspace(state: AppState, workspace_path: str | Path) -> bool:
    """RW-02 Remove：用户显式移除（缺失路径也允许移除）。"""
    entry = workspace_entry_for(state, workspace_path)
    if entry is None:
        return False
    state.recent_workspaces.remove(entry)
    return True


def clear_recent_workspaces(state: AppState, keep_pinned: bool = True) -> int:
    """RW-03 Clear：默认保留 pinned（规格第 19 节）。"""
    removed = 0
    for entry in list(state.recent_workspaces):
        if keep_pinned and entry.pinned:
            continue
        state.recent_workspaces.remove(entry)
        removed += 1
    return removed


def record_activity(
    state: AppState,
    activity_type: str,
    *,
    workspace_path: str = "",
    artifact_path: str = "",
    title: str = "",
    resume_view: dict | None = None,
    limit: int = 20,
    opened_at: str | None = None,
) -> RecentActivityEntry:
    """T4：记录导航型活动；同类型+同路径的旧条目更新时间并置顶。"""
    if activity_type not in ACTIVITY_TYPES:
        raise ValueError(f"unknown activity type: {activity_type!r}")
    opened_at = opened_at or _utc_now_iso()
    normalized_workspace = _normalize_path(workspace_path) if workspace_path else ""
    normalized_artifact = _normalize_path(artifact_path) if artifact_path else ""
    workspace_key = _path_key(workspace_path) if workspace_path else ""
    artifact_key = _path_key(artifact_path) if artifact_path else ""

    existing = next(
        (
            item
            for item in state.recent_activity
            if item.activity_type == activity_type
            and _path_key(item.workspace_path) == workspace_key
            and _path_key(item.artifact_path) == artifact_key
        ),
        None,
    )
    if existing is not None:
        existing.last_opened_at = opened_at
        if title:
            existing.title = title
        if resume_view is not None:
            existing.resume_view = resume_view
        state.recent_activity.remove(existing)
        entry = existing
    else:
        entry = RecentActivityEntry(
            entry_id=uuid.uuid4().hex[:12],
            activity_type=activity_type,
            workspace_path=normalized_workspace,
            artifact_path=normalized_artifact,
            title=title,
            last_opened_at=opened_at,
            resume_view=dict(resume_view or {}),
        )
    state.recent_activity.insert(0, entry)
    # limit 只约束数量；不涉及 pinned 概念
    del state.recent_activity[limit:]
    return entry
