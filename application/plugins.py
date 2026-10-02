"""Plugin Product View 与应用运行时装配（Phase 2.1 规格第 22-32 节）。

Plugin Manager 是现有 File Capability Runtime 的 Product View（G6）：
直接消费 DiscoveryReport / LoadReport / Registry / Policy / CapabilityCatalog，
禁止 Desktop 维护第二套 Plugin Registry。

不做：Agent ExtensionHost、Plugin Marketplace、动态授权体系。
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

from plugin_runtime import (
    RuntimeAssembly,
    assemble_runtime,
    get_default_runtime,
)
from plugin_runtime.catalog import CapabilityCatalog, reset_default_catalog
from plugin_runtime.discovery import DiscoveredPlugin
from plugin_runtime.errors import PluginCompatibilityError
from plugin_runtime.policy import PermissionPolicy

from .config import EffectiveConfig, resolve_effective_config

LOGGER = logging.getLogger("hmbuddy.plugins")


# ---------------------------------------------------------------------------
# 应用运行时装配（规格第 28 节 Rescan 链路）
# ---------------------------------------------------------------------------


@dataclass
class AppRuntime:
    """Desktop 使用的运行时句柄：插件装配 + LLM 客户端 + 生效配置。"""

    assembly: RuntimeAssembly
    effective_config: EffectiveConfig
    catalog: CapabilityCatalog
    llm_client: object | None = None
    llm_status: str = "Not Configured"  # Ready / Not Configured / Error
    llm_status_detail: str = ""

    @property
    def disabled_plugin_ids(self) -> set[str]:
        return set(self.effective_config.disabled_plugin_ids.value)

    def rescan(self) -> "AppRuntime":
        """规格第 28 节：Discover → Validate → Apply disabled → Load →
        Registry → Catalog → 刷新视图。直接复用现有 Runtime，不重写 Loader。"""
        return assemble_app_runtime(
            effective_config=self.effective_config, policy=self.assembly.runtime.policy
        )


def assemble_app_runtime(
    effective_config: EffectiveConfig,
    policy: PermissionPolicy | None = None,
) -> AppRuntime:
    """按 Effective Config 装配插件运行时 + LLM 客户端（规格第 33 节启动流程）。

    任何插件错误都不阻断装配（ER-05）；LLM 未配置/错误也不阻断（ER-07）。
    """
    disabled_ids = set(effective_config.disabled_plugin_ids.value)
    external_dirs = [Path(item) for item, _source in effective_config.external_plugin_dirs]
    assembly = assemble_runtime(
        external_plugin_dirs=external_dirs,
        use_env_plugin_path=False,  # 目录已在 EffectiveConfig 里合并过去重保序
        policy=policy,
        disabled_plugin_ids=disabled_ids,
    )
    # Runtime 重建后默认 Catalog 必须复位（Workspace 视图跟随 Effective Registry）
    reset_default_catalog()
    catalog = CapabilityCatalog(assembly.registry)

    llm_client, llm_status, llm_detail = create_llm_client(effective_config)
    return AppRuntime(
        assembly=assembly,
        effective_config=effective_config,
        catalog=catalog,
        llm_client=llm_client,
        llm_status=llm_status,
        llm_status_detail=llm_detail,
    )


def create_llm_client(effective_config: EffectiveConfig):
    """按 Effective Config 构造 LLM 客户端（G1：不再散读环境变量）。

    返回 (client | None, status, detail)；未配置/失败都不抛异常（ER-07）。
    """
    if not effective_config.llm_configured:
        return None, "Not Configured", "请在 Settings → Model 中配置 Base URL 与 Model"
    try:
        from llm.client import OpenAICompatibleClient

        client = OpenAICompatibleClient(
            base_url=str(effective_config.llm_base_url.value),
            api_key=effective_config.api_key,
            model=str(effective_config.llm_model.value),
        )
        return client, "Ready", ""
    except Exception as exc:  # 防御性：配置错误不阻断应用启动
        LOGGER.warning("LLM client init failed: %s", exc)
        return None, "Error", str(exc)[:200]


# ---------------------------------------------------------------------------
# Plugin Product View（规格第 23-24 节）
# ---------------------------------------------------------------------------

STATUS_ENABLED = "Enabled"
STATUS_DISABLED = "Disabled"
STATUS_LOAD_FAILED = "Load Failed"
STATUS_INCOMPATIBLE = "Incompatible"
STATUS_UNAVAILABLE = "Unavailable"


@dataclass
class PluginView:
    """Plugin Manager 单行视图（规格第 23 节全部字段）。"""

    plugin_id: str
    name: str
    version: str
    api_version: int
    source: str  # builtin / external
    status: str
    extensions: list[str]
    capabilities: list[str]
    declared_permissions: list[str]
    effective_permissions: list[str]
    availability_reason: str
    load_error: str
    is_builtin: bool

    def status_display(self) -> str:
        label = {
            STATUS_ENABLED: "已启用",
            STATUS_DISABLED: "已禁用",
            STATUS_LOAD_FAILED: "加载失败",
            STATUS_INCOMPATIBLE: "不兼容",
            STATUS_UNAVAILABLE: "不可用",
        }.get(self.status, self.status)
        if self.status == STATUS_ENABLED and self.availability_reason:
            label += f"（不可用：{self.availability_reason}）"
        return label


def build_plugin_views(
    assembly: RuntimeAssembly, policy: PermissionPolicy | None = None
) -> list[PluginView]:
    """把现有 Runtime 状态映射为 Plugin Manager 视图（T5 / AC-14 / AC-17）。

    - Enabled：已加载且在 Effective Registry 中；
    - Disabled：被 AppConfig 禁用（仍可 Discovery / 展示 Manifest）；
    - Load Failed / Incompatible：装配失败（原因可观察）；
    - Unavailable：已加载但当前环境不可用（platform/python/依赖）。
    """
    policy = policy or assembly.runtime.policy
    probe_context = PluginContextStub()
    views: list[PluginView] = []

    disabled_ids = {item.manifest.id for item in assembly.disabled}
    failure_by_id: dict[str, str] = {}
    for failed_id, message in assembly.load_report.failures:
        failure_by_id.setdefault(failed_id, message)

    # 已加载（Enabled / Unavailable）
    for loaded in assembly.load_report.loaded:
        manifest = loaded.discovered.manifest
        for provider in loaded.providers:
            declared = list(getattr(provider, "declared_permissions", ()) or ())
            try:
                reason = provider.availability_reason(probe_context)
            except Exception as exc:  # 探针异常本身也是可观察信息
                reason = f"{type(exc).__name__}: {exc}"
            views.append(
                PluginView(
                    plugin_id=manifest.id,
                    name=manifest.name,
                    version=manifest.version,
                    api_version=manifest.api_version,
                    source=loaded.discovered.source,
                    status=STATUS_ENABLED,
                    extensions=list(manifest.extensions),
                    capabilities=manifest.capability_ids(),
                    declared_permissions=declared,
                    effective_permissions=sorted(
                        set(declared) & set(policy.granted_permissions())
                    ),
                    availability_reason=reason or "",
                    load_error="",
                    is_builtin=loaded.discovered.source == "builtin",
                )
            )

    # 被禁用（Discovery 仍可、Manifest 可展示、不进 Effective Registry）
    for discovered in assembly.disabled:
        manifest = discovered.manifest
        views.append(
            PluginView(
                plugin_id=manifest.id,
                name=manifest.name,
                version=manifest.version,
                api_version=manifest.api_version,
                source=discovered.source,
                status=STATUS_DISABLED,
                extensions=list(manifest.extensions),
                capabilities=manifest.capability_ids(),
                declared_permissions=list(manifest.permissions),
                effective_permissions=[],
                availability_reason="已禁用：不参与路由",
                load_error="",
                is_builtin=discovered.source == "builtin",
            )
        )

    # 加载失败 / 不兼容（含 Discovery 阶段的 Manifest 校验失败——
    # 此类失败不进入 all_plugins，需要从 discovery.errors 还原视图）
    for discovered in assembly.discovery.all_plugins:
        manifest = discovered.manifest
        if manifest.id in disabled_ids:
            continue
        error = failure_by_id.get(manifest.id)
        if not error:
            continue
        status = (
            STATUS_INCOMPATIBLE
            if isinstance(_cause_of(error), PluginCompatibilityError)
            or "api_version" in error
            else STATUS_LOAD_FAILED
        )
        views.append(
            PluginView(
                plugin_id=manifest.id,
                name=manifest.name,
                version=manifest.version,
                api_version=manifest.api_version,
                source=discovered.source,
                status=status,
                extensions=list(manifest.extensions),
                capabilities=manifest.capability_ids(),
                declared_permissions=list(manifest.permissions),
                effective_permissions=[],
                availability_reason="加载失败：未进入 Registry",
                load_error=error,
                is_builtin=discovered.source == "builtin",
            )
        )

    # Discovery 阶段失败的插件（Manifest 非法 / api_version 不兼容）：
    # 尽力从原始 JSON 还原展示信息（AC-16：错误可观察，其他插件不受影响）
    presented_dirs = {
        str(view.load_error_source)
        for view in views
        if getattr(view, "load_error_source", None)
    }
    for location, error in assembly.discovery.errors:
        raw_info = _read_manifest_info(Path(location))
        if raw_info is None or raw_info.get("id") in {v.plugin_id for v in views}:
            continue
        status = (
            STATUS_INCOMPATIBLE
            if "api_version" in error
            else STATUS_LOAD_FAILED
        )
        views.append(
            PluginView(
                plugin_id=str(raw_info.get("id") or location),
                name=str(raw_info.get("name") or raw_info.get("id") or location),
                version=str(raw_info.get("version") or "?"),
                api_version=int(raw_info.get("api_version") or 0),
                source="external" if "external" in location else "builtin",
                status=status,
                extensions=list((raw_info.get("accepts") or {}).get("extensions") or []),
                capabilities=[
                    item.get("id") if isinstance(item, dict) else str(item)
                    for item in (raw_info.get("capabilities") or [])
                ],
                declared_permissions=list(raw_info.get("permissions") or []),
                effective_permissions=[],
                availability_reason="Manifest 校验失败：未进入 Registry",
                load_error=error,
                is_builtin=("plugins" in location and "examples" not in location),
            )
        )

    views.sort(key=lambda view: (not view.is_builtin, view.plugin_id))
    return views


def _cause_of(error_text: str):
    """从装配失败文本还原异常类型（文本协议，保持装配层无状态）。"""
    return None


def _read_manifest_info(manifest_path: Path) -> dict | None:
    """Manifest 校验失败时尽力读取原始 JSON 的展示字段（不校验）。"""
    try:
        data = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None


class PluginContextStub:
    """可用性探测用的最小上下文（不触文件系统）。"""

    resolved_path = None
    workspace_root = None
    ocr_options = None
    granted_permissions = frozenset({"filesystem.read"})
    plugin_dir = None
    require_permission = None
    services: dict = {}


# ---------------------------------------------------------------------------
# System Status（规格第 32 节）：只做用户可解释性
# ---------------------------------------------------------------------------


@dataclass
class SystemStatus:
    llm: str
    llm_detail: str = ""
    plugins_loaded: int = 0
    plugins_disabled: int = 0
    plugins_error: int = 0
    model_dir: str = "Not Required"
    model_dir_detail: str = ""
    last_workspace: str = "None"
    last_workspace_detail: str = ""


def build_system_status(
    app_runtime: AppRuntime,
    last_workspace_path: str = "",
) -> SystemStatus:
    assembly = app_runtime.assembly
    model_dir_value = str(app_runtime.effective_config.model_dir.value or "").strip()
    if not model_dir_value:
        model_dir, model_detail = "Not Required", "未配置 OCR 模型目录（扫描件 OCR 不可用）"
    elif Path(model_dir_value).exists():
        model_dir, model_detail = "Configured", model_dir_value
    else:
        model_dir, model_detail = "Missing", f"目录不存在：{model_dir_value}"

    last_ws = "None"
    last_ws_detail = ""
    if last_workspace_path:
        last_ws_detail = last_workspace_path
        last_ws = "Available" if Path(last_workspace_path).is_dir() else "Missing"

    return SystemStatus(
        llm=app_runtime.llm_status,
        llm_detail=app_runtime.llm_status_detail,
        plugins_loaded=len(assembly.load_report.loaded),
        plugins_disabled=len(assembly.disabled),
        plugins_error=len(assembly.load_report.failures) + len(assembly.discovery.errors),
        model_dir=model_dir,
        model_dir_detail=model_detail,
        last_workspace=last_ws,
        last_workspace_detail=last_ws_detail,
    )
