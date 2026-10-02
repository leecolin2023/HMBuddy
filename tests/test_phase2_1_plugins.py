"""Phase 2.1 T5/T6 — Plugin Product View 与 Plugin Config。"""
import json
from pathlib import Path

import pytest

from application.config import AppConfig, resolve_effective_config
from application.plugins import (
    STATUS_DISABLED,
    STATUS_INCOMPATIBLE,
    STATUS_LOAD_FAILED,
    assemble_app_runtime,
    build_plugin_views,
    build_system_status,
)
from plugin_runtime.errors import CapabilityDisabledError
from plugin_runtime.policy import PermissionPolicy
from services.artifact_reader import ArtifactReader

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = PROJECT_ROOT / "evals" / "fixtures"


def _effective(tmp_path, *, disabled=None, external_dirs=None, env=None):
    config = AppConfig()
    if disabled:
        config.plugins.disabled_plugin_ids = list(disabled)
    if external_dirs:
        config.paths.external_plugin_dirs = [str(item) for item in external_dirs]
    effective = resolve_effective_config(config, env=env)
    return effective


def _write_foo_plugin(root: Path, *, plugin_id="test.foo.reader", api_version=1):
    plugin_dir = root / "foo_plugin"
    plugin_dir.mkdir(parents=True, exist_ok=True)
    (plugin_dir / "plugin.json").write_text(
        json.dumps(
            {
                "id": plugin_id,
                "name": "Foo Reader",
                "version": "0.1.0",
                "api_version": api_version,
                "entrypoint": {"module": "plugin", "class": "FooPlugin"},
                "accepts": {"extensions": [".foo"]},
                "capabilities": [{"id": "artifact.read.full", "priority": 100}],
                "permissions": ["filesystem.read"],
            }
        ),
        encoding="utf-8",
    )
    (plugin_dir / "plugin.py").write_text(
        "from pathlib import Path\n"
        "from plugin_runtime.base_provider import CapabilityProviderBase\n"
        "from plugin_runtime.contracts import CapabilityResult\n"
        "from workspace.artifact import Artifact, ArtifactBlock\n\n"
        "class FooReadProvider(CapabilityProviderBase):\n"
        '    provider_id = "test.foo.main"\n'
        '    extensions = (".foo",)\n'
        "    def create_adapter(self, context):\n"
        "        return None\n"
        "    def execute(self, request, context):\n"
        "        text = Path(context.resolved_path).read_text(encoding='utf-8')\n"
        "        artifact = Artifact(\n"
        "            artifact_id=str(request.options.get('artifact_id') or ''),\n"
        "            name=Path(context.resolved_path).name,\n"
        "            path=str(context.resolved_path), artifact_type='foo',\n"
        "            metadata={}, content=text,\n"
        "            blocks=[ArtifactBlock('', 'paragraph', text, {}, {})],\n"
        "            provenance={})\n"
        "        return CapabilityResult(True, artifact, self.provider_id, self.plugin_id)\n\n"
        "class FooPlugin:\n"
        "    def providers(self):\n"
        "        return [FooReadProvider(plugin_id='" + plugin_id + "')]\n",
        encoding="utf-8",
    )
    return root


def test_t5_builtin_plugin_views_complete():
    """T5 / AC-14 / AC-17：内置插件视图包含规格第 23 节全部字段。"""
    runtime = assemble_app_runtime(_effective(tmp_path := Path(__file__).parent / "_tmp_t5"))
    views = build_plugin_views(runtime.assembly)
    by_id = {view.plugin_id: view for view in views}
    docx = by_id["hmbuddy.docx.core"]
    assert docx.status == "Enabled"
    assert docx.extensions == [".docx"]
    assert docx.capabilities == ["artifact.read.full"]
    assert docx.declared_permissions == ["filesystem.read"]
    assert docx.effective_permissions == ["filesystem.read"]
    assert docx.is_builtin is True
    assert docx.version == "0.1.0"
    assert docx.api_version == 1


def test_t5_declared_vs_effective_permissions(tmp_path):
    """AC-17：声明与生效权限分列（doc 声明 COM，默认 Policy 不授予）。"""
    runtime = assemble_app_runtime(_effective(tmp_path / "t5b"))
    views = build_plugin_views(runtime.assembly)
    doc = next(v for v in views if v.plugin_id == "hmbuddy.doc.core")
    assert "office.com" in doc.declared_permissions
    assert "office.com" not in doc.effective_permissions
    assert "filesystem.read" in doc.effective_permissions


def test_t6_disable_via_config_not_manifest(tmp_path):
    """T6 / AC-15：disable 记录在 AppConfig，不修改 plugin.json。"""
    plugin_root = _write_foo_plugin(tmp_path / "ext")
    manifest_path = plugin_root / "foo_plugin" / "plugin.json"
    manifest_before = manifest_path.read_text(encoding="utf-8")

    effective = _effective(tmp_path / "c1", external_dirs=[plugin_root])
    runtime = assemble_app_runtime(effective)
    assert any(v.plugin_id == "test.foo.reader" for v in build_plugin_views(runtime.assembly))

    disabled_config = AppConfig()
    disabled_config.paths.external_plugin_dirs = [str(plugin_root)]
    disabled_config.plugins.disabled_plugin_ids = ["test.foo.reader"]
    effective_disabled = resolve_effective_config(disabled_config)
    runtime_disabled = assemble_app_runtime(effective_disabled)

    views = build_plugin_views(runtime_disabled.assembly)
    foo_view = next(v for v in views if v.plugin_id == "test.foo.reader")
    assert foo_view.status == STATUS_DISABLED
    # 仍可 Discovery / 展示 Manifest
    assert foo_view.extensions == [".foo"]
    # 不进 Effective Registry
    assert runtime_disabled.assembly.registry.providers_for_plugin("test.foo.reader") == []
    # Manifest 文件未被修改
    assert manifest_path.read_text(encoding="utf-8") == manifest_before


