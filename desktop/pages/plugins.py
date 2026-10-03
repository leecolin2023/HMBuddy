"""Plugins 页（Phase 2.2 / 规格第 26 节）：Card / Rich List Row 重设计。

复用现有 Plugin Runtime 视图（build_plugin_views），只重构 Presentation。
主表一 Plugin 一行；Provider / Directory / Manifest / Priority 进详情。
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class PluginsPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setObjectName("PageContainer")
        self.selected_plugin_id: str | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title_column = QVBoxLayout()
        title = QLabel("插件")
        title.setObjectName("SectionTitle")
        subtitle = QLabel(
            "File Capability Runtime 的产品视图；启用/禁用记录在应用配置，不修改插件文件。"
        )
        subtitle.setObjectName("CardMeta")
        title_column.addWidget(title)
        title_column.addWidget(subtitle)
        header.addLayout(title_column, 1)
        self.rescan_button = QPushButton("重新扫描")
        self.rescan_button.clicked.connect(self.rescan)
        header.addWidget(self.rescan_button)
        layout.addLayout(header)

        self.cards_area = QScrollArea()
        self.cards_area.setWidgetResizable(True)
        self.cards_inner = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_inner)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(8)
        self.cards_layout.addStretch(1)
        self.cards_area.setWidget(self.cards_inner)
        layout.addWidget(self.cards_area, 1)

        self.detail_label = QLabel("")
        self.detail_label.setObjectName("CardMeta")
        self.detail_label.setWordWrap(True)
        self.detail_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(self.detail_label)

        self.refresh()

    # ------------------------------------------------------------------

    def refresh(self) -> None:
        self.views = self.controller.plugin_views()
        while self.cards_layout.count() > 1:
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        for view in self.views:
            card = self._build_card(view)
            self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)

    def _build_card(self, view) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        card.setCursor(Qt.PointingHandCursor)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(4, 4, 4, 4)
        card_layout.setSpacing(4)

        top = QHBoxLayout()
        name_label = QLabel(view.name)
        name_label.setObjectName("CardTitle")
        status_badge = QLabel(view.status_display())
        status_badge.setObjectName(
            "Badge" if view.status in ("Enabled", "Disabled") else "BadgeError"
        )
        top.addWidget(name_label)
        top.addStretch(1)
        top.addWidget(status_badge)
        card_layout.addLayout(top)

        meta_bits = []
        if view.load_error:
            meta_bits.append(f"错误：{view.load_error}")
        else:
            meta_bits.append("格式：" + (" ".join(view.extensions) or "-"))
            meta_bits.append("能力：" + (" ".join(view.capabilities) or "-"))
            meta_bits.append("来源：" + ("内置" if view.is_builtin else "外部"))
        meta = QLabel(" · ".join(meta_bits))
        meta.setObjectName("CardMeta")
        meta.setWordWrap(True)
        card_layout.addWidget(meta)

        actions = QHBoxLayout()
        toggle_text = "启用" if view.status == "Disabled" else "禁用"
        toggle_button = QPushButton(toggle_text)
        toggle_button.clicked.connect(
            lambda _checked=False, pid=view.plugin_id, enable=view.status == "Disabled":
            self.set_enabled(pid, enable)
        )
        actions.addWidget(toggle_button)
        detail_button = QPushButton("详情")
        detail_button.clicked.connect(
            lambda _checked=False, pid=view.plugin_id: self.show_detail(pid)
        )
        actions.addWidget(detail_button)
        actions.addStretch(1)
        card_layout.addLayout(actions)

        card.mousePressEvent = lambda _event, pid=view.plugin_id: self.show_detail(pid)
        return card

    # ------------------------------------------------------------------

    def show_detail(self, plugin_id: str) -> None:
        self.selected_plugin_id = plugin_id
        view = next((v for v in self.views if v.plugin_id == plugin_id), None)
        if view is None:
            return
        lines = [
            f"Plugin ID：{view.plugin_id}",
            f"Version：{view.version} · API v{view.api_version} · 来源：{'内置' if view.is_builtin else '外部'}",
            f"状态：{view.status_display()}",
            f"能力：{'、'.join(view.capabilities) or '-'}",
            f"扩展名：{' '.join(view.extensions) or '-'}",
            f"声明权限：{'、'.join(view.declared_permissions) or '-'}",
            f"生效权限：{'、'.join(view.effective_permissions) or '-'}",
        ]
        if view.providers:
            lines.append(f"Providers（{len(view.providers)}）：")
            for provider in view.providers:
                state = "可用" if provider.available else f"不可用：{provider.availability_reason}"
                lines.append(
                    f"  · {provider.provider_id}（priority={provider.priority}，{state}）"
                )
        if view.load_error:
            lines.append(f"加载错误：{view.load_error}")
        self.detail_label.setText("\n".join(lines))

    def set_enabled(self, plugin_id: str, enabled: bool) -> None:
        if not enabled:
            view = next((v for v in self.views if v.plugin_id == plugin_id), None)
            if view is not None and view.is_builtin:
                # 规格第 26 节：允许禁用内置插件，但必须提示影响
                from PySide6.QtWidgets import QMessageBox

                confirm = QMessageBox.question(
                    self,
                    "禁用内置插件",
                    f"禁用 {view.name} 后，当前 Runtime 可能失去 "
                    f"{', '.join(view.extensions) or plugin_id} 的读取能力。确定继续？",
                )
                if confirm != QMessageBox.Yes:
                    return
        self.controller.set_plugin_enabled(plugin_id, enabled)
        self.refresh()

    def rescan(self) -> None:
        self.controller.rescan_plugins()
        self.refresh()
