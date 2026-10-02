"""T2/T7 — Discovery / Loader / 故障隔离测试（规格第 14/15/27 节）。"""
import json
from pathlib import Path

import pytest

from plugin_runtime.discovery import discover_builtin, discover_external
from plugin_runtime.loader import load_plugin
from plugin_runtime.errors import PluginLoadError

GOOD_PLUGIN = {
    "id": "test.good.reader",
    "name": "Good Reader",
    "version": "0.1.0",
    "api_version": 1,
    "entrypoint": {"module": "plugin", "class": "GoodPlugin"},
    "accepts": {"extensions": [".good"]},
    "capabilities": [{"id": "artifact.read.full", "priority": 100}],
    "permissions": ["filesystem.read"],
}


def _write_plugin(root: Path, dir_name: str, manifest: dict, plugin_py: str):
    plugin_dir = root / dir_name
    plugin_dir.mkdir(parents=True, exist_ok=True)
    (plugin_dir / "plugin.json").write_text(
        json.dumps(manifest, ensure_ascii=False), encoding="utf-8"
    )
    (plugin_dir / "plugin.py").write_text(plugin_py, encoding="utf-8")
    return plugin_dir


GOOD_PY = '''
from plugin_runtime.base_provider import CapabilityProviderBase

class GoodReadProvider(CapabilityProviderBase):
    provider_id = "test.good.reader.main"
    extensions = (".good",)

    def create_adapter(self, context):
        return None

class GoodPlugin:
    def providers(self):
        return [GoodReadProvider(plugin_id="test.good.reader")]
'''


def test_builtin_discovery_finds_seven_plugins():
    report = discover_builtin()
    ids = {item.manifest.id for item in report.builtins}
    assert {
        "hmbuddy.docx.core",
        "hmbuddy.pdf.core",
        "hmbuddy.xlsx.core",
        "hmbuddy.pptx.core",
        "hmbuddy.xls.core",
        "hmbuddy.doc.core",
        "hmbuddy.text.core",
    } <= ids
    assert not report.errors


def test_builtin_discovery_does_not_load_examples():
    """examples/ 是外部插件样例，不随内置发现自动加载（G5）。"""
    report = discover_builtin()
    ids = {item.manifest.id for item in report.builtins}
    assert "example.markdown.reader" not in ids


def test_external_discovery_from_dir(tmp_path):
    _write_plugin(tmp_path, "my_reader", GOOD_PLUGIN, GOOD_PY)
    report = discover_external([tmp_path])
    assert [item.manifest.id for item in report.externals] == ["test.good.reader"]
    assert report.externals[0].source == "external"


def test_external_discovery_missing_dir_recorded_not_raised(tmp_path):
    report = discover_external([tmp_path / "no-such-dir"])
    assert report.errors and "does not exist" in report.errors[0][1]


def test_discovery_does_not_execute_plugin_code(tmp_path):
    """FR-D03：Manifest 损坏的插件绝不执行其代码。"""
    bad_dir = tmp_path / "broken"
    bad_dir.mkdir()
    (bad_dir / "plugin.json").write_text("{ broken", encoding="utf-8")
    (bad_dir / "plugin.py").write_text(
        "raise RuntimeError('plugin code must not run during discovery')",
        encoding="utf-8",
    )
    report = discover_external([tmp_path])
    assert report.errors and not report.all_plugins


def test_single_broken_plugin_does_not_affect_others(tmp_path):
    """T7/FR-L03：import error 的插件不影响其他插件加载。"""
    _write_plugin(
        tmp_path,
        "broken_import",
        dict(GOOD_PLUGIN, id="test.broken.import"),
        "import nonexistent_module_xyz\n",
    )
    _write_plugin(tmp_path, "good", GOOD_PLUGIN, GOOD_PY)
    _write_plugin(
        tmp_path,
        "broken_ctor",
        dict(GOOD_PLUGIN, id="test.broken.ctor"),
        GOOD_PY.replace(
            "class GoodPlugin:",
            "class GoodPlugin:\n"
            "    def __init__(self):\n"
            "        raise RuntimeError('constructor explosion')",
        ),
    )

    report = discover_external([tmp_path])
    assert len(report.externals) == 3

    failures = []
    loaded = []
    for discovered in report.externals:
        try:
            loaded.append(load_plugin(discovered))
        except PluginLoadError as exc:
            failures.append((discovered.manifest.id, str(exc)))
    assert {item.discovered.manifest.id for item in loaded} == {"test.good.reader"}
    assert {name for name, _ in failures} == {"test.broken.import", "test.broken.ctor"}


def test_entrypoint_class_missing_rejected(tmp_path):
    _write_plugin(
        tmp_path,
        "no_class",
        dict(GOOD_PLUGIN, id="test.noclass"),
        GOOD_PY.replace("class GoodPlugin:", "class OtherName:"),
    )
    report = discover_external([tmp_path])
    with pytest.raises(PluginLoadError, match="entrypoint class"):
        load_plugin(report.externals[0])


def test_provider_undeclared_capability_rejected(tmp_path):
    """FR-M04：Provider 不得注册 Manifest 未声明的能力。"""
    undeclared_py = GOOD_PY.replace(
        'extensions = (".good",)', 'extensions = (".good",)\n    capability_id = "artifact.ocr"'
    )
    _write_plugin(
        tmp_path, "sneaky", dict(GOOD_PLUGIN, id="test.sneaky"), undeclared_py
    )
    report = discover_external([tmp_path])
    with pytest.raises(PluginLoadError, match="not declared in the manifest"):
        load_plugin(report.externals[0])
