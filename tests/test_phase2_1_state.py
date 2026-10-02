"""Phase 2.1 T2/T3/T4 — AppState / Recent Workspace / Recent Activity。"""
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

from application.state import (
    AppState,
    LastView,
    RecentActivityEntry,
    RecentWorkspace,
    clear_recent_workspaces,
    load_state,
    pin_workspace,
    record_activity,
    record_workspace_open,
    remove_workspace,
    save_state,
    sort_recent_workspaces,
    workspace_entry_for,
)


def _iso(offset_seconds=0):
    return (
        datetime(2026, 10, 2, 12, 0, 0, tzinfo=timezone.utc) + timedelta(seconds=offset_seconds)
    ).isoformat()


# ---------------------------------------------------------------------------
# T2 State 持久化
# ---------------------------------------------------------------------------


def test_state_roundtrip_and_schema_version(tmp_path):
    state = AppState()
    state.last_view = LastView(page="workspace", workspace_path="D:/ws")
    record_workspace_open(state, "D:/ws", limit=10, opened_at=_iso(0))
    path = tmp_path / "state.json"
    save_state(state, path)

    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["schema_version"] == 1  # AC-06
    assert not list(tmp_path.glob("*.tmp"))  # AC-05 原子写无残留

    loaded, errors = load_state(path)
    assert errors == []
    assert loaded.last_view.page == "workspace"
    assert [item.path for item in loaded.recent_workspaces] == [
        str(Path("D:/ws").expanduser())
    ]


def test_state_corrupt_recovery_keeps_original(tmp_path):
    """ER-03：损坏 State → 保留原文件（.corrupt）→ 空 State 继续启动。"""
    path = tmp_path / "state.json"
    path.write_text("{ corrupt", encoding="utf-8")
    state, errors = load_state(path)
    assert state.recent_workspaces == []
    assert errors
    corrupt_file = tmp_path / "state.json.corrupt"
    assert corrupt_file.read_text(encoding="utf-8") == "{ corrupt"
    assert not path.exists() or json.loads(path.read_text(encoding="utf-8"))


def test_state_unknown_activity_type_ignored(tmp_path):
    path = tmp_path / "state.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "recent_activity": [
                    {"activity_type": "agent_task", "title": "非法条目"},
                    {"activity_type": "artifact", "title": "合法条目"},
                ],
            }
        ),
        encoding="utf-8",
    )
    state, errors = load_state(path)
    assert len(state.recent_activity) == 1
    assert state.recent_activity[0].title == "合法条目"
    assert errors


# ---------------------------------------------------------------------------
# T3 Recent Workspace 行为
# ---------------------------------------------------------------------------


def test_t3_record_open_deduplicate_and_update():
    state = AppState()
    record_workspace_open(state, "D:/ws/a", limit=10, opened_at=_iso(0))
    record_workspace_open(state, "D:/ws/A/", limit=10, opened_at=_iso(100))  # 归一去重
    assert len(state.recent_workspaces) == 1
    assert state.recent_workspaces[0].last_opened_at == _iso(100)


def test_t3_limit_evicts_oldest_unpinned():
    state = AppState()
    for index in range(5):
        record_workspace_open(state, f"D:/ws/{index}", limit=3, opened_at=_iso(index))
    assert len(state.recent_workspaces) == 3
    paths = {item.path for item in state.recent_workspaces}
    assert str(Path("D:/ws/0").expanduser()) not in paths  # 最旧被淘汰
    assert str(Path("D:/ws/4").expanduser()) in paths


def test_t3_pinned_survives_limit_and_sorts_first():
    state = AppState()
    record_workspace_open(state, "D:/ws/0", limit=3, opened_at=_iso(0))
    pin_workspace(state, "D:/ws/0", True)  # 先置顶，再灌满触发淘汰
    for index in range(1, 5):
        record_workspace_open(state, f"D:/ws/{index}", limit=3, opened_at=_iso(index))
    assert workspace_entry_for(state, "D:/ws/0") is not None  # pinned 不被淘汰
    assert len(state.recent_workspaces) == 4  # 3 个非 pinned + 1 个 pinned
    ordered = sort_recent_workspaces(state)
    assert ordered[0].path == str(Path("D:/ws/0").expanduser())
    assert ordered[0].pinned is True


