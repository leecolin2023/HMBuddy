"""T3/AC-05 — Capability Registry 测试（priority / 多 Provider / 确定性 tie-break）。"""
import pytest

from plugin_runtime.base_provider import CapabilityProviderBase
from plugin_runtime.errors import CapabilityNotFoundError, DuplicatePluginError
from plugin_runtime.registry import CapabilityRegistry


def _provider(provider_id, priority=100, extensions=(".docx",), plugin_id="test.plugin"):
    class _P(CapabilityProviderBase):
        pass

    _P.capability_id = "artifact.read.full"
    _P.provider_id = provider_id
    _P.priority = priority
    _P.extensions = extensions
    return _P(plugin_id=plugin_id)


def test_register_and_list_capabilities():
    registry = CapabilityRegistry()
    registry.register(_provider("a.first"))
    assert registry.list_capabilities() == ["artifact.read.full"]
    assert registry.has_capability("artifact.read.full")
    assert len(registry.list_providers("artifact.read.full")) == 1
    assert registry.providers_for_plugin("test.plugin")


def test_duplicate_provider_registration_rejected():
    registry = CapabilityRegistry()
    registry.register(_provider("same.id"))
    with pytest.raises(DuplicatePluginError, match="duplicate provider registration"):
        registry.register(_provider("same.id"))


def test_priority_sorting_descending():
    registry = CapabilityRegistry()
    registry.register(_provider("low", priority=10))
    registry.register(_provider("high", priority=100))
    registry.register(_provider("mid", priority=50))
    ordered = [p.provider_id for p in registry.list_providers("artifact.read.full")]
    assert ordered == ["high", "mid", "low"]


def test_deterministic_tie_break_by_provider_id():
    """AC-05：同 priority 时按 provider_id 字母序稳定解析。"""
    registry = CapabilityRegistry()
    registry.register(_provider("zeta", priority=100))
    registry.register(_provider("alpha", priority=100))
    registry.register(_provider("mid", priority=100))
    ordered = [p.provider_id for p in registry.list_providers("artifact.read.full")]
    assert ordered == ["alpha", "mid", "zeta"]


def test_resolve_unknown_capability_raises():
    registry = CapabilityRegistry()
    from plugin_runtime.contracts import CapabilityRequest

    with pytest.raises(CapabilityNotFoundError):
        registry.resolve(CapabilityRequest(capability="artifact.ocr"))


def test_extensions_claimed():
    registry = CapabilityRegistry()
    registry.register(_provider("docx.reader", extensions=(".docx",)))
    registry.register(_provider("pdf.reader", extensions=(".pdf",)))
    assert registry.extensions_claimed() == {".docx", ".pdf"}
