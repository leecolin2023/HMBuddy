"""Phase 2.1 T8 Desktop Smoke（无头）+ T9 架构守护。

T8 十条 smoke 以 AppController（Composition Root 的无头核心）验证；
Tk 壳只做薄视图。T9 确认没有提前长出 Agent Kernel。
"""
import json
from pathlib import Path

import pytest

from application.config import AppConfig, resolve_effective_config
from application.plugins import assemble_app_runtime
from desktop.controller import AppController, bootstrap_controller

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = PROJECT_ROOT / "evals" / "fixtures"


@pytest.fixture()
def app_env(tmp_path):
    """隔离的 per-user 数据目录 + 干净环境。"""
    data_dir = tmp_path / "appdata"
    data_dir.mkdir()
    return {"data_dir": data_dir, "config": data_dir / "config.json", "state": data_dir / "state.json"}


def _controller(app_env):
    return bootstrap_controller(
        config_path=app_env["config"], state_path=app_env["state"], env={}
    )


def test_t8_smoke_01_launch_enters_home(app_env):
    """1. 启动进入 Home。"""
    controller = _controller(app_env)
    assert controller.current_page == "home"


def test_t8_smoke_02_04_recent_workspace_persist_across_restart(app_env):
    """2/3/4. 打开 Workspace → 进入 Recent → 重启后仍在。"""
    controller = _controller(app_env)
    snapshot = controller.open_workspace(FIXTURES_DIR)
    assert snapshot.refs, "fixtures 目录应有可发现文件"
    assert controller.current_page == "workspace"
    assert app_env["state"].is_file()

    # 重启（重新 bootstrap，同一路径）
    restarted = _controller(app_env)
    recent = restarted.recent_workspaces()
    assert recent and Path(recent[0].path).resolve() == FIXTURES_DIR.resolve()


def test_t8_smoke_05_missing_workspace_displayed(app_env):
    """5. Missing Workspace 正确展示（状态可判定，且可移除）。"""
    controller = _controller(app_env)
    record_missing(app_env, "D:/no/such/workspace")
    controller = _controller(app_env)
    entry = controller.recent_workspaces()[0]
    assert not Path(entry.path).is_dir()  # UI 据此显示 [Missing]
    controller.remove_recent_workspace(entry.path)
    assert controller.recent_workspaces() == []


def record_missing(app_env, path):
    controller = _controller(app_env)
    from application.state import record_workspace_open

    record_workspace_open(controller.state, path, limit=10)
    controller.persist_state()


def test_t8_smoke_06_settings_modify_model_config(app_env):
    """6. Settings 修改模型配置 → 保存 → Effective 更新 → LLM Client 重建。"""
    controller = _controller(app_env)
    assert controller.app_runtime.llm_status == "Not Configured"

    config = AppConfig()
    config.llm.base_url = "https://llm.intra/v1"
    config.llm.model = "test-model"
    controller.save_settings(config)

    assert controller.effective_config.llm_model.value == "test-model"
    assert controller.app_runtime.llm_client is not None
    assert controller.app_runtime.llm_status == "Ready"
    assert app_env["config"].is_file()
    saved = json.loads(app_env["config"].read_text(encoding="utf-8"))
    assert saved["llm"]["model"] == "test-model"


def test_t8_smoke_07_plugin_manager_lists_builtins(app_env):
    """7. Plugin Manager 查看现有插件。"""
    controller = _controller(app_env)
    views = controller.plugin_views()
    ids = {view.plugin_id for view in views}
    assert {
        "hmbuddy.docx.core", "hmbuddy.pdf.core", "hmbuddy.xlsx.core",
        "hmbuddy.pptx.core", "hmbuddy.xls.core", "hmbuddy.doc.core",
        "hmbuddy.text.core",
    } <= ids
    assert all(view.load_error == "" for view in views if view.status == "Enabled")