def test_t6_disabled_provider_clear_error(tmp_path):
    """ER-06：唯一 Provider 被禁用时明确提示"所需文件能力当前已禁用"。"""
    plugin_root = _write_foo_plugin(tmp_path / "ext")
    target = plugin_root / "sample.foo"
    target.write_text("foo 内容", encoding="utf-8")

    disabled_config = AppConfig()
    disabled_config.paths.external_plugin_dirs = [str(plugin_root)]
    disabled_config.plugins.disabled_plugin_ids = ["test.foo.reader"]
    effective = resolve_effective_config(disabled_config)
    runtime = assemble_app_runtime(effective)
    reader = ArtifactReader(assembly=runtime.assembly)

    with pytest.raises(CapabilityDisabledError, match="所需文件能力当前已禁用"):
        reader.read_artifact(target)


def test_t5_load_failed_and_incompatible_views(tmp_path):
    """T5：加载失败 / api_version 不兼容分别呈现为 Load Failed / Incompatible。"""
    ext_root = tmp_path / "ext"
    ext_root.mkdir()
    broken = ext_root / "broken_plugin"
    broken.mkdir()
    (broken / "plugin.json").write_text(
        json.dumps(
            {
                "id": "test.broken.reader", "name": "Broken", "version": "0.1.0",
                "api_version": 1,
                "entrypoint": {"module": "plugin", "class": "Nope"},
                "accepts": {"extensions": [".brk"]},
                "capabilities": [{"id": "artifact.read.full"}],
            }
        ),
        encoding="utf-8",
    )
    (broken / "plugin.py").write_text("raise RuntimeError('boom')", encoding="utf-8")

    incompatible = ext_root / "old_plugin"
    incompatible.mkdir()
    (incompatible / "plugin.json").write_text(
        json.dumps(
            {
                "id": "test.old.reader", "name": "Old", "version": "0.1.0",
                "api_version": 99,
                "entrypoint": {"module": "plugin", "class": "P"},
                "accepts": {"extensions": [".old"]},
                "capabilities": [{"id": "artifact.read.full"}],
            }
        ),
        encoding="utf-8",
    )

    effective = _effective(tmp_path / "cfg", external_dirs=[ext_root])
    runtime = assemble_app_runtime(effective)
    views = {v.plugin_id: v for v in build_plugin_views(runtime.assembly)}
    assert views["test.broken.reader"].status == STATUS_LOAD_FAILED
    assert "boom" in views["test.broken.reader"].load_error
    assert views["test.old.reader"].status == STATUS_INCOMPATIBLE


def test_t5_unavailable_view_reason(tmp_path, monkeypatch):
    """T5 / AC-H08 联动：平台不满足的插件在视图里呈现不可用原因。"""
    ext_root = _write_foo_plugin(tmp_path / "ext")
    manifest_path = ext_root / "foo_plugin" / "plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["platforms"] = ["linux"]
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")

    effective = _effective(tmp_path / "cfg", external_dirs=[ext_root])
    runtime = assemble_app_runtime(effective)
    views = {v.plugin_id: v for v in build_plugin_views(runtime.assembly)}
    foo = views["test.foo.reader"]
    if sys.platform.startswith("win"):
        assert foo.status == "Enabled"
        assert "platform" in foo.availability_reason
    else:
        assert foo.availability_reason is None or "platform" not in foo.availability_reason


import sys  # noqa: E402


def test_t6_rescan_applies_config_changes(tmp_path):
    """T6 / 规格 28：Rescan 后新目录中的插件出现。"""
    from application.config import ConfigSource

    effective = _effective(tmp_path / "c0")
    runtime = assemble_app_runtime(effective)
    assert all(v.plugin_id != "test.foo.reader" for v in build_plugin_views(runtime.assembly))

    ext_root = _write_foo_plugin(tmp_path / "ext")
    effective.external_plugin_dirs.append((str(ext_root), ConfigSource.USER))
    refreshed = runtime.rescan()
    assert any(
        v.plugin_id == "test.foo.reader" for v in build_plugin_views(refreshed.assembly)
    )


def test_t8_system_status_fields(tmp_path):
    from application.state import record_workspace_open

    effective = _effective(tmp_path / "cfg")
    runtime = assemble_app_runtime(effective)
    state = None
    from application.state import AppState

    state = AppState()
    record_workspace_open(state, str(FIXTURES_DIR), limit=10)
    status = build_system_status(runtime, str(FIXTURES_DIR))
    assert status.llm == "Not Configured"  # 未配置 LLM
    assert status.plugins_loaded >= 7
    assert status.plugins_error == 0
    assert status.model_dir == "Not Required"
    assert status.last_workspace == "Available"

    missing = build_system_status(runtime, "D:/definitely/missing/ws")
    assert missing.last_workspace == "Missing"
