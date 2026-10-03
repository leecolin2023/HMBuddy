"""Sidebar（规格 G2 / 第 10 节）：工作导航。

品牌区 + 新建会话 + 搜索 + 工作区列表（Pinned→Recent）+ 插件 + 设置 +
底部极简 Status Dot。不固定显示 Home / Workspace 一级功能按钮（AC-05）。
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from desktop.theme import SIDEBAR_DEFAULT_WIDTH, SIDEBAR_MAX_WIDTH, SIDEBAR_MIN_WIDTH


class Sidebar(QFrame):
    new_conversation_clicked = Signal()
    workspace_open_requested = Signal(str)  # workspace path
    plugins_open_requested = Signal()
    settings_open_requested = Signal()
    search_changed = Signal(str)
    search_file_selected = Signal(object)  # ArtifactRef
    activity_open_requested = Signal(object)  # RecentActivityEntry
    status_dot_clicked = Signal()

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setObjectName("Sidebar")
        self.setFixedWidth(SIDEBAR_DEFAULT_WIDTH)
        self.setMinimumWidth(SIDEBAR_MIN_WIDTH)
        self.setMaximumWidth(SIDEBAR_MAX_WIDTH)

        # INT-006：稳定 id / 路径映射
        self._workspace_rows: dict[str, object] = {}
        self._search_rows: dict[str, dict] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 12, 10, 10)
        layout.setSpacing(8)

        brand = QLabel("HMBuddy")
        brand.setObjectName("BrandLabel")
        layout.addWidget(brand)

        self.new_chat_button = QPushButton("+ 新建会话")
        self.new_chat_button.setObjectName("SidebarButton")
        self.new_chat_button.clicked.connect(self.new_conversation_clicked.emit)
        layout.addWidget(self.new_chat_button)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索（Ctrl+K）")
        self.search_input.textChanged.connect(self._on_search_changed)
        layout.addWidget(self.search_input)

        self.search_results = QListWidget()
        self.search_results.setVisible(False)
        self.search_results.itemClicked.connect(self._on_search_result_clicked)
        layout.addWidget(self.search_results, 1)
        # INT-006：选择映射通过 item UserRole payload 显式承载（不依赖 index）

        section = QLabel("工作区")
        section.setObjectName("SidebarSectionLabel")
        layout.addWidget(section)

        self.workspace_list = QListWidget()
        self.workspace_list.itemClicked.connect(self._on_workspace_clicked)
        layout.addWidget(self.workspace_list, 2)

        plugins_button = QPushButton("插件")
        plugins_button.setObjectName("SidebarButton")
        plugins_button.clicked.connect(self.plugins_open_requested.emit)
        layout.addWidget(plugins_button)

        settings_button = QPushButton("设置")
        settings_button.setObjectName("SidebarButton")
        settings_button.clicked.connect(self.settings_open_requested.emit)
        layout.addWidget(settings_button)

        layout.addStretch(1)
        self.status_dot = QLabel("●")
        self.status_dot.setObjectName("StatusDotLabel")
        self.status_dot.setCursor(Qt.PointingHandCursor)
        self.status_dot.mousePressEvent = lambda _event: self.status_dot_clicked.emit()
        layout.addWidget(self.status_dot)

        self.refresh()

    # ------------------------------------------------------------------

    def refresh(self) -> None:
        self.refresh_workspaces()
        self.refresh_status()

    def refresh_workspaces(self) -> None:
        """规格第 13 节：每行只突出 Display Name；Missing 标记；
        详细信息走 Tooltip；排序复用 Pinned → Last Opened Desc。"""
        self.workspace_list.clear()
        self._workspace_rows.clear()
        for entry in self.controller.recent_workspaces():
            missing = not Path(entry.path).is_dir()
            label = ("[Missing] " if missing else "") + (
                entry.display_name or entry.path
            )
            item = QListWidgetItem(("📌 " if entry.pinned else "") + label)
            item.setToolTip(
                f"{entry.path}\n最近打开：{entry.last_opened_at[:19].replace('T', ' ')}"
                + ("\n路径缺失：可移除后重新打开以重新定位" if missing else "")
            )
            item.setData(Qt.UserRole, entry.path)
            self.workspace_list.addItem(item)
            self._workspace_rows[entry.workspace_id] = entry

    def refresh_status(self) -> None:
        status = self.controller.system_status()
        if status.llm == "Ready":
            color, text = "#2e8b57", "● Ready"
        elif status.llm == "Error":
            color, text = "#b3403a", "● LLM Error"
        else:
            color, text = "#c47f17", "● LLM 未配置"
        if status.plugins_error:
            text += f" · 插件错误 {status.plugins_error}"
        self.status_dot.setText(text)
        self.status_dot.setStyleSheet(f"color: {color}; background: transparent;")

    # ------------------------------------------------------------------

    def _on_workspace_clicked(self, item: QListWidgetItem) -> None:
        path = item.data(Qt.UserRole)
        if path:
            self.workspace_open_requested.emit(path)

    def _on_search_changed(self, text: str) -> None:
        """规格第 12 节：按 工作区 / 当前工作区文件 / 最近活动 分组展示；
        只匹配名称与路径元数据，不读取文件正文。"""
        query = (text or "").strip()
        if not query:
            self.search_results.setVisible(False)
            self.search_results.clear()
            self._search_rows.clear()
            return

        results = self.controller.search(query)
        self.search_results.clear()
        def add_section(title: str) -> None:
            section_item = QListWidgetItem(title)
            section_item.setFlags(section_item.flags() & ~Qt.ItemIsSelectable)
            self.search_results.addItem(section_item)

        def add_row(label: str, payload: dict) -> None:
            item = QListWidgetItem(label)
            # INT-006：UserRole 直接承载稳定 payload（entry_id / path / ref），
            # 选择映射不依赖 list index
            item.setData(Qt.UserRole, payload)
            self.search_results.addItem(item)

        if results["workspaces"]:
            add_section("工作区")
            for entry in results["workspaces"]:
                add_row(
                    entry.display_name or entry.path,
                    {"kind": "workspace", "path": entry.path},
                )
        if results["files"]:
            add_section("当前工作区文件")
            for ref in results["files"][:20]:
                add_row(
                    f"{ref.name}（{ref.artifact_type.upper()}）",
                    {"kind": "file", "ref": ref},
                )
        if results["activity"]:
            add_section("最近活动")
            for entry in results["activity"][:10]:
                add_row(entry.title or "（无标题）", {"kind": "activity", "entry": entry})
        # INT-006：稳定 entry_id 映射（不依赖 list index / Tk 自动 iid）

        has_rows = bool(
            results["workspaces"] or results["files"] or results["activity"]
        )
        self.search_results.setVisible(has_rows)

    def _on_search_result_clicked(self, item: QListWidgetItem) -> None:
        payload = item.data(Qt.UserRole) or {}
        kind = payload.get("kind")
        if kind == "workspace":
            self.search_results.setVisible(False)
            self.search_input.clear()
            self.workspace_open_requested.emit(payload["path"])
        elif kind == "file":
            self.search_results.setVisible(False)
            self.search_input.clear()
            self.search_file_selected.emit(payload["ref"])
        elif kind == "activity":
            self.search_results.setVisible(False)
            self.search_input.clear()
            self.activity_open_requested.emit(payload["entry"])
