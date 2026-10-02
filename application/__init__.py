"""HMBuddy Application Layer（Phase 2.1）。

产品应用基础模块：AppConfig / AppState / Recent / Plugin Product View。
按规格第 7 节，这些是"简单应用逻辑模块"，不是 Kernel Primitive——
不引入 Session / TaskEngine / AgentLoop / ToolRegistry / ExtensionHost。
"""
from .config import (
    AppConfig,
    ConfigSource,
    ConfigStore,
    EffectiveConfig,
    app_config_path,
    app_data_dir,
    app_logs_dir,
    app_state_path,
    load_config,
    resolve_effective_config,
    save_config,
    validate_config,
)
from .state import AppState, LastView, load_state, save_state
from .recent import RecentActivityEntry, RecentWorkspace
from .plugins import (
    AppRuntime,
    PluginView,
    assemble_app_runtime,
    build_plugin_views,
    build_system_status,
    create_llm_client,
)

__all__ = [
    "AppConfig",
    "ConfigSource",
    "ConfigStore",
    "EffectiveConfig",
    "app_data_dir",
    "app_config_path",
    "app_state_path",
    "app_logs_dir",
    "load_config",
    "save_config",
    "resolve_effective_config",
    "validate_config",
    "AppState",
    "LastView",
    "load_state",
    "save_state",
    "RecentWorkspace",
    "RecentActivityEntry",
    "AppRuntime",
    "PluginView",
    "assemble_app_runtime",
    "build_plugin_views",
    "build_system_status",
    "create_llm_client",
]
