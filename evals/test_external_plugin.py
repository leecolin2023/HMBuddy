"""T6/AC-04 — 外部插件验收：不修改 Core 与既有插件的前提下新增 Markdown 能力。

将仓库自带的 plugins/examples/markdown_reader 加入 HMBUDDY_PLUGIN_PATH，
Runtime 自动发现并按 priority=100 覆盖内置文本插件（priority=50）。
"""
import json
from pathlib import Path

import pytest

import plugin_runtime
from plugin_runtime import assemble_runtime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
# HMBUDDY_PLUGIN_PATH 指向"插件容器目录"（其子目录各是一个插件）
EXAMPLE_CONTAINER = PROJECT_ROOT / "plugins" / "examples"
EXAMPLE_DIR = EXAMPLE_CONTAINER / "markdown_reader"


@pytest.fixture()
def external_runtime():
    """隔离装配：内置插件 + examples 外部插件，不污染全局默认 Runtime。"""
    assembly = assemble_runtime(
        external_plugin_dirs=[EXAMPLE_CONTAINER],
        use_env_plugin_path=False,
    )
    assert any(
        item.discovered.manifest.id == "example.markdown.reader"
        for item in assembly.load_report.loaded
    ), f"example plugin 加载失败: {assembly.load_report.failures}"
    return assembly


def test_example_plugin_discovered_as_external():
    from plugin_runtime.discovery import discover_external

    report = discover_external([EXAMPLE_CONTAINER])
    assert [item.manifest.id for item in report.externals] == ["example.markdown.reader"]
    assert report.externals[0].manifest.extensions == [".md"]
    assert not report.errors


def test_external_plugin_serves_read_full(tmp_path, external_runtime):
    target = tmp_path / "notes.md"
    target.write_text("# 外部插件标题\n\n来自外部插件的内容\n", encoding="utf-8")

    from services.artifact_reader import ArtifactReader

    reader = ArtifactReader()
    # 把默认 Runtime 替换为带外部插件的装配（仅本测试）
    original = reader.runtime
    reader.runtime = external_runtime.runtime
    try:
        artifact = reader.read_artifact(target)
    finally:
        reader.runtime = original

    assert artifact.artifact_type == "md"
    assert artifact.metadata["origin"] == "external-plugin"
    assert artifact.provenance["plugin_id"] == "example.markdown.reader"
    assert artifact.provenance["provider_id"] == "example.markdown.reader.plain"
    assert artifact.content == "# 外部插件标题\n\n来自外部插件的内容"


def test_external_plugin_priority_overrides_builtin(tmp_path, external_runtime):
    """priority=100 的外部插件在 .md 上压过 priority=50 的内置文本插件。"""
    target = tmp_path / "doc.md"
    target.write_text("内容", encoding="utf-8")
    request_md = external_runtime.registry.list_providers("artifact.read.full")
    supporting = [
        p
        for p in request_md
        if ".md" in getattr(p, "extensions", ())
    ]
    assert supporting[0].plugin_id == "example.markdown.reader"
    assert supporting[0].priority == 100


def test_ac04_env_plugin_path_flow(monkeypatch, tmp_path):
    """AC-04 完整链路：HMBUDDY_PLUGIN_PATH → 默认 Runtime 自动发现 → read_artifact。"""
    from services.artifact_reader import ArtifactReader

    monkeypatch.setenv("HMBUDDY_PLUGIN_PATH", str(EXAMPLE_CONTAINER))
    assembly = assemble_runtime()  # use_env_plugin_path 默认 True
    assert any(
        item.discovered.manifest.id == "example.markdown.reader"
        for item in assembly.load_report.loaded
    )

    target = tmp_path / "README.md"
    target.write_text("# Hello\n", encoding="utf-8")
    reader = ArtifactReader()
    original = reader.runtime
    reader.runtime = assembly.runtime
    try:
        artifact = reader.read_artifact(target)
    finally:
        reader.runtime = original
    assert artifact.provenance["plugin_id"] == "example.markdown.reader"


def test_workspace_ref_also_works_with_external_plugin(tmp_path, external_runtime):
    """G5 链路：Workspace 发现 .md → ArtifactRef → read_artifact → Artifact。"""
    from workspace.workspace import Workspace

    ws_root = tmp_path / "ws"
    ws_root.mkdir()
    (ws_root / "doc.md").write_text("# 文档\n", encoding="utf-8")
    workspace = Workspace(ws_root)
    ref = next(r for r in workspace.list_artifacts() if r.name == "doc.md")

    from services.artifact_reader import ArtifactReader

    reader = ArtifactReader(workspace=workspace)
    original = reader.runtime
    reader.runtime = external_runtime.runtime
    try:
        artifact = reader.read_artifact(ref)
    finally:
        reader.runtime = original
    assert artifact.artifact_id == ref.artifact_id
    assert artifact.blocks
