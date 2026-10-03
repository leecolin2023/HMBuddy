"""AppConfig（规格第 9-13 节）：统一应用配置。

- Config Source Precedence（T7）：Default < User config.json < Environment < Runtime Argument；
- 原子写（FR-C01）：config.json.tmp → flush → replace；
- 非法配置不阻断启动（FR-C02）：保留原文件，使用默认值/可解析部分；
- Secret 边界（FR-C03）：config.json 永不保存明文 API Key，只保存 api_key_env；
- schema_version 第一版就存在（FR-C04）；
- Effective Config 可解释每个值的来源（AC-08）。
"""
from __future__ import annotations

import json
import logging
import os
import sys
from dataclasses import asdict, dataclass, field, fields, replace
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

LOGGER = logging.getLogger("hmbuddy.config")

CONFIG_SCHEMA_VERSION = 1
DEFAULT_API_KEY_ENV = "HMBUDDY_LLM_API_KEY"

ENV_LLM_BASE_URL = "HMBUDDY_LLM_BASE_URL"
ENV_LLM_MODEL = "HMBUDDY_LLM_MODEL"
ENV_MODEL_DIR = "HMBUDDY_MODEL_DIR"
ENV_PLUGIN_PATH = "HMBUDDY_PLUGIN_PATH"
ENV_CONFIG_PATH = "HMBUDDY_CONFIG_PATH"
ENV_STATE_PATH = "HMBUDDY_STATE_PATH"
ENV_DATA_DIR = "HMBUDDY_DATA_DIR"

# 历史兼容：Phase 2 曾直接读取 FCE_MODEL_DIR
LEGACY_ENV_MODEL_DIR = "FCE_MODEL_DIR"


class ConfigSource(str, Enum):
    DEFAULT = "Default"
    USER = "User Config"
    ENVIRONMENT = "Environment"
    RUNTIME = "Runtime Argument"


@dataclass
class LlmConfig:
    base_url: str = ""
    model: str = ""
    api_key_env: str = DEFAULT_API_KEY_ENV


@dataclass
class PathsConfig:
    external_plugin_dirs: list[str] = field(default_factory=list)
    model_dir: str = ""


@dataclass
class PluginsConfig:
    disabled_plugin_ids: list[str] = field(default_factory=list)


@dataclass
class DesktopConfig:
    """INT-003：None = 用户未设置（回落 Default）；False / 0 是合法显式配置。"""

    restore_last_workspace: bool | None = None
    recent_workspace_limit: int | None = None
    recent_activity_limit: int | None = None


