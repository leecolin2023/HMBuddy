"""Phase 2.1.1 — Desktop & Runtime Integration Hardening 验收测试（T1-T12 / AC-I01~I15）。

覆盖规格第 18 节测试策略；Tk Widget 级测试在无显示环境下自动跳过。
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

from application.config import AppConfig, ConfigSource, resolve_effective_config
from application.plugins import assemble_app_runtime, build_plugin_views
from application.state import load_state, record_workspace_open, save_state
from desktop.controller import AppController, bootstrap_controller
from plugin_runtime.errors import CapabilityDisabledError
from workspace.artifact import make_workspace_id
from workspace.workspace import Workspace

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = PROJECT_ROOT / "evals" / "fixtures"

FOO_PLUGIN_PY = (
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
    "        return [FooReadProvider(plugin_id='test.foo.reader')]\n"
)


def _write_foo_plugin(root: Path, *, plugin_id="test.foo.reader", platforms=None):
    plugin_dir = root / "foo_plugin"
    plugin_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "id": plugin_id,
        "name": "Foo Reader",
        "version": "0.1.0",
        "api_version": 1,
        "entrypoint": {"module": "plugin", "class": "FooPlugin"},
        "accepts": {"extensions": [".foo"]},
        "capabilities": [{"id": "artifact.read.full", "priority": 100}],
        "permissions": ["filesystem.read"],
    }
    if platforms is not None:
        manifest["platforms"] = platforms
    (plugin_dir / "plugin.json").write_text(
        json.dumps(manifest, ensure_ascii=False), encoding="utf-8"
    )
    (plugin_dir / "plugin.py").write_text(FOO_PLUGIN_PY, encoding="utf-8")
    return root


def _foo_controller(tmp_path, *, disabled=False):
    config = AppConfig()
    config.paths.external_plugin_dirs = [str(tmp_path / "ext")]
    if disabled:
        config.plugins.disabled_plugin_ids = ["test.foo.reader"]
    return AppController(
        config=config,
        config_path=tmp_path / "config.json",
        state_path=tmp_path / "state.json",
    )


# ---------------------------------------------------------------------------
# T1 / AC-I01 / AC-I02 — Catalog 单一真相（enable / disable / rescan）
# ---------------------------------------------------------------------------


def test_t1_enabled_foo_visible_everywhere(tmp_path):
    ext_root = _write_foo_plugin(tmp_path / "ext")
    (ext_root / "sample.foo").write_text("foo 内容", encoding="utf-8")
    controller = _foo_controller(tmp_path)
    controller.open_workspace(ext_root)

    # Plugin Manager
    views = {v.plugin_id: v for v in controller.plugin_views()}
    assert views["test.foo.reader"].status == "Enabled"
    # Workspace Discovery（同一 Catalog）
    assert any(r.extension == "foo" for r in controller.refs)
    # File Picker
    filters = controller.app_runtime.catalog.artifact_extensions()
    assert ".foo" in filters
    # ArtifactReader 可读取
    ref = next(r for r in controller.refs if r.extension == "foo")
    artifact = controller.open_artifact(ref)
    assert artifact.content == "foo 内容"


def test_t1_disabled_foo_disappears_from_workspace(tmp_path):
    ext_root = _write_foo_plugin(tmp_path / "ext")
    (ext_root / "sample.foo").write_text("foo 内容", encoding="utf-8")
    controller = _foo_controller(tmp_path)
    controller.open_workspace(ext_root)
    assert any(r.extension == "foo" for r in controller.refs)

    # 禁用唯一 .foo Provider
    controller.set_plugin_enabled("test.foo.reader", False)
    # Plugin Manager = Disabled
    views = {v.plugin_id: v for v in controller.plugin_views()}
    assert views["test.foo.reader"].status == "Disabled"
    # Workspace = 不再把 .foo 展示为可读 Artifact（AC-I02 Rescan 一致）
    assert all(r.extension != "foo" for r in controller.refs)
    # 用户显式选择文件读取 → CapabilityDisabledError 而非 Unsupported
    target = ext_root / "sample.foo"
    with pytest.raises(CapabilityDisabledError, match="已禁用"):
        controller.reader.read_artifact(target, workspace=controller.workspace)


# ---------------------------------------------------------------------------
# T2 / AC-I03 / AC-I04 — 真实 OpenAICompatibleClient.ask()（fake endpoint）
# ---------------------------------------------------------------------------


def test_t2_real_client_ask_without_attribute_error(tmp_path, monkeypatch):
    """INT-002：真实协议路径不得缺 context_policy；payload 含 system+context+question。"""
    from llm.client import OpenAICompatibleClient
    from workspace.artifact import Artifact, ArtifactBlock

    captured = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps(
                {"choices": [{"message": {"content": "fake 回答"}}]}
            ).encode("utf-8")

    def fake_urlopen(request, timeout=None):
        captured["url"] = request.full_url
        captured["payload"] = json.loads(request.data.decode("utf-8"))
        return FakeResponse()

    import urllib.request

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    client = OpenAICompatibleClient(
        base_url="https://fake.endpoint/v1", api_key="key", model="fake-model"
    )
    huge_blocks = [
        ArtifactBlock("", "paragraph", f"段落 {i} 内容" * 30, {"line_index": i}, {})
        for i in range(1500)
    ]
    artifact = Artifact(
        artifact_id="a_big", name="big.txt", path="big.txt", artifact_type="txt",
        blocks=huge_blocks, content="x" * 100000,
    )
    # 不抛 AttributeError；默认 ContextPolicy 生效（AC-I04）
    answer = client.ask(artifact, "客户A拟申请3亿元授信，风险如何？")
    assert answer == "fake 回答"
    assert client.context_policy is not None
    assert client.last_context_result.truncated is True  # 默认预算生效

    payload = captured["payload"]
    assert payload["model"] == "fake-model"
    roles = [message["role"] for message in payload["messages"]]
    assert roles == ["system", "user"]
    system_text = payload["messages"][0]["content"]
    user_text = payload["messages"][1]["content"]
    assert "文档分析助手" in system_text  # System Prompt
    assert "[Question]" in user_text and "客户A拟申请3亿元授信" in user_text
    assert "[Context Truncated]" in user_text  # 超大 Artifact 有截断
    assert captured["url"].startswith("https://fake.endpoint/v1/chat/completions")


# ---------------------------------------------------------------------------
# T3 / AC-I05 — False / 0 是合法用户配置
# ---------------------------------------------------------------------------


def test_t3_false_and_zero_keep_user_source():
    config = AppConfig()
    config.desktop.restore_last_workspace = False
    config.desktop.recent_workspace_limit = 0
    config.desktop.recent_activity_limit = 0
    effective = resolve_effective_config(config)
    assert effective.restore_last_workspace.value is False
    assert effective.restore_last_workspace.source is ConfigSource.USER
    assert effective.recent_workspace_limit.value == 0
    assert effective.recent_workspace_limit.source is ConfigSource.USER
    assert effective.recent_activity_limit.value == 0
    assert effective.recent_activity_limit.source is ConfigSource.USER


def test_t3_unset_falls_back_to_default():
    effective = resolve_effective_config(AppConfig())
    assert effective.restore_last_workspace.value is True
    assert effective.restore_last_workspace.source is ConfigSource.DEFAULT
    assert effective.recent_workspace_limit.value == 10


# ---------------------------------------------------------------------------
# T4 / AC-I06 — 显式 env 全链路贯穿
# ---------------------------------------------------------------------------


def test_t4_bootstrap_env_propagates(tmp_path, monkeypatch):
    """显式 env 与宿主 os.environ 不一致时，以显式 env 为准。"""
    monkeypatch.delenv("HMBUDDY_LLM_MODEL", raising=False)
    monkeypatch.delenv("HMBUDDY_PLUGIN_PATH", raising=False)
    ext_root = _write_foo_plugin(tmp_path / "ext")

    env = {
        "HMBUDDY_LLM_BASE_URL": "https://from-env/v1",
        "HMBUDDY_LLM_MODEL": "env-model",
        "HMBUDDY_PLUGIN_PATH": str(ext_root),
    }
    controller = bootstrap_controller(
        config_path=tmp_path / "config.json",
        state_path=tmp_path / "state.json",
        env=env,
    )
    effective = controller.effective_config
    assert effective.llm_model.value == "env-model"
    assert effective.llm_model.source is ConfigSource.ENVIRONMENT
    assert any(
        p == str(ext_root) and s is ConfigSource.ENVIRONMENT
        for p, s in effective.external_plugin_dirs
    )
    assert controller.app_runtime.llm_client is not None
    assert controller.app_runtime.llm_client.model_name == "env-model"
    # 外部插件目录来自显式 env（不在宿主 os.environ 中也生效）
    assert any(v.plugin_id == "test.foo.reader" for v in controller.plugin_views())


# ---------------------------------------------------------------------------
# T5 / AC-I07 — Unavailable 真实状态
# ---------------------------------------------------------------------------


def test_t5_unavailable_status_real(tmp_path):
    ext_root = _write_foo_plugin(
        tmp_path / "ext", plugin_id="test.linux.foo", platforms=["linux"]
    )
    config = AppConfig()
    config.paths.external_plugin_dirs = [str(ext_root)]
    controller = AppController(
        config=config,
        config_path=tmp_path / "config.json",
        state_path=tmp_path / "state.json",
    )
    view = {v.plugin_id: v for v in controller.plugin_views()}["test.linux.foo"]
    if sys.platform.startswith("win"):
        assert view.status == "Unavailable"
        assert not view.providers[0].available
        assert "platform" in view.availability_reason
    else:
        assert view.status == "Enabled"


# ---------------------------------------------------------------------------
# T9 / AC-I12 — 动态 Picker（与 T1 联动，这里断言 filter 生成）
# ---------------------------------------------------------------------------


def test_t9_picker_filter_from_catalog(tmp_path):
    _write_foo_plugin(tmp_path / "ext")
    controller = _foo_controller(tmp_path)
    extensions = sorted(controller.app_runtime.catalog.artifact_extensions())
    assert ".foo" in extensions
    # 未安装 .foo 的干净环境不出现在 filter
    plain = AppController(
        config_path=tmp_path / "c2.json", state_path=tmp_path / "s2.json"
    )
    plain_exts = sorted(plain.app_runtime.catalog.artifact_extensions())
    assert ".foo" not in plain_exts


# ---------------------------------------------------------------------------
# T10 / AC-I13 — 多 Provider Plugin 聚合为一行
# ---------------------------------------------------------------------------


def test_t10_multi_provider_plugin_aggregates_to_one_row(tmp_path):
    ext_root = tmp_path / "ext"
    plugin_dir = ext_root / "multi_plugin"
    plugin_dir.mkdir(parents=True, exist_ok=True)
    (plugin_dir / "plugin.json").write_text(
        json.dumps(
            {
                "id": "test.multi.reader",
                "name": "Multi Reader",
                "version": "0.1.0",
                "api_version": 1,
                "entrypoint": {"module": "plugin", "class": "MultiPlugin"},
                "accepts": {"extensions": [".mul"]},
                "capabilities": [{"id": "artifact.read.full", "priority": 100}],
                "permissions": ["filesystem.read"],
            }
        ),
        encoding="utf-8",
    )
    (plugin_dir / "plugin.py").write_text(
        "from plugin_runtime.base_provider import CapabilityProviderBase\n\n"
        "class AProvider(CapabilityProviderBase):\n"
        '    provider_id = "test.multi.a"\n'
        '    extensions = (".mul",)\n'
        "    def create_adapter(self, context):\n"
        "        return None\n\n"
        "class BProvider(CapabilityProviderBase):\n"
        '    provider_id = "test.multi.b"\n'
        '    extensions = (".mul",)\n'
        "    priority = 60\n"
        "    def create_adapter(self, context):\n"
        "        return None\n\n"
        "class MultiPlugin:\n"
        "    def providers(self):\n"
        "        return [AProvider(plugin_id='test.multi.reader'),"
        " BProvider(plugin_id='test.multi.reader')]\n",
        encoding="utf-8",
    )

    config = AppConfig()
    config.paths.external_plugin_dirs = [str(ext_root)]
    controller = AppController(
        config=config,
        config_path=tmp_path / "config.json",
        state_path=tmp_path / "state.json",
    )
    views = [v for v in controller.plugin_views() if v.plugin_id == "test.multi.reader"]
    assert len(views) == 1, "一 Plugin 一行（INT-010）"
    view = views[0]
    assert [p.provider_id for p in view.providers] == [
        "test.multi.a",
        "test.multi.b",
    ], "同 priority 时按 provider_id 稳定排序"
    # Manifest 权威（BUG-003）：同能力声明的 priority 统一注入两个 Provider
    assert view.providers[0].priority == 100
    assert view.providers[1].priority == 100


# ---------------------------------------------------------------------------
# T11 / AC-I14 — QA Activity 不落问题正文
# ---------------------------------------------------------------------------


def test_t11_qa_question_text_not_persisted(tmp_path):
    controller = AppController(
        config_path=tmp_path / "config.json",
        state_path=tmp_path / "state.json",
    )
    controller.open_workspace(FIXTURES_DIR)
    ref = next(r for r in controller.refs if r.name == "sample.docx")
    controller.open_artifact(ref)
    sensitive_question = "客户A拟申请3亿元授信，风险如何？"
    controller.record_qa()

    state_content = (tmp_path / "state.json").read_text(encoding="utf-8")
    assert sensitive_question not in state_content
    assert "3亿" not in state_content
    activity = controller.recent_activity()[0]
    assert activity.activity_type == "artifact_qa"
    assert activity.title.startswith("问答 · ")
    assert sensitive_question not in activity.title


# ---------------------------------------------------------------------------
# T7 / AC-I09 — Workspace Identity 唯一
# ---------------------------------------------------------------------------


def test_t7_workspace_identity_unified_and_stable(tmp_path):
    config_path = tmp_path / "config.json"
    state_path = tmp_path / "state.json"
    controller = bootstrap_controller(
        config_path=config_path, state_path=state_path, env={}
    )
    controller.open_workspace(FIXTURES_DIR)
    core_id = controller.workspace.workspace_id
    recent_entry = controller.recent_workspaces()[0]
    assert recent_entry.workspace_id == core_id  # 与 Core Workspace 一致

    restarted = bootstrap_controller(
        config_path=config_path, state_path=state_path, env={}
    )
    assert restarted.recent_workspaces()[0].workspace_id == core_id  # 跨重启稳定


# ---------------------------------------------------------------------------
# T6 / AC-I08 — Recent Activity Widget 级选择映射（无显示环境自动跳过）
# ---------------------------------------------------------------------------


def test_t6_recent_activity_selection_by_entry_id(tmp_path):
    """T6 / AC-I08：Recent Activity 按稳定 entry_id 选择并恢复（Widget 级）。"""
    pytest.importorskip("PySide6.QtWidgets")
    from PySide6.QtWidgets import QApplication

    from desktop.widgets.sidebar import Sidebar

    qt_app = QApplication.instance() or QApplication([])
    controller = bootstrap_controller(
        config_path=tmp_path / "config.json",
        state_path=tmp_path / "state.json",
        env={},
    )
    controller.open_workspace(FIXTURES_DIR)
    ref = next(r for r in controller.refs if r.name == "sample.docx")
    controller.open_artifact(ref)
    controller.record_qa()

    sidebar = Sidebar(controller)
    qa_entry = controller.recent_activity()[0]

    # 渲染搜索结果并按稳定 entry_id 命中
    sidebar.search_input.setText(qa_entry.title or "问答")
    def _activity_row(index):
        data = sidebar.search_results.item(index).data(0x0100) or {}
        entry = data.get("entry")
        return data.get("kind") == "activity" and entry is not None and entry.entry_id == qa_entry.entry_id

    matches = [
        index for index in range(sidebar.search_results.count()) if _activity_row(index)
    ]
    assert matches, "搜索结果中应包含该 QA activity"
    item = sidebar.search_results.item(matches[0])

    opened = {}
    sidebar.activity_open_requested.connect(
        lambda entry: opened.update(entry_id=entry.entry_id, workspace=entry.workspace_path)
    )
    sidebar._on_search_result_clicked(item)
    assert opened.get("entry_id") == qa_entry.entry_id
    assert Path(opened["workspace"]).resolve() == FIXTURES_DIR.resolve()


class _ShellStub:
    """Widget 级测试用的最小 Shell 替身：workspace stub 真正驱动 controller。"""

    def __init__(self, controller):
        self.controller = controller

    def navigate(self, page, payload=None):
        pass

    def refresh_status(self):
        pass

    @property
    def pages(self):
        return {"workspace": _WorkspaceStub(self.controller)}


class _WorkspaceStub:
    def __init__(self, controller):
        self.controller = controller

    def select_and_load(self, path):
        ref = next(
            (r for r in self.controller.refs if Path(r.path) == Path(path)), None
        )
        if ref is not None:
            self.controller.open_artifact(ref)