def test_t3_remove_and_clear_keeps_pinned():
    state = AppState()
    record_workspace_open(state, "D:/ws/a", limit=10, opened_at=_iso(0))
    record_workspace_open(state, "D:/ws/b", limit=10, opened_at=_iso(1))
    pin_workspace(state, "D:/ws/b", True)

    assert remove_workspace(state, "D:/ws/a") is True
    assert remove_workspace(state, "D:/ws/a") is False
    removed = clear_recent_workspaces(state, keep_pinned=True)
    assert removed == 0  # 只剩 pinned，无可清
    record_workspace_open(state, "D:/ws/c", limit=10, opened_at=_iso(2))
    removed = clear_recent_workspaces(state, keep_pinned=True)
    assert removed == 1
    assert [item.path for item in state.recent_workspaces] == [
        str(Path("D:/ws/b").expanduser())
    ]


# ---------------------------------------------------------------------------
# T4 Recent Activity 行为
# ---------------------------------------------------------------------------


def test_t4_activity_types_order_and_limit():
    state = AppState()
    record_activity(
        state, "workspace", workspace_path="D:/ws/a", title="打开工作区",
        limit=3, opened_at=_iso(0),
    )
    record_activity(
        state, "artifact", workspace_path="D:/ws/a", artifact_path="D:/ws/a/1.docx",
        title="1.docx", limit=3, opened_at=_iso(1),
    )
    record_activity(
        state, "artifact_qa", workspace_path="D:/ws/a", artifact_path="D:/ws/a/1.docx",
        title="文档问答", limit=3, opened_at=_iso(2),
    )
    record_activity(
        state, "artifact", workspace_path="D:/ws/b", artifact_path="D:/ws/b/2.xlsx",
        title="2.xlsx", limit=3, opened_at=_iso(3),
    )
    assert len(state.recent_activity) == 3  # limit 生效
    assert state.recent_activity[0].activity_type == "artifact"  # 最新在前
    assert state.recent_activity[0].artifact_path.endswith("2.xlsx")


def test_t4_same_activity_updates_instead_of_duplicates():
    state = AppState()
    record_activity(state, "artifact", artifact_path="D:/a.docx", title="a", limit=10,
                    opened_at=_iso(0))
    record_activity(state, "artifact", artifact_path="D:/a.docx", title="a reopened",
                    limit=10, opened_at=_iso(50))
    assert len(state.recent_activity) == 1
    assert state.recent_activity[0].title == "a reopened"
    assert state.recent_activity[0].last_opened_at == _iso(50)


def test_t4_resume_view_present_and_no_content_persisted():
    """T4 / AC-12/13：resume_view 可恢复上下文；条目字段为白名单，无正文/Prompt/Answer。"""
    state = AppState()
    entry = record_activity(
        state,
        "artifact_qa",
        workspace_path="D:/ws",
        artifact_path="D:/ws/报告.docx",
        title="报告问答",
        resume_view={"page": "workspace", "artifact": "D:/ws/报告.docx"},
        limit=10,
    )
    assert entry.resume_view == {"page": "workspace", "artifact": "D:/ws/报告.docx"}
    # 结构级断言：条目字段白名单（规格第 16/36 节）
    assert set(entry.__dict__) == {
        "entry_id", "activity_type", "workspace_path", "artifact_path",
        "title", "last_opened_at", "resume_view",
    }
    # 持久化 JSON 同样只含白名单字段，体量远小于任何正文/Prompt
    import json as _json

    serialized = _json.dumps(entry.__dict__, ensure_ascii=False)
    assert "报告.docx" in serialized
    assert len(serialized) < 500


def test_t4_unknown_activity_type_rejected():
    state = AppState()
    with pytest.raises(ValueError, match="unknown activity type"):
        record_activity(state, "agent_task", title="不得提前长出 Task 域")
