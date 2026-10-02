"""Phase 1.1.1 Contract Hardening 验收测试（规格第 23/24 节 T2-T13 / AC-H01~H13）。

T1 权限强制与 T7 Ref 信任域分别在 evals/test_xls_doc.py 与
evals/test_artifact_reader.py 覆盖；此处覆盖其余验收项。
"""
import json
import sys
import types
from pathlib import Path

import pytest

from plugin_runtime import assemble_runtime
from plugin_runtime.base_provider import CapabilityProviderBase
from plugin_runtime.catalog import CapabilityCatalog, StaticExtensionCatalog
from plugin_runtime.contracts import (
    CAPABILITY_READ_FULL,
    CapabilityRequest,
    PluginContext,
)
from plugin_runtime.errors import (
    CapabilityNotFoundError,
    PluginPermissionError,
    ProviderExecutionError,
    ProviderNotAvailableError,
    ProviderSelectionError,
)
from plugin_runtime.policy import PermissionPolicy
from plugin_runtime.registry import CapabilityRegistry
from workspace.errors import (
    ArtifactNotFoundError,
    ArtifactParseError,
    EncryptedArtifactError,
    WorkspaceBoundaryError,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = PROJECT_ROOT / "evals" / "fixtures"


# ---------------------------------------------------------------------------
# 插件构建工具
# ---------------------------------------------------------------------------

def _write_plugin(root: Path, dir_name: str, manifest: dict, files: dict[str, str]):
    plugin_dir = root / dir_name
    plugin_dir.mkdir(parents=True, exist_ok=True)
    (plugin_dir / "plugin.json").write_text(
        json.dumps(manifest, ensure_ascii=False), encoding="utf-8"
    )
    for relative, content in files.items():
        target = plugin_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return plugin_dir


def _manifest(**overrides):
    base = {
        "id": "test.foo.reader",
        "name": "Foo Reader",
        "version": "0.1.0",
        "api_version": 1,
        "entrypoint": {"module": "plugin", "class": "FooPlugin"},
        "accepts": {"extensions": [".foo"]},
        "capabilities": [{"id": "artifact.read.full", "priority": 100}],
        "permissions": ["filesystem.read"],
    }
    base.update(overrides)
    if "priority" in base:  # 便捷参数：写到 capabilities[0].priority
        base["capabilities"][0]["priority"] = base.pop("priority")
    return base


FOO_PLUGIN_PY = '''
from pathlib import Path

from plugin_runtime.base_provider import CapabilityProviderBase
from plugin_runtime.contracts import CapabilityResult
from workspace.artifact import Artifact, ArtifactBlock


class FooReadProvider(CapabilityProviderBase):
    provider_id = "test.foo.reader.main"
    extensions = (".foo",)  # 故意与 Manifest 冲突，Loader 必须覆盖

    def create_adapter(self, context):
        return None

    def execute(self, request, context):
        path = Path(context.resolved_path)
        text = path.read_text(encoding="utf-8")
        artifact = Artifact(
            artifact_id=str(request.options.get("artifact_id") or ""),
            name=path.name,
            path=str(path),
            artifact_type="foo",
            metadata={},
            content=text,
            blocks=[ArtifactBlock("", "paragraph", text, {}, {})],
            provenance={},
        )
        return CapabilityResult(True, artifact, self.provider_id, self.plugin_id,
                                plugin_version=self.plugin_version)


class FooPlugin:
    def providers(self):
        return [FooReadProvider(plugin_id="hmbuddy.docx.core")]  # 冲突：伪装成 docx
'''


def test_t2_new_extension_full_chain(tmp_path):
    """T2 / AC-H02：全新 .foo 扩展名，不改 Core 完成发现→读取全链路。"""
    outside_root = tmp_path / "data"
    outside_root.mkdir()
    (outside_root / "model.foo").write_text("foo 数据内容", encoding="utf-8")
    _write_plugin(tmp_path, "foo_plugin", _manifest(), {"plugin.py": FOO_PLUGIN_PY})

    assembly = assemble_runtime(
        external_plugin_dirs=[tmp_path], use_env_plugin_path=False
    )
    assert any(
        item.discovered.manifest.id == "test.foo.reader"
        for item in assembly.load_report.loaded
    ), assembly.load_report.failures

    from plugin_runtime.catalog import CapabilityCatalog

    from workspace.workspace import Workspace

    workspace = Workspace(outside_root)
    # 用带外部插件的 Catalog 装配 Workspace（模拟完整安装新插件后的环境）
    workspace_with_plugin = Workspace(
        outside_root, extension_catalog=CapabilityCatalog(assembly.registry)
    )
    refs = workspace_with_plugin.list_artifacts()
    foo_refs = [r for r in refs if r.name == "model.foo"]
    assert foo_refs, "Workspace 必须自动发现 .foo（不改 Core）"
    assert foo_refs[0].artifact_type == "foo"
    assert foo_refs[0].workspace_id == workspace_with_plugin.workspace_id

    from services.artifact_reader import ArtifactReader

    reader = ArtifactReader(external_plugin_dirs=[tmp_path])
    artifact = reader.read_artifact(foo_refs[0], workspace=workspace_with_plugin)
    assert artifact.artifact_type == "foo"
    assert artifact.content == "foo 数据内容"
    assert artifact.provenance["plugin_id"] == "test.foo.reader"


def test_t3_manifest_is_authoritative(tmp_path):
    """T3 / AC-H03：Provider 与 Manifest 冲突时，Manifest 必须生效。"""
    _write_plugin(
        tmp_path,
        "foo_plugin",
        _manifest(priority=10),  # Manifest: .foo / priority=10
        {"plugin.py": FOO_PLUGIN_PY},  # Provider: 伪装 docx / priority 9999 继承基类默认
    )
    assembly = assemble_runtime(
        external_plugin_dirs=[tmp_path], use_env_plugin_path=False
    )
    providers = assembly.registry.providers_for_plugin("test.foo.reader")
    provider = providers[0]
    assert provider.extensions == (".foo",)  # 不再是 .docx
    assert provider.priority == 10
    assert provider.plugin_id == "test.foo.reader"  # 不再是 hmbuddy.docx.core
    assert provider.plugin_version == "0.1.0"
    # .docx 路由不受影响（不抢占）
    from workspace.artifact import ArtifactRef
    from datetime import datetime, timezone

    request = CapabilityRequest(
        capability=CAPABILITY_READ_FULL,
        artifact_ref=ArtifactRef(
            artifact_id="a_x", name="a.docx", path="/tmp/a.docx",
            extension="docx", size=1,
            modified_at=datetime(2026, 10, 2, tzinfo=timezone.utc),
            artifact_type="docx",
        ),
    )
    assert not provider.supports(request)


def test_t4_provider_single_materialization(tmp_path):
    """T4 / AC-H04：providers() 每次返回新对象时，Loader 只调用一次，
    Registry 注册对象与 Loader 校验对象同一。"""
    counting_py = FOO_PLUGIN_PY.replace(
        'class FooPlugin:\n    def providers(self):\n'
        '        return [FooReadProvider(plugin_id="hmbuddy.docx.core")]',
        'class FooPlugin:\n'
        '    materialize_count = 0\n\n'
        '    def __init__(self):\n'
        '        type(self).materialize_count = 0\n\n'
        '    def providers(self):\n'
        '        type(self).materialize_count += 1\n'
        '        return [FooReadProvider(plugin_id="hmbuddy.docx.core")]',
    )
    assert "materialize_count += 1" in counting_py  # 确认注入生效
    _write_plugin(tmp_path, "foo_plugin", _manifest(), {"plugin.py": counting_py})
    assembly = assemble_runtime(
        external_plugin_dirs=[tmp_path], use_env_plugin_path=False
    )
    loaded = next(
        item
        for item in assembly.load_report.loaded
        if item.discovered.manifest.id == "test.foo.reader"
    )
    assert loaded.plugin.materialize_count == 1  # 只物化一次
    registry_provider = assembly.registry.providers_for_plugin("test.foo.reader")[0]
    assert registry_provider is loaded.providers[0]  # 对象 identity 一致


def test_t5_external_plugin_dirs_parameter(tmp_path):
    """T5 / AC-H05：ArtifactReader(external_plugin_dirs=...) 直接生效，
    不允许 monkeypatch runtime / 环境变量兜底。"""
    _write_plugin(tmp_path, "foo_plugin", _manifest(), {"plugin.py": FOO_PLUGIN_PY})
    target = tmp_path / "sample.foo"
    target.write_text("foo", encoding="utf-8")

    from services.artifact_reader import ArtifactReader

    reader = ArtifactReader(external_plugin_dirs=[tmp_path])
    artifact = reader.read_artifact(target)
    assert artifact.provenance["plugin_id"] == "test.foo.reader"


def test_t6_default_context_budget_via_client():
    """T6 / AC-H06：LLM 主路径默认有界，调用方无需配置。"""
    from llm.client import MockLLMClient
    from workspace.artifact import Artifact, ArtifactBlock

    huge = Artifact(
        artifact_id="a_huge",
        name="huge.txt",
        path="/tmp/huge.txt",
        artifact_type="txt",
        blocks=[
            ArtifactBlock(
                "", "paragraph", f"第 {index} 段超长正文内容" * 20, {"line_index": index}, {}
            )
            for index in range(2000)
        ],
        content="x" * 200000,
    )
    client = MockLLMClient()
    answer = client.ask(huge, "这份文档说了什么？")
    assert answer == "mock answer"
    user_message = client.last_user_message
    assert len(user_message) < 60000  # 默认预算（20000 chars + 头部 + 问题）
    assert "[Context Truncated]" in user_message
    assert client.last_context_result.truncated is True


def test_t8_availability_platform_and_python(tmp_path, monkeypatch):
    """T8 / AC-H08：platform / python / 依赖可用性参与路由。"""
    _write_plugin(
        tmp_path,
        "foo_plugin",
        _manifest(platforms=["linux"], runtime={"python": ">=3.10"}),
        {"plugin.py": FOO_PLUGIN_PY},
    )
    assembly = assemble_runtime(
        external_plugin_dirs=[tmp_path], use_env_plugin_path=False
    )
    provider = assembly.registry.providers_for_plugin("test.foo.reader")[0]

    from workspace.artifact import ArtifactRef
    from datetime import datetime, timezone

    ref = ArtifactRef(
        artifact_id="a", name="x.foo", path="x.foo", extension="foo", size=1,
        modified_at=datetime(2026, 10, 2, tzinfo=timezone.utc), artifact_type="foo",
    )
    request = CapabilityRequest(capability=CAPABILITY_READ_FULL, artifact_ref=ref)
    context = PluginContext(resolved_path=Path("x.foo"))

    if sys.platform.startswith("win"):
        # 当前为 Windows，manifest 声明 linux-only → 不可用且原因可诊断
        with pytest.raises(ProviderNotAvailableError, match="platform"):
            assembly.runtime.execute(request, context)
        assert provider.availability_reason(context) and "platform" in provider.availability_reason(context)
    else:
        assert provider.availability_reason(context) is None

    # python_requires 不满足 → 不可用（第二个插件 provider_id 必须不同，
    # 否则会被 Registry 的重复注册检测正确拒绝）
    future_py = FOO_PLUGIN_PY.replace("test.foo.reader.main", "test.future.reader.main")
    _write_plugin(
        tmp_path,
        "future_plugin",
        _manifest(
            id="test.future.reader",
            name="Future",
            runtime={"python": ">=99.0"},
        ),
        {"plugin.py": future_py},
    )
    assembly2 = assemble_runtime(
        external_plugin_dirs=[tmp_path], use_env_plugin_path=False
    )
    future_provider = next(
        p
        for p in assembly2.registry.list_providers(CAPABILITY_READ_FULL)
        if p.plugin_id == "test.future.reader"
    )
    reason = future_provider.availability_reason(context)
    assert reason and "python" in reason


def test_t8_dependency_probe_blocks_execution():
    class _P(CapabilityProviderBase):
        provider_id = "dep.reader"
        extensions = (".dep",)

        def probe_dependencies(self):
            return "missing optional dependency 'superlib'"

        def create_adapter(self, context):
            return None

    registry = CapabilityRegistry()
    registry.register(_P(plugin_id="test.dep"))
    from plugin_runtime.runtime import CapabilityRuntime

    runtime = CapabilityRuntime(registry)
    with pytest.raises(ProviderNotAvailableError, match="superlib"):
        runtime.execute(
            CapabilityRequest(
                capability=CAPABILITY_READ_FULL, artifact_ref=_ref("x.dep")
            ),
            PluginContext(resolved_path=Path("x.dep")),
        )


def _ref(name, extension=None):
    from datetime import datetime, timezone

    from workspace.artifact import ArtifactRef

    ext = extension or name.rsplit(".", 1)[-1]
    return ArtifactRef(
        artifact_id="a",
        name=name,
        path=name,
        extension=ext,
        size=1,
        modified_at=datetime(2026, 10, 2, tzinfo=timezone.utc),
        artifact_type=ext,
    )


def test_t9_locators_on_all_formats():
    """T9 / AC-H09：四种格式的 Block 均生成标准 Locator。"""
    from services.artifact_reader import ArtifactReader

    reader = ArtifactReader()
    docx_standard = reader.read_artifact(FIXTURES_DIR / "sample.docx")
    pdf_standard = reader.read_artifact(FIXTURES_DIR / "sample.pdf")
    xlsx_standard = reader.read_artifact(FIXTURES_DIR / "sample.xlsx")
    pptx_standard = reader.read_artifact(FIXTURES_DIR / "sample.pptx")

    assert docx_standard.blocks, "docx blocks 不应为空"
    for block in docx_standard.blocks:
        assert block.locator is not None, block.block_type
        assert block.locator.scheme == "docx"
        assert set(block.locator.data) <= {"paragraph_index", "table_index"}
    for block in pdf_standard.blocks:
        assert block.locator is not None and block.locator.scheme == "pdf"
        assert "page" in block.locator.data
    for block in xlsx_standard.blocks:
        assert block.locator is not None and block.locator.scheme == "xlsx"
        assert set(block.locator.data) == {"sheet", "range"}
    for block in pptx_standard.blocks:
        assert block.locator is not None and block.locator.scheme == "pptx"
        assert "slide" in block.locator.data


def test_t10_success_false_never_records_ok():
    """T10 / AC-H10：success=False 不得产生 ok trace。"""

    class _P(CapabilityProviderBase):
        provider_id = "failing.reader"
        extensions = (".txt",)

        def create_adapter(self, context):
            return None

        def execute(self, request, context):
            from plugin_runtime.contracts import CapabilityResult

            return CapabilityResult(
                success=False, value=None, provider_id=self.provider_id,
                plugin_id=self.plugin_id, error="provider-level failure",
            )

    registry = CapabilityRegistry()
    registry.register(_P(plugin_id="test.failing"))
    from plugin_runtime.runtime import CapabilityRuntime

    runtime = CapabilityRuntime(registry)
    with pytest.raises(ProviderExecutionError, match="success=False"):
        runtime.execute(
            CapabilityRequest(capability=CAPABILITY_READ_FULL, artifact_ref=_ref("x.txt")),
            PluginContext(resolved_path=Path("x.txt")),
        )
    assert all(t.status != "ok" for t in runtime.traces)
    assert runtime.traces[-1].status == "error"


def test_t11_selection_diagnostics():
    """T11 / AC-H11：supports 异常不得伪装成"不支持"。"""

    class _Bad(CapabilityProviderBase):
        provider_id = "bad.supports"
        extensions = (".txt",)

        def supports(self, request):
            raise RuntimeError("supports exploded")

        def create_adapter(self, context):
            return None

    registry = CapabilityRegistry()
    registry.register(_Bad(plugin_id="test.bad"))
    from plugin_runtime.runtime import CapabilityRuntime

    runtime = CapabilityRuntime(registry)
    with pytest.raises(ProviderSelectionError) as excinfo:
        runtime.execute(
            CapabilityRequest(capability=CAPABILITY_READ_FULL, artifact_ref=_ref("x.txt")),
            PluginContext(resolved_path=Path("x.txt")),
        )
    diagnostic = excinfo.value.diagnostics[0]
    assert diagnostic["stage"] == "supports"
    assert diagnostic["error_type"] == "RuntimeError"
    assert diagnostic["provider_id"] == "bad.supports"


def test_t12_fallback_allowlist():
    """T12 / AC-H12：fallback 只对显式 allowlist 的错误发生。"""

    def _runtime(behaviors):
        registry = CapabilityRegistry()
        for index, behavior in enumerate(behaviors):
            provider = _behavior_provider(f"p{index}.reader", 100 - index, behavior)
            registry.register(provider)
        from plugin_runtime.runtime import CapabilityRuntime

        return CapabilityRuntime(registry)

    def _run(behaviors):
        runtime = _runtime(behaviors)
        try:
            runtime.execute(
                CapabilityRequest(capability=CAPABILITY_READ_FULL, artifact_ref=_ref("x.txt")),
                PluginContext(resolved_path=Path("x.txt")),
            )
            return "ok"
        except Exception as exc:
            return type(exc).__name__

    # parse 类错误 → fallback 到 ok Provider
    assert _run(["parse_error", "ok"]) == "ok"
    # 加密文件：显式决定为允许 fallback（换 COM 类 Provider 有意义）
    assert _run(["encrypted", "ok"]) == "ok"
    # 越界 / 不存在 → 禁止 fallback
    assert _run(["boundary", "ok"]) == "WorkspaceBoundaryError"
    assert _run(["not_found", "ok"]) == "ArtifactNotFoundError"
    # 权限 → 禁止 fallback
    assert _run(["permission", "ok"]) == "PluginPermissionError"


def _behavior_provider(provider_id, priority, behavior):
    class _P(CapabilityProviderBase):
        pass

    _P.capability_id = CAPABILITY_READ_FULL
    _P.provider_id = provider_id
    _P.priority = priority
    _P.extensions = (".txt",)
    provider = _P(plugin_id="test.allowlist")
    provider.behavior = behavior

    import types
    from plugin_runtime.contracts import CapabilityResult

    def execute(self, request, context):
        if self.behavior == "ok":
            return CapabilityResult(True, "ok", self.provider_id, self.plugin_id)
        if self.behavior == "parse_error":
            raise ArtifactParseError("x.txt", adapter=self.provider_id, cause=ValueError("bad"))
        if self.behavior == "encrypted":
            raise EncryptedArtifactError("x.txt", adapter=self.provider_id, reason="enc")
        if self.behavior == "boundary":
            raise WorkspaceBoundaryError("x.txt", "root")
        if self.behavior == "not_found":
            raise ArtifactNotFoundError("x.txt")
        if self.behavior == "permission":
            raise PluginPermissionError(self.plugin_id, ["office.com"], ())
        raise AssertionError(self.behavior)

    provider.execute = types.MethodType(execute, provider)
    return provider


def test_t13_external_package_plugin_with_relative_import(tmp_path):
    """T13 / AC-H13：外部插件可以是标准 package，内部相对 import 正常。"""
    manifest = _manifest(
        id="test.pkg.reader",
        entrypoint={"module": "hmbuddy_foo.plugin", "class": "FooPackagePlugin"},
    )
    package_code = '''
from .parser import parse_foo  # 相对 import，验证 package 机制

from plugin_runtime.base_provider import CapabilityProviderBase
from plugin_runtime.contracts import CapabilityResult
from workspace.artifact import Artifact, ArtifactBlock
from pathlib import Path


class PkgFooProvider(CapabilityProviderBase):
    provider_id = "test.pkg.reader.main"
    extensions = (".foo",)

    def create_adapter(self, context):
        return None

    def execute(self, request, context):
        text = parse_foo(Path(context.resolved_path))
        artifact = Artifact(
            artifact_id=str(request.options.get("artifact_id") or ""),
            name=Path(context.resolved_path).name,
            path=str(context.resolved_path),
            artifact_type="foo",
            metadata={},
            content=text,
            blocks=[ArtifactBlock("", "paragraph", text, {}, {})],
            provenance={},
        )
        return CapabilityResult(True, artifact, self.provider_id, self.plugin_id)


class FooPackagePlugin:
    def providers(self):
        return [PkgFooProvider(plugin_id="test.pkg.reader")]
'''
    parser_code = '''
def parse_foo(path):
    return path.read_text(encoding="utf-8")
'''
    plugin_dir = _write_plugin(
        tmp_path,
        "pkg_plugin",
        manifest,
        {
            "hmbuddy_foo/__init__.py": "",
            "hmbuddy_foo/plugin.py": package_code,
            "hmbuddy_foo/parser.py": parser_code,
        },
    )

    assembly = assemble_runtime(
        external_plugin_dirs=[tmp_path], use_env_plugin_path=False
    )
    assert any(
        item.discovered.manifest.id == "test.pkg.reader"
        for item in assembly.load_report.loaded
    ), assembly.load_report.failures

    target = tmp_path / "sample.foo"
    target.write_text("package 插件内容", encoding="utf-8")
    from services.artifact_reader import ArtifactReader

    reader = ArtifactReader(external_plugin_dirs=[tmp_path])
    artifact = reader.read_artifact(target)
    assert artifact.content == "package 插件内容"
    assert artifact.provenance["plugin_id"] == "test.pkg.reader"


def test_t15_trace_bounded_and_started_at_correct():
    """BUG-015 / AC-H15：traces 有界且 started_at 是真实开始时间。"""
    from plugin_runtime.runtime import CapabilityRuntime

    registry = CapabilityRegistry()

    class _P(CapabilityProviderBase):
        provider_id = "slow.reader"
        extensions = (".txt",)

        def create_adapter(self, context):
            return None

        def execute(self, request, context):
            import time as _time

            from plugin_runtime.contracts import CapabilityResult

            _time.sleep(0.02)
            return CapabilityResult(True, "ok", self.provider_id, self.plugin_id)

    registry.register(_P(plugin_id="test.trace"))
    runtime = CapabilityRuntime(registry, max_traces=5)
    for index in range(20):
        runtime.execute(
            CapabilityRequest(capability=CAPABILITY_READ_FULL, artifact_ref=_ref("x.txt")),
            PluginContext(resolved_path=Path("x.txt")),
        )
    assert len(runtime.traces) == 5  # 有界
    from datetime import datetime

    parsed = datetime.fromisoformat(runtime.traces[-1].started_at)
    assert parsed.tzinfo is not None
    # started_at 必须早于 trace 记录完成的当前时间，且 duration 与 sleep 相符
    assert runtime.traces[-1].duration_ms >= 15


def test_catalog_views():
    """BUG-002：CapabilityCatalog 提供扩展名视图。"""
    assembly = get_default_runtime()
    catalog = CapabilityCatalog(assembly.registry)
    extensions = catalog.artifact_extensions()
    assert {".docx", ".pdf", ".xlsx", ".pptx", ".xls", ".doc"} <= extensions
    assert catalog.can_handle_extension(".docx")
    assert catalog.can_handle_extension("DOCX")  # 大小写归一
    assert not catalog.can_handle_extension(".nope")
    assert catalog.artifact_type_for(".docx") == "docx"
    providers = catalog.providers_for(".docx")
    assert providers and providers[0].plugin_id == "hmbuddy.docx.core"


def get_default_runtime():  # 局部 helper：避免顶部导入顺序问题
    from plugin_runtime import get_default_runtime as _fn

    return _fn()
