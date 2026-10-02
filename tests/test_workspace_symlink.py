"""FR-S02 — Workspace 符号链接边界测试：插件化不得削弱边界。"""
import os

import pytest

from workspace.errors import WorkspaceBoundaryError
from workspace.workspace import Workspace

pytestmark = pytest.mark.skipif(
    not hasattr(os, "symlink"), reason="平台不支持 symlink"
)


@pytest.fixture()
def linked_workspace(tmp_path):
    """workspace/link.docx → workspace 外部真实文件。"""
    ws_root = tmp_path / "ws"
    ws_root.mkdir()
    outside = tmp_path / "outside" / "secret.docx"
    outside.parent.mkdir()
    outside.write_bytes(b"outside-bytes")
    link = ws_root / "link.docx"
    try:
        os.symlink(outside, link)
    except OSError as exc:
        pytest.skip(f"无法创建符号链接（需要开发者模式/管理员权限）: {exc}")
    return ws_root, link, outside


def test_symlink_escaping_workspace_is_blocked(linked_workspace):
    ws_root, link, _ = linked_workspace
    workspace = Workspace(ws_root)
    with pytest.raises(WorkspaceBoundaryError):
        workspace.resolve_path(link)


def test_symlink_escape_blocked_in_read_artifact(linked_workspace):
    from services.artifact_reader import read_artifact

    ws_root, link, _ = linked_workspace
    with pytest.raises(WorkspaceBoundaryError):
        read_artifact(link, workspace=Workspace(ws_root))


def test_symlink_inside_workspace_allowed(tmp_path):
    """指向 Workspace 内部目标的链接不受影响。"""
    ws_root = tmp_path / "ws"
    ws_root.mkdir()
    real = ws_root / "real.txt"
    real.write_text("inside", encoding="utf-8")
    link = ws_root / "link.txt"
    try:
        os.symlink(real, link)
    except OSError as exc:
        pytest.skip(f"无法创建符号链接: {exc}")
    workspace = Workspace(ws_root)
    assert workspace.resolve_path(link) == real.resolve()
