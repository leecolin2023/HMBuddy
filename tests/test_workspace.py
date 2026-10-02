"""Workspace 扫描器单元测试（规格第 9 节 FR-W01 ~ FR-W04）。"""
import os
import sys

import pytest

from workspace.errors import WorkspaceBoundaryError
from workspace.workspace import Workspace


@pytest.fixture()
def ws_dir(tmp_path):
    """构造一个含四类支持文件与各种噪声文件的测试目录。"""
    (tmp_path / "a.docx").write_bytes(b"docx")
    (tmp_path / "b.pdf").write_bytes(b"pdf")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "c.xlsx").write_bytes(b"xlsx")
    (sub / "deep").mkdir()
    (sub / "deep" / "d.pptx").write_bytes(b"pptx")
    # 噪声：临时 / 隐藏 / 不支持
    (tmp_path / "~$a.docx").write_bytes(b"temp")
    (tmp_path / "~WRD0001.tmp").write_bytes(b"temp")
    (tmp_path / ".hidden.docx").write_bytes(b"hidden")
    (tmp_path / ".DS_Store").write_bytes(b"junk")
    (tmp_path / "Thumbs.db").write_bytes(b"junk")
    (tmp_path / "Desktop.ini").write_bytes(b"junk")
    (tmp_path / "x.tmp").write_bytes(b"temp")
    (tmp_path / "evil.exe").write_bytes(b"exe")
    (tmp_path / "notes.txt").write_bytes(b"text")
    return tmp_path


def test_list_artifacts_finds_supported_files(ws_dir):
    workspace = Workspace(ws_dir)
    refs = workspace.list_artifacts()
    names = {ref.name for ref in refs}
    assert names == {"a.docx", "b.pdf", "c.xlsx", "d.pptx", "notes.txt"}
    types = {ref.name: ref.artifact_type for ref in refs}
    assert types == {
        "a.docx": "docx",
        "b.pdf": "pdf",
        "c.xlsx": "xlsx",
        "d.pptx": "pptx",
        "notes.txt": "txt",
    }


def test_refs_are_sorted_and_fields_filled(ws_dir):
    workspace = Workspace(ws_dir)
    refs = workspace.list_artifacts()
    paths = [ref.path for ref in refs]
    assert paths == sorted(paths)
    for ref in refs:
        assert ref.size > 0
        assert ref.extension == ref.name.rsplit(".", 1)[1]
        assert ref.modified_at.tzinfo is not None
        assert os.path.isabs(ref.path)
        assert ref.path.startswith(str(workspace.root_path))
        assert ref.artifact_id.startswith("a_")


def test_artifact_id_stable_across_scans(ws_dir):
    workspace = Workspace(ws_dir)
    first = {ref.name: ref.artifact_id for ref in workspace.list_artifacts()}
    second = {ref.name: ref.artifact_id for ref in workspace.list_artifacts()}
    assert first == second


def test_optional_extensions_only_when_requested(ws_dir):
    (ws_dir / "config.ini").write_bytes(b"[section]\nkey=value\n")
    # 默认核心扩展集不包含 .ini
    default_refs = Workspace(ws_dir).list_artifacts()
    assert all(ref.extension != "ini" for ref in default_refs)

    extended = Workspace(ws_dir, extra_extensions={".ini": "txt"}).list_artifacts()
    names = {ref.name for ref in extended}
    assert "config.ini" in names


@pytest.mark.skipif(sys.platform != "win32", reason="Windows 隐藏属性")
def test_windows_hidden_attribute_ignored(ws_dir):
    target = ws_dir / "secret.docx"
    target.write_bytes(b"hidden-by-attribute")
    os.system(f'attrib +h "{target}"')
    try:
        names = {ref.name for ref in Workspace(ws_dir).list_artifacts()}
        assert "secret.docx" not in names
    finally:
        os.system(f'attrib -h "{target}"')


def test_is_temp_or_hidden_rules():
    for name in ["~$a.docx", "~WRD0001.tmp", ".DS_Store", ".hidden.docx",
                 "Thumbs.db", "Desktop.ini", "x.tmp", ".a"]:
        assert Workspace.is_temp_or_hidden(name), name
    for name in ["a.docx", "报表.xlsx", "quarter.pdf", "team.pptx"]:
        assert not Workspace.is_temp_or_hidden(name), name


def test_resolve_path_allows_inside(ws_dir):
    workspace = Workspace(ws_dir)
    resolved = workspace.resolve_path("sub/c.xlsx")
    assert resolved == (ws_dir / "sub" / "c.xlsx").resolve()
    resolved = workspace.resolve_path(ws_dir / "a.docx")
    assert resolved.exists()


def test_resolve_path_blocks_escape(ws_dir):
    workspace = Workspace(ws_dir)
    with pytest.raises(WorkspaceBoundaryError):
        workspace.resolve_path("../outside.docx")
    with pytest.raises(WorkspaceBoundaryError):
        workspace.resolve_path(ws_dir.parent / "outside.docx")
    with pytest.raises(WorkspaceBoundaryError):
        workspace.resolve_path("sub/../../outside.docx")


def test_workspace_root_validation(tmp_path):
    with pytest.raises(FileNotFoundError):
        Workspace(tmp_path / "nope")
    file_root = tmp_path / "file.docx"
    file_root.write_bytes(b"x")
    with pytest.raises(NotADirectoryError):
        Workspace(file_root)
