"""遗留格式 Eval（fce 能力融入）：.xls 经 xlrd 读取；.doc 在无 Word/WPS 时明确报错。"""
import sys

import pytest

from services.artifact_reader import read_artifact
from workspace.errors import ArtifactParseError

xlrd = pytest.importorskip("xlrd", reason="未安装 xlrd，跳过 .xls Eval")


def test_xls_sheet_and_values(xls_standard):
    assert xls_standard.artifact_type == "xls"
    assert xls_standard.metadata["sheet_count"] == 1
    assert xls_standard.metadata["sheets"][0]["name"] == "部门费用"


def test_xls_grid_content(xls_standard):
    table = xls_standard.blocks_of_type("table")[0]
    assert table.location["sheet"] == "部门费用"
    assert table.metadata["cells"][0] == ["项目", "2024", "2025"]
    assert table.metadata["cells"][1] == ["营业收入", "1200", "1500"]
    assert table.metadata["cells"][2] == ["营业成本", "800", "900"]


def test_xls_merged_cells(xls_standard):
    table = xls_standard.blocks_of_type("table")[0]
    assert "A5:C5" in table.metadata.get("merged_cells", [])


def test_xls_extraction_method_recorded(xls_standard):
    table = xls_standard.blocks_of_type("table")[0]
    assert table.metadata.get("extraction_method") in {"xlrd", "Excel.Application",
                                                      "Ket.Application", "ET.Application"}


def test_xls_com_fallback_requires_dynamic_permission(tmp_path, monkeypatch):
    """BUG-001/4.3：XLS 的 xlrd 路径只需 filesystem.read；
    但准备 COM fallback 前必须动态申请 office.com。"""
    import sys
    import types

    from plugin_runtime.errors import PluginPermissionError
    from services.artifact_reader import ArtifactReader

    calls = {"dispatch": 0}
    fake_client = types.ModuleType("win32com.client")

    def dispatch_ex(prog_id):
        calls["dispatch"] += 1
        raise AssertionError("DispatchEx must not be called without permission")

    fake_client.DispatchEx = dispatch_ex
    fake_win32com = types.ModuleType("win32com")
    fake_win32com.client = fake_client
    monkeypatch.setitem(sys.modules, "win32com", fake_win32com)
    monkeypatch.setitem(sys.modules, "win32com.client", fake_client)
    monkeypatch.setitem(sys.modules, "xlrd", None)  # 逼走 COM 路径

    target = tmp_path / "legacy.xls"
    target.write_bytes(b"fake xls bytes")
    reader = ArtifactReader()  # 默认 Policy
    with pytest.raises(PluginPermissionError, match="office.com"):
        reader.read_artifact(target)
    assert calls["dispatch"] == 0


def test_corrupt_doc_raises_parse_error(tmp_path):
    """.doc：授权 office.com 后，损坏文件必须落入显式解析错误类型。"""
    from adapters.text import TEXT_ENCODINGS  # noqa: F401  (确保模块可用)
    from plugin_runtime.policy import PermissionPolicy
    from services.artifact_reader import ArtifactReader

    target = tmp_path / "broken.doc"
    target.write_bytes(b"this is not a real OLE document")
    reader = ArtifactReader(
        policy=PermissionPolicy(
            granted=frozenset({"filesystem.read", "office.com", "wps.com"})
        )
    )
    with pytest.raises(ArtifactParseError):
        reader.read_artifact(target)


@pytest.mark.windows_only
@pytest.mark.skipif(sys.platform != 'win32', reason='.doc COM 为 Windows-only 能力（INT-008）')
def test_doc_com_blocked_without_permission(tmp_path, monkeypatch):
    """BUG-001 / AC-H01 / T1：默认 Policy 下 .doc 不得实际启动 Word/WPS。

    注入假的 win32com.client 模块记录 DispatchEx 调用；权限校验必须发生在
    任何 COM 调用之前（即使 xlrd 缺失也一样）。
    """
    import sys
    import types

    from plugin_runtime.errors import PluginPermissionError
    from services.artifact_reader import ArtifactReader

    calls = {"dispatch": 0}

    fake_client = types.ModuleType("win32com.client")

    def dispatch_ex(prog_id):
        calls["dispatch"] += 1
        raise AssertionError("DispatchEx must not be called without permission")

    fake_client.DispatchEx = dispatch_ex
    fake_win32com = types.ModuleType("win32com")
    fake_win32com.client = fake_client
    monkeypatch.setitem(sys.modules, "win32com", fake_win32com)
    monkeypatch.setitem(sys.modules, "win32com.client", fake_client)
    # 同时屏蔽 xlrd，逼走 COM 路径
    monkeypatch.setitem(sys.modules, "xlrd", None)

    target = tmp_path / "anything.doc"
    target.write_bytes(b"whatever content")
    reader = ArtifactReader()  # 默认 Policy：仅 filesystem.read
    with pytest.raises(PluginPermissionError, match="office.com"):
        reader.read_artifact(target)
    assert calls["dispatch"] == 0
