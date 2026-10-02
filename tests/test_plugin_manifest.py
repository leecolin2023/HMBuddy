"""T1 — Manifest 校验测试（规格第 9/27 节）。"""
import json

import pytest

from plugin_runtime.errors import PluginCompatibilityError, PluginManifestError
from plugin_runtime.manifest import load_manifest, parse_manifest


def _write_manifest(tmp_path, data, filename="plugin.json"):
    path = tmp_path / filename
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path


VALID = {
    "id": "hmbuddy.docx.core",
    "name": "DOCX Core Plugin",
    "version": "0.1.0",
    "api_version": 1,
    "entrypoint": {"module": "plugins.docx.plugin", "class": "DocxPlugin"},
    "accepts": {"extensions": [".docx"]},
    "capabilities": [{"id": "artifact.read.full", "priority": 100}],
    "permissions": ["filesystem.read"],
}


def test_valid_manifest(tmp_path):
    manifest = load_manifest(_write_manifest(tmp_path, VALID))
    assert manifest.id == "hmbuddy.docx.core"
    assert manifest.capability_ids() == ["artifact.read.full"]
    assert manifest.extensions == [".docx"]
    assert manifest.plugin_dir == tmp_path


@pytest.mark.parametrize(
    "mutation",
    [
        lambda d: d.pop("id"),
        lambda d: d.pop("name"),
        lambda d: d.pop("version"),
        lambda d: d.pop("api_version"),
        lambda d: d.pop("entrypoint"),
        lambda d: d.pop("accepts"),
        lambda d: d.pop("capabilities"),
    ],
)
def test_missing_required_field_rejected(tmp_path, mutation):
    data = json.loads(json.dumps(VALID))
    mutation(data)
    with pytest.raises(PluginManifestError):
        load_manifest(_write_manifest(tmp_path, data))


def test_invalid_plugin_id_rejected(tmp_path):
    data = dict(VALID, id="HMBUDDY DOCX")  # 大写/空格
    with pytest.raises(PluginManifestError, match="invalid plugin id"):
        parse_manifest(data)


def test_invalid_version_rejected(tmp_path):
    data = dict(VALID, version="1.0")  # 非 SemVer
    with pytest.raises(PluginManifestError, match="invalid version"):
        parse_manifest(data)


def test_incompatible_api_version_rejected(tmp_path):
    data = dict(VALID, api_version=999)
    with pytest.raises(PluginCompatibilityError, match="api_version"):
        parse_manifest(data)


def test_unknown_permission_rejected(tmp_path):
    data = dict(VALID, permissions=["filesystem.read", "root.access"])
    with pytest.raises(PluginManifestError, match="unknown permission"):
        parse_manifest(data)


def test_duplicate_capability_rejected(tmp_path):
    data = dict(
        VALID,
        capabilities=[
            {"id": "artifact.read.full"},
            {"id": "artifact.read.full", "priority": 50},
        ],
    )
    with pytest.raises(PluginManifestError, match="duplicate capability"):
        parse_manifest(data)


def test_invalid_extension_rejected(tmp_path):
    data = dict(VALID, accepts={"extensions": ["docx"]})  # 缺点号
    with pytest.raises(PluginManifestError, match="invalid extension"):
        parse_manifest(data)


def test_broken_json_rejected(tmp_path):
    path = tmp_path / "plugin.json"
    path.write_text("{ not json", encoding="utf-8")
    with pytest.raises(PluginManifestError, match="invalid JSON"):
        load_manifest(path)


def test_missing_manifest_file_rejected(tmp_path):
    with pytest.raises(PluginManifestError, match="not found"):
        load_manifest(tmp_path / "nope" / "plugin.json")
