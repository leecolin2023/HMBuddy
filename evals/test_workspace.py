"""Workspace 发现 Eval（规格 G1 / 22-A：文件发现成功率 100%）。"""
from evals.conftest import EXPECTED_FIXTURES
from workspace.workspace import Workspace


def test_all_required_fixtures_exist(fixtures_dir):
    present = {p.name for p in fixtures_dir.iterdir()}
    assert EXPECTED_FIXTURES <= present


def test_discovery_success_rate_is_100_percent(fixtures_dir):
    """8 个支持格式的样例必须全部被发现，且不发现任何不支持文件。"""
    workspace = Workspace(fixtures_dir)
    refs = workspace.list_artifacts()
    found = {ref.name for ref in refs}
    assert EXPECTED_FIXTURES <= found
    assert all(
        ref.artifact_type in {"docx", "pdf", "xlsx", "xls", "pptx"} for ref in refs
    )
    # 生成脚本与 __pycache__ 等不得混入
    assert all(not ref.name.endswith(".py") for ref in refs)
    assert found == EXPECTED_FIXTURES


def test_refs_metadata_complete(fixtures_dir):
    for ref in Workspace(fixtures_dir).list_artifacts():
        assert ref.size > 0
        assert ref.modified_at.tzinfo is not None
        assert "." + ref.extension == ref.name[ref.name.rfind("."):]
        assert ref.path.startswith(str(fixtures_dir))
