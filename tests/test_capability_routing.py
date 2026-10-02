"""T4/T8 + AC-01/AC-02/AC-06/AC-10 — 路由与权限集成测试。"""
import json
from pathlib import Path

import pytest

from plugin_runtime import assemble_runtime, get_default_runtime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = PROJECT_ROOT / "evals" / "fixtures"


def test_ac02_builtin_plugins_auto_registered():
    """AC-02：启动 Runtime 后可列出内置插件及其 Capability。"""
    assembly = get_default_runtime()
    plugin_ids = {
        item.discovered.manifest.id for item in assembly.load_report.loaded
    }
    assert {
        "hmbuddy.docx.core",
        "hmbuddy.pdf.core",
        "hmbuddy.xlsx.core",
        "hmbuddy.pptx.core",
        "hmbuddy.xls.core",
        "hmbuddy.doc.core",
        "hmbuddy.text.core",
    } <= plugin_ids
    assert assembly.registry.list_capabilities() == ["artifact.read.full"]


def test_ac01_core_does_not_reference_adapters():
    """AC-01：核心 Router/Reader 不得出现具体 Adapter 静态列表。"""
    for relative in ("services/artifact_reader.py", "plugin_runtime/router.py",
                     "plugin_runtime/registry.py", "plugin_runtime/runtime.py"):
        source = (PROJECT_ROOT / relative).read_text(encoding="utf-8")
        for name in (
            "DocxAdapter",
            "PdfAdapter",
            "XlsxAdapter",
            "PptxAdapter",
            "TextAdapter",
            "XlsAdapter",
            "DocLegacyAdapter",
            "default_adapters",
        ):
            assert name not in source, f"{relative} 引用了 {name}"


def test_t4_routing_to_correct_plugin():
    """T4：四种核心格式路由到正确的内置 Provider（经 provenance 验证）。"""
    from services.artifact_reader import ArtifactReader

    reader = ArtifactReader()
    expectations = {
        "sample.docx": "hmbuddy.docx.core",
        "sample.pdf": "hmbuddy.pdf.core",
        "sample.xlsx": "hmbuddy.xlsx.core",
        "sample.pptx": "hmbuddy.pptx.core",
        "sample.xls": "hmbuddy.xls.core",
    }
    for filename, expected_plugin in expectations.items():
        artifact = reader.read_artifact(FIXTURES_DIR / filename)
        assert artifact.provenance["plugin_id"] == expected_plugin, filename
        assert artifact.provenance["plugin_version"] == "0.1.0"
        assert artifact.provenance["provider_id"]
        assert artifact.provenance["capability_trace"].get("request_id")


def test_t8_permission_observable():
    """T8/AC-07：插件声明权限可观察，未授权能力不静默执行。"""
    assembly = get_default_runtime()
    doc_providers = assembly.registry.providers_for_plugin("hmbuddy.doc.core")
    assert doc_providers, "doc legacy provider 应已注册"
    declared = set(doc_providers[0].declared_permissions)
    assert {"office.com", "wps.com"} <= declared
    # 默认 Policy 不授予 COM / 网络权限
    policy = assembly.runtime.policy
    assert not policy.grants("office.com")
    assert not policy.grants("network")
    assert policy.grants("filesystem.read")


def test_t8_write_permission_request_rejected():
    from plugin_runtime.errors import PluginPermissionError
    from plugin_runtime.policy import PermissionPolicy

    policy = PermissionPolicy()  # 只授予 filesystem.read
    with pytest.raises(PluginPermissionError, match="not granted by policy"):
        policy.require("some.plugin", "filesystem.write", ["filesystem.write"])


def test_t8_undeclared_permission_rejected():
    from plugin_runtime.errors import PluginPermissionError
    from plugin_runtime.policy import PermissionPolicy

    policy = PermissionPolicy(granted=frozenset({"filesystem.read", "network"}))
    # 未声明 network 却想用 → 拒绝
    with pytest.raises(PluginPermissionError, match="declared but not granted|missing"):
        policy.require("some.plugin", "network", ["filesystem.read"])


def test_t7_execute_failure_isolated(tmp_path, monkeypatch):
    """AC-06/T7：故障插件不影响其他插件与正常读取。"""
    broken_dir = tmp_path / "broken"
    broken_dir.mkdir()
    (broken_dir / "plugin.json").write_text(
        json.dumps(
            {
                "id": "test.broken.reader",
                "name": "Broken",
                "version": "0.1.0",
                "api_version": 1,
                "entrypoint": {"module": "plugin", "class": "BrokenPlugin"},
                "accepts": {"extensions": [".broken"]},
                "capabilities": [{"id": "artifact.read.full"}],
                "permissions": ["filesystem.read"],
            }
        ),
        encoding="utf-8",
    )
    (broken_dir / "plugin.py").write_text(
        "raise RuntimeError('constructor explosion')", encoding="utf-8"
    )

    assembly = assemble_runtime(external_plugin_dirs=[tmp_path], use_env_plugin_path=False)
    assert any(name == "test.broken.reader" for name, _ in assembly.load_report.failures)
    # 内置插件仍然全部就位
    assert "hmbuddy.docx.core" in {
        item.discovered.manifest.id for item in assembly.load_report.loaded
    }

    # 正常读取不受影响
    from services.artifact_reader import ArtifactReader

    reader = ArtifactReader()
    artifact = reader.read_artifact(PROJECT_ROOT / "evals/fixtures/sample.docx")
    assert artifact.provenance["plugin_id"] == "hmbuddy.docx.core"
