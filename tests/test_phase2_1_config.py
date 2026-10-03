"""Phase 2.1 T1/T7 — AppConfig：加载/保存/优先级/校验/原子写/Secret 边界。"""
import json
import os
from pathlib import Path

import pytest

from application.config import (
    AppConfig,
    ConfigSource,
    app_config_path,
    app_data_dir,
    app_logs_dir,
    app_state_path,
    load_config,
    resolve_effective_config,
    save_config,
    validate_config,
)


def test_app_data_paths_defaults(monkeypatch):
    monkeypatch.setenv("APPDATA", r"C:\Users\u\AppData\Roaming")
    monkeypatch.delenv("HMBUDDY_DATA_DIR", raising=False)
    monkeypatch.delenv("HMBUDDY_CONFIG_PATH", raising=False)
    monkeypatch.delenv("HMBUDDY_STATE_PATH", raising=False)
    data_dir = app_data_dir({})
    assert data_dir.name == "HMBuddy"
    assert app_config_path({}).name == "config.json"
    assert app_state_path({}).name == "state.json"
    assert app_logs_dir({}).name == "logs"
    # 显式覆盖（规格第 9 节）
    monkeypatch.setenv("HMBUDDY_CONFIG_PATH", r"D:\custom\cfg.json")
    assert str(app_config_path()) == r"D:\custom\cfg.json"


def test_t1_load_missing_file_returns_defaults(tmp_path):
    config, errors = load_config(tmp_path / "config.json")
    assert errors == []
    assert config.schema_version == 1
    # INT-003：未设置 = None；默认值在 EffectiveConfig 解析层生效
    assert config.desktop.recent_workspace_limit is None
    effective = resolve_effective_config(config)
    assert effective.recent_workspace_limit.value == 10
    assert effective.recent_workspace_limit.source is ConfigSource.DEFAULT


def test_t1_load_valid_config(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "llm": {"base_url": "https://llm.intra/v1", "model": "deepseek"},
                "paths": {"external_plugin_dirs": ["D:/plugins"]},
                "plugins": {"disabled_plugin_ids": ["hmbuddy.doc.core"]},
                "desktop": {"recent_workspace_limit": 3},
            }
        ),
        encoding="utf-8",
    )
    config, errors = load_config(path)
    assert errors == []
    assert config.llm.model == "deepseek"
    assert config.paths.external_plugin_dirs == ["D:/plugins"]
    assert config.plugins.disabled_plugin_ids == ["hmbuddy.doc.core"]
    assert config.desktop.recent_workspace_limit == 3


def test_t1_invalid_json_keeps_file_and_uses_defaults(tmp_path):
    """FR-C02：非法配置继续启动，原文件保留供排查。"""
    path = tmp_path / "config.json"
    path.write_text("{ broken json", encoding="utf-8")
    config, errors = load_config(path)
    assert config.schema_version == 1  # 默认值
    assert errors and "不是合法 JSON" in errors[0]
    assert path.read_text(encoding="utf-8") == "{ broken json"  # 原文件未动


def test_t1_invalid_fields_reported_and_ignored(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps({"desktop": {"recent_workspace_limit": "not-a-number"}}),
        encoding="utf-8",
    )
    config, errors = load_config(path)
    assert config.desktop.recent_workspace_limit is None  # 非法值不采纳（未设置）
    assert any("recent_workspace_limit" in item for item in errors)
    effective = resolve_effective_config(config)
    assert effective.recent_workspace_limit.value == 10  # Effective 层回落默认


def test_t1_atomic_write_and_schema_version(tmp_path):
    path = tmp_path / "config.json"
    save_config(AppConfig(), path)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["schema_version"] == 1  # FR-C04
    assert not list(tmp_path.glob("*.tmp"))  # 原子替换后无残留
    config, errors = load_config(path)
    assert errors == []


def test_t1_secret_never_persisted(tmp_path):
    """FR-C03 / AC-07：明文 API Key 不得写入 config.json。"""
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps({"llm": {"api_key": "sk-secret-value"}}), encoding="utf-8"
    )
    config, errors = load_config(path)
    assert any("api_key" in item for item in errors)
    save_config(config, path)
    content = path.read_text(encoding="utf-8")
    assert "sk-secret-value" not in content
    assert "api_key\"" not in content.replace("api_key_env", "")


