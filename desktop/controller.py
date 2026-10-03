"""Desktop Controller（规格第 33/34 节）。

Application Composition Root 的无头核心：组装 config / state / plugin
runtime / llm client，并承载页面共享的应用动作（打开工作区、读取文件、
记录活动、插件启用/禁用/Rescan、Settings 保存）。

Tk 页面只是本 Controller 的薄视图；这样 T8 Desktop Smoke 可以在无 GUI
环境下逐条验证。
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from application.config import (
    AppConfig,
    ConfigStore,
    EffectiveConfig,
    app_config_path,
    app_state_path,
    load_config,
    resolve_effective_config,
    save_config,
)
from application.plugins import (
    AppRuntime,
    PluginView,
    assemble_app_runtime,
    build_plugin_views,
    build_system_status,
)
from application.state import (
    ACTIVITY_ARTIFACT,
    ACTIVITY_ARTIFACT_QA,
    ACTIVITY_WORKSPACE,
    AppState,
    load_state,
    record_activity,
    record_workspace_open,
    save_state,
    sort_recent_workspaces,
)
from services.artifact_reader import ArtifactReader
from workspace.errors import ArtifactRuntimeError
from workspace.workspace import Workspace

LOGGER = logging.getLogger("hmbuddy.desktop")

PAGES = ("home", "workspace", "plugins", "settings")


@dataclass
class WorkspaceSnapshot:
    """Workspace 页面当前数据（页面渲染只消费快照）。"""

    workspace: Workspace
    refs: list


class AppController:
    """组装 + 应用动作。不 import Tk。"""

    def __init__(
        self,
        *,
        config: AppConfig | None = None,
        config_errors: list[str] | None = None,
        state: AppState | None = None,
        state_errors: list[str] | None = None,
        app_runtime: AppRuntime | None = None,
        config_store: ConfigStore | None = None,
        config_path: Path | None = None,
        state_path: Path | None = None,
        env=None,
        effective_config: EffectiveConfig | None = None,
    ):
        self.config = config or AppConfig()
        self.config_errors = list(config_errors or [])
        self.state = state or AppState()
        self.state_errors = list(state_errors or [])
        self.config_store = config_store or ConfigStore(
            config_path or app_config_path()
        )
        self.state_path = state_path or app_state_path()
        # INT-004：Composition Root 只解析一次 Environment Context，
        # 之后所有层（Settings 保存 / Rescan / LLM / 插件目录）都消费这个结果。
        self.env = env
        self.effective_config: EffectiveConfig = (
            effective_config
            or resolve_effective_config(self.config, env=self.env)
        )
        self.app_runtime = app_runtime or assemble_app_runtime(self.effective_config)

        self.reader = ArtifactReader(assembly=self.app_runtime.assembly)
        self.current_page = "home"
        self.workspace: Workspace | None = None
        self.refs: list = []
        self.current_artifact = None

    # ------------------------------------------------------------------
    # 导航（规格第 21 节：current_page + navigate）
    # ------------------------------------------------------------------

    def navigate(self, page: str, payload: dict | None = None) -> None:
        if page not in PAGES:
            raise ValueError(f"unknown page: {page!r}")
        self.current_page = page
        payload = payload or {}
        if page == "workspace" and payload.get("workspace_path"):
            self.state.last_view.workspace_path = str(payload["workspace_path"])
        LOGGER.info("navigate page=%s", page)

    # ------------------------------------------------------------------
    # Workspace / Artifact 动作
    # ------------------------------------------------------------------

    def open_workspace(self, raw_path: str | Path) -> WorkspaceSnapshot:
        """RW-01 Open：validate → Workspace → list artifacts → 更新 Recent → 进入 Workspace 页。

        INT-001：Workspace 必须显式使用当前 AppRuntime 的 Capability Catalog，
        不得回落全局 Default Catalog——Plugin Manager 与 Workspace 只能有一套能力事实。
        """
        workspace = Workspace(
            raw_path, extension_catalog=self.app_runtime.catalog
        )
        refs = workspace.list_artifacts()
        self.workspace = workspace
        self.refs = refs
        self.current_artifact = None
        self.current_page = "workspace"

        limit = int(self.effective_config.recent_workspace_limit.value)
        record_workspace_open(
            self.state,
            str(workspace.root_path),
            limit=limit,
            display_name=workspace.root_path.name,
        )
        record_activity(
            self.state,
            ACTIVITY_WORKSPACE,
            workspace_path=str(workspace.root_path),
            title=workspace.root_path.name,
            resume_view={"page": "workspace"},
            limit=int(self.effective_config.recent_activity_limit.value),
        )
        self.state.last_view.page = "workspace"
        self.state.last_view.workspace_path = str(workspace.root_path)
        self.persist_state()
        return WorkspaceSnapshot(workspace=workspace, refs=refs)

    def open_artifact(self, ref) -> object:
        """读取 Artifact（沿用既有 Runtime）；同时记录 artifact activity。"""
        if self.workspace is None:
            raise RuntimeError("尚未打开工作区")
        artifact = self.reader.read_artifact(ref, workspace=self.workspace)
        self.current_artifact = artifact
        limit = int(self.effective_config.recent_activity_limit.value)
        record_activity(
            self.state,
            ACTIVITY_ARTIFACT,
            workspace_path=str(self.workspace.root_path),
            artifact_path=ref.path,
            title=ref.name,
            resume_view={"page": "workspace", "artifact": ref.path},
            limit=limit,
        )
        self.state.last_view.artifact_path = ref.path
        self.persist_state()
        return artifact

    def record_qa(self, ref) -> None:
        """文档问答活动：只记录导航入口（INT-011：不落问题正文，内网敏感信息不写盘）。"""
        if self.workspace is None:
            return
        artifact_name = ref.name if ref else (self.current_artifact.name if self.current_artifact else "")
        record_activity(
            self.state,
            ACTIVITY_ARTIFACT_QA,
            workspace_path=str(self.workspace.root_path),
            artifact_path=ref.path if ref else "",
            title=f"问答 · {artifact_name}",
            resume_view={"page": "workspace", "artifact": ref.path if ref else ""},
            limit=int(self.effective_config.recent_activity_limit.value),
        )
        self.persist_state()

    # ------------------------------------------------------------------
    # Recent 查询与操作（委托 application.state）
    # ------------------------------------------------------------------

    def recent_workspaces(self):
        return sort_recent_workspaces(self.state)

    def recent_activity(self):
        return list(self.state.recent_activity)

    def pin_workspace(self, path: str, pinned: bool = True) -> None:
        from application.state import pin_workspace as _pin

        _pin(self.state, path, pinned)
        self.persist_state()

    def remove_recent_workspace(self, path: str) -> None:
        from application.state import remove_workspace as _remove

        _remove(self.state, path)
        self.persist_state()

    def clear_recent_workspaces(self) -> None:
        from application.state import clear_recent_workspaces as _clear

        _clear(self.state, keep_pinned=True)
        self.persist_state()

    # ------------------------------------------------------------------
    # Settings / Plugin 管理
    # ------------------------------------------------------------------

    def save_settings(self, new_config: AppConfig) -> None:
        """Settings 保存：立即持久化并按生效策略应用（规格第 31 节）。

        - recent limit / restore：立即生效；
        - plugin dirs / enable-disable：重建 Plugin Runtime；
        - model：重建 LLM Client。
        - INT-001/AC-I02：重建后若已有打开的 Workspace，则以新 Catalog 重建
          Workspace 并刷新文件列表（方案 A，保持 Workspace 不可变倾向）。
        """
        self.config = new_config
        self.config_store.save(new_config)
        self.config_errors = []
        # INT-004：沿用 Composition Root 解析好的 Environment Context
        self.effective_config = resolve_effective_config(self.config, env=self.env)
        old_runtime = self.app_runtime
        self.app_runtime = assemble_app_runtime(
            self.effective_config, policy=old_runtime.assembly.runtime.policy
        )
        self.reader = ArtifactReader(assembly=self.app_runtime.assembly)
        if self.workspace is not None:
            # INT-001 / AC-I02：单一能力事实——打开中的 Workspace 同步新 Catalog
            workspace_root = self.workspace.root_path
            new_workspace = Workspace(
                workspace_root, extension_catalog=self.app_runtime.catalog
            )
            self.workspace = new_workspace
            self.refs = new_workspace.list_artifacts()
        self.persist_state()

    def plugin_views(self) -> list[PluginView]:
        return build_plugin_views(self.app_runtime.assembly, self.app_runtime.assembly.runtime.policy)

    def set_plugin_enabled(self, plugin_id: str, enabled: bool) -> None:
        """AC-15：enable/disable 记录在 AppConfig，不修改 plugin.json。"""
        disabled = list(self.config.plugins.disabled_plugin_ids)
        if enabled and plugin_id in disabled:
            disabled.remove(plugin_id)
        elif not enabled and plugin_id not in disabled:
            disabled.append(plugin_id)
        self.config.plugins.disabled_plugin_ids = disabled
        self.save_settings(self.config)
        LOGGER.info("plugin %s disabled=%s", plugin_id, not enabled)

    def rescan_plugins(self) -> None:
        """规格第 28 节 Rescan：重建 Runtime 并刷新视图。"""
        self.save_settings(self.config)

    def system_status(self):
        last_path = self.state.last_view.workspace_path or (
            self.state.recent_workspaces[0].path if self.state.recent_workspaces else ""
        )
        return build_system_status(self.app_runtime, last_path)

    # ------------------------------------------------------------------

    def persist_state(self) -> None:
        try:
            save_state(self.state, self.state_path)
        except OSError as exc:  # ER：保存失败不影响内存状态
            LOGGER.error("state save failed: %s", exc)
            self.state_errors.append(f"state 保存失败：{exc}")


def bootstrap_controller(
    *,
    config_path: Path | None = None,
    state_path: Path | None = None,
    env=None,
) -> AppController:
    """规格第 33 节启动流程：Resolve Paths → Load Config → Effective →
    Load State → Assemble Runtime → LLM Client → Controller。

    INT-004：显式 env 在此处一次性解析进 EffectiveConfig，
    Controller 与其下游全部消费同一 Environment Context。
    Config / State / 插件 / LLM 问题都不阻断启动（规格第 33 节）。
    """
    resolved_config_path = config_path or app_config_path(env)
    resolved_state_path = state_path or app_state_path(env)
    config, config_errors = load_config(resolved_config_path, env)
    state, state_errors = load_state(resolved_state_path)
    effective_config = resolve_effective_config(config, env=env)
    controller = AppController(
        config=config,
        config_errors=config_errors,
        state=state,
        state_errors=state_errors,
        config_path=resolved_config_path,
        state_path=resolved_state_path,
        env=env,
        effective_config=effective_config,
    )
    if config_errors:
        LOGGER.warning("config errors: %s", config_errors)
    if state_errors:
        LOGGER.warning("state errors: %s", state_errors)
    return controller
