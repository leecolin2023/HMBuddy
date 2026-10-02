"""遗留格式 Eval（fce 能力融入）：.xls 经 xlrd 读取；.doc 在无 Word/WPS 时明确报错。"""
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


def test_corrupt_doc_raises_parse_error(tmp_path):
    """.doc：无论平台是否装有 Word/WPS，损坏文件都必须落入显式错误类型。"""
    target = tmp_path / "broken.doc"
    target.write_bytes(b"this is not a real OLE document")
    with pytest.raises(ArtifactParseError):
        read_artifact(target)