def test_validate_config_reports_bad_values():
    config = AppConfig()
    config.plugins.disabled_plugin_ids = ["ok-id", ""]
    config.desktop.recent_workspace_limit = -1
    errors = validate_config(config)
    assert len(errors) == 2


def test_t7_config_precedence_full_chain(tmp_path, monkeypatch):
    """T7：Default < User Config < Environment < Runtime Argument。"""
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps({"llm": {"model": "user-model", "base_url": "https://user/v1"}}),
        encoding="utf-8",
    )
    user_config, _ = load_config(path)

    # 1. Default
    effective = resolve_effective_config(AppConfig(), env={})
    assert effective.llm_model.source is ConfigSource.DEFAULT

    # 2. User Config
    effective = resolve_effective_config(user_config, env={})
    assert effective.llm_model.value == "user-model"
    assert effective.llm_model.source is ConfigSource.USER

    # 3. Environment 覆盖 User Config
    effective = resolve_effective_config(
        user_config, env={"HMBUDDY_LLM_MODEL": "env-model"}
    )
    assert effective.llm_model.value == "env-model"
    assert effective.llm_model.source is ConfigSource.ENVIRONMENT
    assert effective.llm_model.detail == "HMBUDDY_LLM_MODEL"

    # 4. Runtime Argument 最高
    effective = resolve_effective_config(
        user_config,
        env={"HMBUDDY_LLM_MODEL": "env-model"},
        runtime_overrides={"llm_model": "runtime-model"},
    )
    assert effective.llm_model.value == "runtime-model"
    assert effective.llm_model.source is ConfigSource.RUNTIME


def test_t7_env_overrides_explained(tmp_path):
    """AC-08：Effective Config 可解释来源；env 覆盖时 UI 不得假装改 config 即生效。"""
    user_config, _ = load_config(tmp_path / "missing.json")
    effective = resolve_effective_config(
        user_config, env={"HMBUDDY_LLM_BASE_URL": "https://env/v1"}
    )
    assert effective.llm_base_url.source is ConfigSource.ENVIRONMENT
    # 用户 config.json 里 base_url 仍为空——env 值不写回文件
    assert user_config.llm.base_url == ""


def test_t7_external_dirs_merge_dedupe_ordered(tmp_path, monkeypatch):
    """规格第 27 节：Config 与 HMBUDDY_PLUGIN_PATH 合并、去重、保序、来源可辨。"""
    user_config = AppConfig()
    user_config.paths.external_plugin_dirs = ["D:/plugins/a", "D:/plugins/shared"]
    effective = resolve_effective_config(
        user_config,
        env={
            "HMBUDDY_PLUGIN_PATH": "D:/plugins/shared" + os.pathsep + "D:/plugins/b"
        },
    )
    entries = effective.external_plugin_dirs
    paths = [p for p, _ in entries]
    assert paths[0] == str(Path("D:/plugins/a").expanduser())
    assert paths.count(str(Path("D:/plugins/shared").expanduser())) == 1
    sources = {p: s for p, s in entries}
    assert sources[str(Path("D:/plugins/b").expanduser())] is ConfigSource.ENVIRONMENT
    assert sources[str(Path("D:/plugins/a").expanduser())] is ConfigSource.USER


def test_t6_api_key_resolved_from_named_env(monkeypatch):
    """FR-C03：config 只保存 api_key_env 名称，运行期从该环境变量解析密钥。"""
    monkeypatch.setenv("MY_COMPANY_KEY", "sk-runtime-value")
    user_config = AppConfig()
    user_config.llm.api_key_env = "MY_COMPANY_KEY"
    user_config.llm.base_url = "https://llm/v1"
    user_config.llm.model = "m"
    effective = resolve_effective_config(user_config)
    assert effective.api_key == "sk-runtime-value"
    assert effective.llm_configured is True
    # 持久化内容只有变量名，绝无密钥值
    saved = json.dumps(user_config.to_dict())
    assert "sk-runtime-value" not in saved
    assert "MY_COMPANY_KEY" in saved