def test_t8_smoke_08_disabled_external_plugin(app_env, tmp_path):
    """8. Disabled External Plugin：禁用后读取给出明确"已禁用"提示。"""
    ext_root = tmp_path / "ext"
    ext_root.mkdir()
    plugin_dir = ext_root / "foo_plugin"
    plugin_dir.mkdir()
    (plugin_dir / "plugin.json").write_text(
        json.dumps(
            {
                "id": "test.foo.reader", "name": "Foo", "version": "0.1.0",
                "api_version": 1,
                "entrypoint": {"module": "plugin", "class": "FooPlugin"},
                "accepts": {"extensions": [".foo"]},
                "capabilities": [{"id": "artifact.read.full"}],
                "permissions": ["filesystem.read"],
            }
        ),
        encoding="utf-8",
    )
    (plugin_dir / "plugin.py").write_text(
        "from pathlib import Path\n"
        "from plugin_runtime.base_provider import CapabilityProviderBase\n"
        "from plugin_runtime.contracts import CapabilityResult\n"
        "from workspace.artifact import Artifact, ArtifactBlock\n"
        "class FooReadProvider(CapabilityProviderBase):\n"
        '    provider_id = "test.foo.main"\n'
        '    extensions = (".foo",)\n'
        "    def create_adapter(self, context):\n"
        "        return None\n"
        "    def execute(self, request, context):\n"
        "        text = Path(context.resolved_path).read_text(encoding='utf-8')\n"
        "        artifact = Artifact(artifact_id='', name='x.foo',"
        " path=str(context.resolved_path), artifact_type='foo', metadata={},"
        " content=text, blocks=[], provenance={})\n"
        "        return CapabilityResult(True, artifact, self.provider_id, self.plugin_id)\n"
        "class FooPlugin:\n"
        "    def providers(self):\n"
        "        return [FooReadProvider(plugin_id='test.foo.reader')]\n",
        encoding="utf-8",
    )

    config = AppConfig()
    config.paths.external_plugin_dirs = [str(ext_root)]
    controller = AppController(
        config=config,
        config_path=app_env["config"],
        state_path=app_env["state"],
    )
    assert any(v.plugin_id == "test.foo.reader" for v in controller.plugin_views())

    # 用户禁用该插件 → 重启（bootstrap 从 config.json 加载禁用名单）
    config.plugins.disabled_plugin_ids = ["test.foo.reader"]
    controller.save_settings(config)
    restarted = bootstrap_controller(
        config_path=app_env["config"], state_path=app_env["state"], env={}
    )
    views = {v.plugin_id: v for v in restarted.plugin_views()}
    assert views["test.foo.reader"].status == "Disabled"

    # ER-06：读取被禁用扩展名 → 明确提示而非 Unsupported
    from plugin_runtime.errors import CapabilityDisabledError

    target = ext_root / "sample.foo"
    target.write_text("foo", encoding="utf-8")
    restarted.open_workspace(ext_root)
    with pytest.raises(CapabilityDisabledError, match="已禁用"):
        restarted.reader.read_artifact(target, workspace=restarted.workspace)


def test_t8_smoke_09_rescan_correct_after_change(app_env, tmp_path):
    """9. Rescan 后状态正确。"""
    controller = _controller(app_env)
    before = len(controller.plugin_views())
    controller.rescan_plugins()
    after = controller.plugin_views()
    assert len(after) == before  # 无配置变化时稳定
    assert all(view.status in {"Enabled", "Unavailable"} for view in after
               if view.status != "Disabled")


def test_t8_smoke_10_llm_not_configured_still_reads(app_env):
    """10. LLM 未配置仍可读取文件（ER-07 / AC-18）。"""
    controller = _controller(app_env)
    assert controller.app_runtime.llm_client is None
    controller.open_workspace(FIXTURES_DIR)
    ref = next(r for r in controller.refs if r.name == "sample.docx")
    artifact = controller.open_artifact(ref)
    assert artifact.blocks
    assert controller.app_runtime.llm_status == "Not Configured"


def test_t8_recent_activity_records_navigation(app_env):
    """AC-11：打开工作区/文件/问答后，Recent Activity 可恢复上下文。"""
    controller = _controller(app_env)
    controller.open_workspace(FIXTURES_DIR)
    ref = next(r for r in controller.refs if r.name == "sample.docx")
    controller.open_artifact(ref)
    controller.record_qa()

    entries = controller.recent_activity()
    assert entries[0].activity_type == "artifact_qa"
    assert entries[1].activity_type == "artifact"
    # 重启后仍可恢复
    restarted = _controller(app_env)
    assert restarted.recent_activity()[0].activity_type == "artifact_qa"
    assert restarted.recent_activity()[0].resume_view.get("artifact") == ref.path


def test_t9_no_agent_kernel_in_product_layer():
    """T9 / AC-21：产品层不得长出 Session / TaskEngine / AgentLoop 等。"""
    forbidden_definitions = (
        "TaskEngine", "AgentLoop", "ToolRegistry", "ExtensionHost",
        "Planner", "WorkflowGraph", "RecentTaskEntry", "TaskGraph",
    )
    scanned = list((PROJECT_ROOT / "application").rglob("*.py")) + list(
        (PROJECT_ROOT / "desktop").rglob("*.py")
    )
    assert scanned, "应扫描到 application/ 与 desktop/ 源码"
    for source_file in scanned:
        source = source_file.read_text(encoding="utf-8")
        for name in forbidden_definitions:
            assert f"class {name}" not in source, f"{source_file} 定义了 {name}"
            assert f"def {name}" not in source
            assert f"import {name}" not in source
            # 允许注释/文档字符串中说明"不实现 Session"等，但禁止作为类型使用
            assert f": {name}" not in source, f"{source_file} 将 {name} 用作类型"
