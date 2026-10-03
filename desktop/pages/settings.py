"""Settings 页（Phase 2.2 / 规格第 27-28 节）：左侧分类导航 + 右侧内容区。

分类：General / Models / File Processing / Plugins / Advanced。
Effective Config Source 可解释性保留（AC-22 / 规格 28 节）。
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from application.config import AppConfig, ConfigSource


class SettingsPage(QWidget):
    CATEGORIES = ("General", "Models", "File Processing", "Plugins", "Advanced")

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setObjectName("PageContainer")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        title = QLabel("设置")
        title.setObjectName("SectionTitle")
        layout.addWidget(title)

        body = QHBoxLayout()
        layout.addLayout(body, 1)

        self.category_list = QListWidget()
        self.category_list.setFixedWidth(180)
        for category in self.CATEGORIES:
            self.category_list.addItem(QListWidgetItem(category))
        self.category_list.currentRowChanged.connect(self._on_category_changed)
        body.addWidget(self.category_list)

        self.content_stack = QStackedWidget()
        body.addWidget(self.content_stack, 1)

        self.content_stack.addWidget(self._build_general())          # 0
        self.content_stack.addWidget(self._build_models())           # 1
        self.content_stack.addWidget(self._build_file_processing())  # 2
        self.content_stack.addWidget(self._build_plugins())          # 3
        self.content_stack.addWidget(self._build_advanced())         # 4

        save_row = QHBoxLayout()
        save_button = QPushButton("保存并应用")
        save_button.clicked.connect(self.save)
        save_row.addWidget(save_button)
        save_row.addStretch(1)
        layout.addLayout(save_row)

        self.category_list.setCurrentRow(0)
        self._load_values()

    # ------------------------------------------------------------------
    # 各分类表单
    # ------------------------------------------------------------------

    def _build_general(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(8, 0, 0, 0)
        layout.setSpacing(8)
        self.restore_var = _make_checkbox("启动时恢复最近工作区")
        layout.addWidget(self.restore_var)
        ws_row, self.ws_limit_input = _make_int_row("Recent Workspace 数量上限")
        layout.addLayout(ws_row)
        activity_row, self.activity_limit_input = _make_int_row(
            "Recent Activity 数量上限"
        )
        layout.addLayout(activity_row)
        layout.addStretch(1)
        return page

    def _build_models(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(8, 0, 0, 0)
        layout.setSpacing(8)
        effective = self.controller.effective_config

        self.base_url_input = QLineEdit(str(effective.llm_base_url.value))
        layout.addWidget(_make_labeled("Base URL", self.base_url_input, effective.llm_base_url))
        self.model_input = QLineEdit(str(effective.llm_model.value))
        layout.addWidget(_make_labeled("Model", self.model_input, effective.llm_model))
        self.api_key_env_input = QLineEdit(str(effective.api_key_env.value))
        layout.addWidget(
            _make_labeled(
                "API Key 环境变量（不保存明文密钥）",
                self.api_key_env_input,
                effective.api_key_env,
            )
        )
        status = QLabel(
            f"当前状态：{self.controller.app_runtime.llm_status}"
            + (
                f"（{self.controller.app_runtime.llm_status_detail}）"
                if self.controller.app_runtime.llm_status_detail
                else ""
            )
        )
        status.setObjectName("CardMeta")
        layout.addWidget(status)
        layout.addStretch(1)
        return page

    def _build_file_processing(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(8, 0, 0, 0)
        layout.setSpacing(8)
        effective = self.controller.effective_config
        self.model_dir_input = QLineEdit(str(effective.model_dir.value))
        layout.addWidget(_make_labeled("OCR 模型目录", self.model_dir_input, effective.model_dir))

        extensions = sorted(
            self.controller.app_runtime.catalog.artifact_extensions()
        )
        capability_note = QLabel(
            "当前文件能力扩展名：" + (" ".join(extensions) or "-")
            + "\n（由 Capability Catalog 派生，安装新插件后自动更新）"
        )
        capability_note.setObjectName("CardMeta")
        capability_note.setWordWrap(True)
        layout.addWidget(capability_note)
        layout.addStretch(1)
        return page

    def _build_plugins(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(8, 0, 0, 0)
        layout.setSpacing(8)
        effective = self.controller.effective_config
        info = QLabel("外部插件目录：")
        layout.addWidget(info)
        for path, source in effective.external_plugin_dirs:
            row = QLabel(f"  · {path}（{source.value}）")
            row.setObjectName("CardMeta")
            layout.addWidget(row)
        if not effective.external_plugin_dirs:
            empty = QLabel("  · （未配置）")
            empty.setObjectName("CardMeta")
            layout.addWidget(empty)
        note = QLabel(
            "目录来源为 Environment 时不能在 UI 删除；增删外部插件目录请编辑 "
            "config.json 的 paths.external_plugin_dirs 或环境变量 "
            "HMBUDDY_PLUGIN_PATH 后 Rescan。"
        )
        note.setObjectName("CardMeta")
        note.setWordWrap(True)
        layout.addWidget(note)
        rescan_button = QPushButton("重新扫描插件")
        rescan_button.clicked.connect(self._rescan)
        layout.addWidget(rescan_button)
        open_plugins = QPushButton("打开插件管理")
        open_plugins.clicked.connect(self._open_plugins)
        layout.addWidget(open_plugins)
        layout.addStretch(1)
        return page

    def _build_advanced(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(8, 0, 0, 0)
        layout.setSpacing(8)
        lines = [
            f"Config Path：{self.controller.config_store.path}",
            f"State Path：{self.controller.state_path}",
        ]
        effective = self.controller.effective_config
        if effective.llm_model.source is ConfigSource.ENVIRONMENT:
            lines.append(
                f"环境覆盖：HMBUDDY_LLM_MODEL={effective.llm_model.value}"
                "（UI 修改 config.json 不会改变当前 Effective Value）"
            )
        if self.controller.config_errors:
            lines.append("Config 错误：")
            lines.extend(f"  · {item}" for item in self.controller.config_errors)
        info = QLabel("\n".join(lines))
        info.setObjectName("CardMeta")
        info.setWordWrap(True)
        info.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(info)
        layout.addStretch(1)
        return page

    # ------------------------------------------------------------------

    def _on_category_changed(self, row: int) -> None:
        self.content_stack.setCurrentIndex(max(row, 0))

    def _load_values(self) -> None:
        controller = self.controller
        effective = controller.effective_config
        self.restore_var.setChecked(bool(effective.restore_last_workspace.value))
        self.ws_limit_input.setText(str(int(effective.recent_workspace_limit.value)))
        self.activity_limit_input.setText(
            str(int(effective.recent_activity_limit.value))
        )

    def save(self) -> None:
        try:
            ws_limit = max(int(self.ws_limit_input.text().strip() or 10), 0)
            activity_limit = max(
                int(self.activity_limit_input.text().strip() or 20), 0
            )
        except ValueError:
            QMessageBox.warning(self, "输入无效", "数量上限必须是整数。")
            return
        config = self.controller.config
        config.desktop.restore_last_workspace = bool(self.restore_var.isChecked())
        config.desktop.recent_workspace_limit = ws_limit
        config.desktop.recent_activity_limit = activity_limit
        config.llm.base_url = self.base_url_input.text().strip()
        config.llm.model = self.model_input.text().strip()
        config.llm.api_key_env = self.api_key_env_input.text().strip() or "HMBUDDY_LLM_API_KEY"
        config.paths.model_dir = self.model_dir_input.text().strip()
        # external_plugin_dirs / disabled_plugin_ids 由 Plugins 管理保留
        self.controller.save_settings(config)
        self._load_values()
        QMessageBox.information(self, "已保存", "设置已保存并应用（写入 config.json）。")

    def _rescan(self) -> None:
        self.controller.rescan_plugins()
        self._load_values()
        QMessageBox.information(self, "Rescan 完成", "已按当前配置重新发现并加载插件。")

    def _open_plugins(self) -> None:
        """跳转 Plugins 管理（由 Shell 完成：切回 Conversation 顶部导航）。"""
        window = self.window()
        if hasattr(window, "navigate"):
            window.navigate(1)  # PluginsPage


def _make_labeled(label: str, editor: QWidget, effective_value) -> QWidget:
    container = QWidget()
    layout = QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(2)
    row = QHBoxLayout()
    caption = QLabel(label)
    caption.setMinimumWidth(180)
    row.addWidget(caption)
    row.addWidget(editor, 1)
    layout.addLayout(row)
    source_text = f"来源：{effective_value.source.value}"
    if effective_value.detail:
        source_text += f"（{effective_value.detail}）"
    source_label = QLabel(source_text)
    source_label.setObjectName("CardMeta")
    source_row = QHBoxLayout()
    source_row.addSpacing(180)
    source_row.addWidget(source_label, 1)
    layout.addLayout(source_row)
    return container


def _make_checkbox(label: str):
    from PySide6.QtWidgets import QCheckBox

    return QCheckBox(label)


def _make_int_row(label: str) -> tuple[QHBoxLayout, QLineEdit]:
    row = QHBoxLayout()
    caption = QLabel(label)
    caption.setMinimumWidth(180)
    row.addWidget(caption)
    editor = QLineEdit()
    row.addWidget(editor)
    row.addStretch(1)
    return row, editor
