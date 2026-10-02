"""T7 + ER-P01/02/03 — Runtime 执行、fallback trace 与错误模型测试。"""
import json
import types
from pathlib import Path

import pytest

from plugin_runtime import assemble_runtime
from plugin_runtime.base_provider import CapabilityProviderBase
from plugin_runtime.contracts import (
    CAPABILITY_READ_FULL,
    CapabilityRequest,
    PluginContext,
)
from plugin_runtime.errors import (
    CapabilityNotFoundError,
    PluginLoadError,
    ProviderExecutionError,
    ProviderNotAvailableError,
)
from plugin_runtime.policy import PermissionPolicy
from plugin_runtime.registry import CapabilityRegistry
from plugin_runtime.runtime import CapabilityRuntime
from workspace.errors import ArtifactParseError, WorkspaceBoundaryError

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _make_provider(provider_id, *, priority=100, extensions=(".txt",), behavior="ok"):
    class _P(CapabilityProviderBase):
        pass

    _P.capability_id = CAPABILITY_READ_FULL
    _P.provider_id = provider_id
    _P.priority = priority
    _P.extensions = extensions
    provider = _P(plugin_id="test.runtime")
    provider.behavior = behavior
    provider.execute = _make_execute(behavior, provider)
    return provider


def _make_execute(behavior, provider):
    from plugin_runtime.contracts import CapabilityResult

    def execute(self, request, context):
        if behavior == "ok":
            return CapabilityResult(
                success=True,
                value=f"ok-by-{self.provider_id}",
                provider_id=self.provider_id,
                plugin_id=self.plugin_id,
            )
        if behavior == "parse_error":
            raise ArtifactParseError("fake.docx", adapter=self.provider_id, cause=ValueError("bad"))
        if behavior == "boundary":
            raise WorkspaceBoundaryError("outside", "root")
        if behavior == "crash":
            raise RuntimeError("non-domain explosion")
        if behavior == "unavailable":
            raise ProviderNotAvailableError(CAPABILITY_READ_FULL, self.plugin_id, self.provider_id)
        raise AssertionError(behavior)

    return types.MethodType(execute, provider)


def _request(extension="txt"):
    from workspace.artifact import ArtifactRef
    from datetime import datetime, timezone

    return CapabilityRequest(
        capability=CAPABILITY_READ_FULL,
        artifact_ref=ArtifactRef(
            artifact_id="a_test",
            name=f"file{extension}",
            path=f"/tmp/file{extension}",
            extension=extension.lstrip("."),
            size=10,
            modified_at=datetime(2026, 10, 2, tzinfo=timezone.utc),
            artifact_type=extension.lstrip("."),
        ),
        options={"artifact_id": "a_test"},
    )


def _registry(*providers):
    registry = CapabilityRegistry()
    for provider in providers:
        registry.register(provider)
    return registry


def test_er_p01_capability_not_found():
    runtime = assemble_runtime().runtime
    request = CapabilityRequest(capability="artifact.ocr")
    with pytest.raises(CapabilityNotFoundError):
        runtime.execute(request)


def test_er_p02_provider_unavailable():
    provider = _make_provider("u.reader", behavior="unavailable")

    class _P(type(provider)):
        pass

    def is_available(self, context):
        return False

    provider.is_available = is_available.__get__(provider)
    runtime = CapabilityRuntime(_registry(provider))
    with pytest.raises(ProviderNotAvailableError):
        runtime.execute(_request(), PluginContext(resolved_path=Path("x.txt")))


def test_er_p03_non_domain_exception_wrapped_with_context():
    provider = _make_provider("crash.reader", behavior="crash")
    runtime = CapabilityRuntime(_registry(provider))
    with pytest.raises(ProviderExecutionError) as excinfo:
        runtime.execute(_request(), PluginContext(resolved_path=Path("x.txt")))
    assert excinfo.value.provider_id == "crash.reader"
    assert excinfo.value.capability == CAPABILITY_READ_FULL
    assert excinfo.value.plugin_id == "test.runtime"
    assert isinstance(excinfo.value.cause, RuntimeError)


def test_fallback_chain_and_trace():
    """P6：首选 Provider 解析失败 → fallback 到次选，trace 记录 fallback_from。"""
    first = _make_provider("first.reader", priority=100, behavior="parse_error")
    second = _make_provider("second.reader", priority=50, behavior="ok")
    runtime = CapabilityRuntime(_registry(first, second))
    result = runtime.execute(_request(), PluginContext(resolved_path=Path("x.txt")))
    assert result.value == "ok-by-second.reader"
    assert result.metadata["trace"]["fallback_from"] == "first.reader"
    statuses = [(t.provider_id, t.status) for t in runtime.traces]
    assert statuses == [("first.reader", "error"), ("second.reader", "ok")]


def test_no_silent_fallback_on_workspace_boundary():
    """FR-R03 禁止清单：Workspace 越界不允许 fallback。"""
    first = _make_provider("first.reader", priority=100, behavior="boundary")
    second = _make_provider("second.reader", priority=50, behavior="ok")
    runtime = CapabilityRuntime(_registry(first, second))
    with pytest.raises(WorkspaceBoundaryError):
        runtime.execute(_request(), PluginContext(resolved_path=Path("x.txt")))
    # 第二个 Provider 没有被执行
    assert all(t.provider_id != "second.reader" for t in runtime.traces)


def test_all_providers_failed_raises_last_error():
    first = _make_provider("first.reader", priority=100, behavior="parse_error")
    second = _make_provider("second.reader", priority=50, behavior="crash")
    runtime = CapabilityRuntime(_registry(first, second))
    with pytest.raises(ProviderExecutionError):
        runtime.execute(_request(), PluginContext(resolved_path=Path("x.txt")))


def test_reader_maps_execution_error_to_artifact_parse_error(tmp_path):
    """ER-02 兼容：Provider 执行失败在门面上呈现为 ArtifactParseError。"""
    from services.artifact_reader import ArtifactReader

    target = tmp_path / "broken.docx"
    target.write_bytes(b"not a zip")
    reader = ArtifactReader()
    with pytest.raises(ArtifactParseError):
        reader.read_artifact(target)