@dataclass
class AppConfig:
    schema_version: int = CONFIG_SCHEMA_VERSION
    llm: LlmConfig = field(default_factory=LlmConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    plugins: PluginsConfig = field(default_factory=PluginsConfig)
    desktop: DesktopConfig = field(default_factory=DesktopConfig)

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# 用户数据目录（规格第 9 节）
# ---------------------------------------------------------------------------


def app_data_dir(env=None) -> Path:
    """Per-user data directory：Windows %APPDATA%\\HMBuddy，其余 ~/.local/share/HMBuddy。

    可用 HMBUDDY_DATA_DIR 整体覆盖（测试 / 便携部署）。
    """
    env = os.environ if env is None else env
    override = (env.get(ENV_DATA_DIR) or "").strip()
    if override:
        return Path(override).expanduser()
    if sys.platform.startswith("win"):
        base = env.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        return Path(base) / "HMBuddy"
    base = env.get("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
    return Path(base) / "HMBuddy"


def app_config_path(env=None) -> Path:
    env = os.environ if env is None else env
    override = (env.get(ENV_CONFIG_PATH) or "").strip()
    if override:
        return Path(override).expanduser()
    return app_data_dir(env) / "config.json"


def app_state_path(env=None) -> Path:
    env = os.environ if env is None else env
    override = (env.get(ENV_STATE_PATH) or "").strip()
    if override:
        return Path(override).expanduser()
    return app_data_dir(env) / "state.json"


def app_logs_dir(env=None) -> Path:
    return app_data_dir(env) / "logs"


# ---------------------------------------------------------------------------
# 加载 / 保存 / 校验
# ---------------------------------------------------------------------------


def _parse_config(data: Any, errors: list[str]) -> AppConfig:
    """从已解析 JSON 构造 AppConfig；未知/非法字段记入 errors 并忽略（FR-C02）。"""
    config = AppConfig()
    if not isinstance(data, dict):
        errors.append("config 根节点必须是 JSON 对象")
        return config

    # FR-C03：明文 Secret 出现在配置文件中 → 视为非法并忽略该字段
    for secret_key in ("api_key", "api_key_value", "token", "password"):
        if secret_key in data:
            errors.append(
                f"config.json 不允许保存明文 {secret_key!r}（只允许 llm.api_key_env），已忽略"
            )

    version = data.get("schema_version", CONFIG_SCHEMA_VERSION)
    if not isinstance(version, int):
        errors.append("schema_version 必须是整数，已忽略并使用当前版本")
    elif version > CONFIG_SCHEMA_VERSION:
        errors.append(
            f"config schema_version {version} 高于当前支持的 {CONFIG_SCHEMA_VERSION}，"
            "将按当前版本尽力解析"
        )
    else:
        config.schema_version = version

    llm = data.get("llm") or {}
    if isinstance(llm, dict):
        config.llm.base_url = str(llm.get("base_url") or "")
        config.llm.model = str(llm.get("model") or "")
        api_key_env = str(llm.get("api_key_env") or "").strip()
        if "api_key" in llm:
            errors.append("llm.api_key 不允许保存明文密钥，已忽略")
        config.llm.api_key_env = api_key_env or DEFAULT_API_KEY_ENV

    paths = data.get("paths") or {}
    if isinstance(paths, dict):
        dirs = paths.get("external_plugin_dirs") or []
        if isinstance(dirs, list):
            config.paths.external_plugin_dirs = [str(item) for item in dirs]
        else:
            errors.append("paths.external_plugin_dirs 必须是列表")
        config.paths.model_dir = str(paths.get("model_dir") or "")

    plugins = data.get("plugins") or {}
    if isinstance(plugins, dict):
        disabled = plugins.get("disabled_plugin_ids") or []
        if isinstance(disabled, list):
            config.plugins.disabled_plugin_ids = [str(item) for item in disabled]
        else:
            errors.append("plugins.disabled_plugin_ids 必须是列表")

    desktop = data.get("desktop") or {}
    if isinstance(desktop, dict):
        # INT-003：区分"未设置"（None/缺省 → Default）与显式 False / 0（User Config）
        if "restore_last_workspace" in desktop:
            value = desktop.get("restore_last_workspace")
            if value is None:
                pass  # 未设置：保留 None，解析层回落默认
            elif isinstance(value, bool):
                config.desktop.restore_last_workspace = value
            else:
                errors.append("desktop.restore_last_workspace 必须是布尔值")
        if "recent_workspace_limit" in desktop:
            limit = desktop.get("recent_workspace_limit")
            if limit is None:
                pass
            elif isinstance(limit, int) and not isinstance(limit, bool) and limit >= 0:
                config.desktop.recent_workspace_limit = limit
            else:
                errors.append("desktop.recent_workspace_limit 必须是非负整数")
        if "recent_activity_limit" in desktop:
            activity_limit = desktop.get("recent_activity_limit")
            if activity_limit is None:
                pass
            elif (
                isinstance(activity_limit, int)
                and not isinstance(activity_limit, bool)
                and activity_limit >= 0
            ):
                config.desktop.recent_activity_limit = activity_limit
            else:
                errors.append("desktop.recent_activity_limit 必须是非负整数")

    errors.extend(validate_config(config))
    return config


def load_config(path: Path, env=None) -> tuple[AppConfig, list[str]]:
    """加载用户配置；文件缺失 / 非法 JSON 时返回默认值与错误列表（FR-C02），
    原文件保留不动。"""
    path = Path(path)
    errors: list[str] = []
    if not path.is_file():
        return AppConfig(), errors
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"读取 config 失败（使用默认配置）：{exc}")
        return AppConfig(), errors
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        errors.append(f"config.json 不是合法 JSON（已保留原文件）：{exc}")
        return AppConfig(), errors
    return _parse_config(data, errors), errors


def validate_config(config: AppConfig) -> list[str]:
    errors: list[str] = []
    if config.schema_version != CONFIG_SCHEMA_VERSION:
        errors.append(
            f"schema_version 应为 {CONFIG_SCHEMA_VERSION}，当前 {config.schema_version}"
        )
    for plugin_id in config.plugins.disabled_plugin_ids:
        if not plugin_id.strip():
            errors.append("disabled_plugin_ids 含空字符串")
    desktop = config.desktop
    if desktop.restore_last_workspace is not None and not isinstance(
        desktop.restore_last_workspace, bool
    ):
        errors.append("restore_last_workspace 必须是布尔值或未设置")
    for name, value in (
        ("recent_workspace_limit", desktop.recent_workspace_limit),
        ("recent_activity_limit", desktop.recent_activity_limit),
    ):
        if value is not None and (not isinstance(value, int) or isinstance(value, bool) or value < 0):
            errors.append(f"{name} 必须是非负整数或未设置")
    return errors


def save_config(config: AppConfig, path: Path) -> None:
    """原子写（FR-C01）。AppConfig 中不含任何 Secret 字段（FR-C03）。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    payload = json.dumps(config.to_dict(), ensure_ascii=False, indent=2) + "\n"
    with open(tmp_path, "w", encoding="utf-8") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp_path, path)
    LOGGER.info("config saved path=%s", path)


class ConfigStore:
    """极小的配置存取契约（规格第 12 节）：不扩展成 Repository/Service。"""

    def __init__(self, path: Path):
        self.path = Path(path)

    def load(self) -> tuple[AppConfig, list[str]]:
        return load_config(self.path)

    def save(self, config: AppConfig) -> None:
        save_config(config, self.path)


# ---------------------------------------------------------------------------
# Effective Config（规格第 11 节：Default < User < Environment < Runtime）
# ---------------------------------------------------------------------------


@dataclass
class EffectiveValue:
    value: Any
    source: ConfigSource
    detail: str = ""  # 例如环境变量名

    def __str__(self) -> str:  # UI 直接展示
        label = f"{self.value!r}（来源：{self.source.value}）"
        if self.detail:
            label += f" {self.detail}"
        return label


@dataclass
class EffectiveConfig:
    llm_base_url: EffectiveValue
    llm_model: EffectiveValue
    api_key_env: EffectiveValue
    api_key: str  # 运行期从环境解析，永不持久化（FR-C03）
    external_plugin_dirs: list[tuple[str, ConfigSource]]
    model_dir: EffectiveValue
    disabled_plugin_ids: EffectiveValue
    restore_last_workspace: EffectiveValue
    recent_workspace_limit: EffectiveValue
    recent_activity_limit: EffectiveValue
    llm_configured: bool
    config_errors: list[str] = field(default_factory=list)


def resolve_effective_config(
    user_config: AppConfig | None = None,
    env=None,
    runtime_overrides: dict | None = None,
) -> EffectiveConfig:
    """按 Default < User Config < Environment < Runtime Argument 解析生效配置。

    runtime_overrides 仅用于显式调用方（测试 / CLI），Desktop UI 不使用。

    INT-003：字符串用"非空即已设置"；布尔/整数用 None 哨兵区分
    "未设置"与显式 False / 0——不用 truthy 判断。
    """
    env = os.environ if env is None else env
    user = user_config or AppConfig()
    runtime_overrides = dict(runtime_overrides or {})

    def _resolve_env(field_name: str, env_names: str | tuple | None, parse=str):
        runtime_value = runtime_overrides.get(field_name)
        if runtime_value is not None:
            return EffectiveValue(runtime_value, ConfigSource.RUNTIME)
        if env_names:
            env_names_tuple = (
                (env_names,) if isinstance(env_names, str) else tuple(env_names)
            )
            for env_name in env_names_tuple:
                env_value = (env.get(env_name) or "").strip()
                if env_value:
                    return EffectiveValue(
                        parse(env_value), ConfigSource.ENVIRONMENT, detail=env_name
                    )
        return None

    def _resolve_string(field_name, user_value, env_names, parse=str):
        resolved = _resolve_env(field_name, env_names, parse)
        if resolved is not None:
            return resolved
        if user_value:
            return EffectiveValue(user_value, ConfigSource.USER)
        return EffectiveValue(parse(), ConfigSource.DEFAULT)

    def _resolve_bool(field_name, user_value, default: bool):
        runtime_value = runtime_overrides.get(field_name)
        if runtime_value is not None:
            return EffectiveValue(runtime_value, ConfigSource.RUNTIME)
        if user_value is not None:  # INT-003：显式 False 也是 User Config
            return EffectiveValue(bool(user_value), ConfigSource.USER)
        return EffectiveValue(default, ConfigSource.DEFAULT)

    def _resolve_int(field_name, user_value, default: int):
        runtime_value = runtime_overrides.get(field_name)
        if runtime_value is not None:
            return EffectiveValue(runtime_value, ConfigSource.RUNTIME)
        if user_value is not None:  # INT-003：显式 0 也是 User Config
            return EffectiveValue(int(user_value), ConfigSource.USER)
        return EffectiveValue(default, ConfigSource.DEFAULT)

    def _resolve_string_list(field_name, user_value):
        runtime_value = runtime_overrides.get(field_name)
        if runtime_value is not None:
            return EffectiveValue(list(runtime_value), ConfigSource.RUNTIME)
        if user_value:
            return EffectiveValue(list(user_value), ConfigSource.USER)
        return EffectiveValue([], ConfigSource.DEFAULT)

    llm_base_url = _resolve_string("llm_base_url", user.llm.base_url, ENV_LLM_BASE_URL)
    llm_model = _resolve_string("llm_model", user.llm.model, ENV_LLM_MODEL)
    api_key_env = _resolve_string("api_key_env", user.llm.api_key_env, None)
    model_dir = _resolve_string(
        "model_dir",
        user.paths.model_dir,
        (ENV_MODEL_DIR, LEGACY_ENV_MODEL_DIR),
    )

    api_key = ""
    if api_key_env.value:
        api_key = (env.get(str(api_key_env.value)) or "").strip()

    # 外部插件目录：Config 与 HMBUDDY_PLUGIN_PATH 合并，去重保序（规格第 27 节）
    dir_entries: list[tuple[str, ConfigSource]] = []
    seen: set[str] = set()

    def _add_dir(raw: str, source: ConfigSource):
        normalized = str(Path(raw).expanduser()) if raw else ""
        if not normalized or normalized in seen:
            return
        seen.add(normalized)
        dir_entries.append((normalized, source))

    for item in user.paths.external_plugin_dirs:
        _add_dir(item, ConfigSource.USER)
    env_plugin_path = (env.get(ENV_PLUGIN_PATH) or "").strip()
    if env_plugin_path:
        for item in env_plugin_path.split(os.pathsep):
            _add_dir(item, ConfigSource.ENVIRONMENT)
    for item in runtime_overrides.get("external_plugin_dirs", []) or []:
        _add_dir(item, ConfigSource.RUNTIME)

    disabled = _resolve_string_list(
        "disabled_plugin_ids", user.plugins.disabled_plugin_ids
    )
    restore = _resolve_bool(
        "restore_last_workspace", user.desktop.restore_last_workspace, default=True
    )
    ws_limit = _resolve_int(
        "recent_workspace_limit", user.desktop.recent_workspace_limit, default=10
    )
    activity_limit = _resolve_int(
        "recent_activity_limit", user.desktop.recent_activity_limit, default=20
    )

    llm_configured = bool(
        str(llm_base_url.value).strip() and str(llm_model.value).strip()
    )
    return EffectiveConfig(
        llm_base_url=llm_base_url,
        llm_model=llm_model,
        api_key_env=api_key_env,
        api_key=api_key,
        external_plugin_dirs=dir_entries,
        model_dir=model_dir,
        disabled_plugin_ids=disabled,
        restore_last_workspace=restore,
        recent_workspace_limit=ws_limit,
        recent_activity_limit=activity_limit,
        llm_configured=llm_configured,
        config_errors=[],
    )
