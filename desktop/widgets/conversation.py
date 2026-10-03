"""Conversation Surface（规格 G1 / 第 14-19 节）：中间主工作区。

Header + Message Stream（User / HMBuddy / File Card / Status Notice）+
Composer（Add File / Text Input / Send）。零状态区分有无 Workspace。
QA 复用现有 Artifact QA 链路；Conversation 只是 Presentation Surface。
"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal

from desktop.theme import COLORS
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ..widgets.file_card import FileCard


class ConversationSurface(QWidget):
    send_question = Signal(str)  # 用户问题（active artifact 由 Controller 掌握）
    add_file_requested = Signal()
    file_card_clicked = Signal(object)  # ArtifactRef
    open_workspace_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ---- Header（规格第 14 节：Workspace 名称为主，路径放 Tooltip）----
        header = QWidget()
        header.setObjectName("ConversationHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 10, 16, 10)
        header_column = QVBoxLayout()
        header_column.setSpacing(0)
        self.title_label = QLabel("HMBuddy")
        self.title_label.setObjectName("ConversationTitle")
        self.subtitle_label = QLabel("")
        self.subtitle_label.setObjectName("ConversationSubtitle")
        header_column.addWidget(self.title_label)
        header_column.addWidget(self.subtitle_label)
        header_layout.addLayout(header_column)
        header_layout.addStretch(1)
        layout.addWidget(header)

        # ---- Message Stream / Zero State ----
        self.stream_area = QScrollArea()
        self.stream_area.setObjectName("MessageStream")
        self.stream_area.setWidgetResizable(True)
        self.stream_inner = QWidget()
        self.stream_inner.setObjectName("MessageStream")
        self.stream_layout = QVBoxLayout(self.stream_inner)
        self.stream_layout.setContentsMargins(20, 16, 20, 16)
        self.stream_layout.setSpacing(10)
        self.stream_layout.addStretch(1)
        self.stream_area.setWidget(self.stream_inner)
        layout.addWidget(self.stream_area, 1)

        # 零状态覆盖层（规格第 15 节）
        self.zero_state = self._build_zero_state()
        layout.addWidget(self.zero_state, 1)

        # ---- Composer（规格第 18 节）----
        composer = QFrame()
        composer.setObjectName("Composer")
        composer_layout = QHBoxLayout(composer)
        composer_layout.setContentsMargins(14, 10, 14, 10)
        self.add_file_button = QPushButton("[ + ]")
        self.add_file_button.setToolTip("选择要分析的文件")
        self.add_file_button.clicked.connect(self.add_file_requested.emit)
        self.input = QLineEdit()
        self.input.setObjectName("ComposerInput")
        self.input.setPlaceholderText("输入问题……")
        self.input.returnPressed.connect(self._emit_send)
        self.send_button = QPushButton("Send")
        self.send_button.setObjectName("SendButton")
        self.send_button.clicked.connect(self._emit_send)
        composer_layout.addWidget(self.add_file_button)
        composer_layout.addWidget(self.input, 1)
        composer_layout.addWidget(self.send_button)
        layout.addWidget(composer)

        self.show_zero_state()

    def _build_zero_state(self) -> QWidget:
        container = QWidget()
        container.setObjectName("ZeroState")
        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignCenter)
        self.zero_title = QLabel("HMBuddy")
        self.zero_title.setStyleSheet("font-size: 22px; font-weight: 600;")
        self.zero_title.setAlignment(Qt.AlignCenter)
        self.zero_subtitle = QLabel("选择一个工作区开始")
        self.zero_subtitle.setAlignment(Qt.AlignCenter)
        self.zero_subtitle.setStyleSheet(f"color: {COLORS['muted']};")
        self.zero_button = QPushButton("打开工作区")
        self.zero_button.clicked.connect(self.open_workspace_requested.emit)
        button_row = QHBoxLayout()
        button_row.setAlignment(Qt.AlignCenter)
        button_row.addWidget(self.zero_button)
        layout.addWidget(self.zero_title)
        layout.addWidget(self.zero_subtitle)
        layout.addSpacing(12)
        layout.addLayout(button_row)
        return container

    # ------------------------------------------------------------------
    # 状态渲染
    # ------------------------------------------------------------------

    def show_zero_state(self, has_workspace: bool = False, workspace_name: str = "") -> None:
        """规格第 15 节：Zero State 不显示大面积 System Status Dashboard。"""
        if has_workspace:
            self.zero_title.setText("HMBuddy")
            self.zero_subtitle.setText(f"当前工作区：{workspace_name}\n\n你想查看或分析什么？")
            self.zero_button.setText("选择文件")
        else:
            self.zero_title.setText("HMBuddy")
            self.zero_subtitle.setText("选择一个工作区开始")
            self.zero_button.setText("打开工作区")
        self.zero_state.setVisible(True)
        self.stream_area.setVisible(False)
        self.update_header(workspace_name)

    def show_conversation(self, workspace_name: str = "") -> None:
        self.zero_state.setVisible(False)
        self.stream_area.setVisible(True)
        self.update_header(workspace_name)

    def update_header(self, workspace_name: str = "", artifact_name: str = "") -> None:
        self.title_label.setText(workspace_name or "HMBuddy")
        self.subtitle_label.setText(artifact_name or "")
        self.title_label.setToolTip(workspace_name)

    def set_composer_enabled(self, enabled: bool, placeholder: str | None = None) -> None:
        self.input.setEnabled(enabled)
        self.send_button.setEnabled(enabled)
        if placeholder:
            self.input.setPlaceholderText(placeholder)

    # ------------------------------------------------------------------
    # 消息渲染（规格第 16 节四类 Presentation Item）
    # ------------------------------------------------------------------

    def clear_stream(self) -> None:
        while self.stream_layout.count() > 1:  # 保留末尾 stretch
            item = self.stream_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def add_user_message(self, text: str) -> None:
        bubble = QLabel(text)
        bubble.setObjectName("UserBubble")
        bubble.setWordWrap(True)
        bubble.setMaximumWidth(560)
        bubble.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self._append(bubble)

    def add_assistant_message(self, text: str) -> None:
        bubble = QLabel(text)
        bubble.setObjectName("AssistantBubble")
        bubble.setWordWrap(True)
        bubble.setMaximumWidth(640)
        bubble.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self._append(bubble)

    def add_status_notice(self, text: str, *, error: bool = False) -> None:
        label = QLabel(text)
        label.setObjectName("ErrorNotice" if error else "StatusNotice")
        label.setWordWrap(True)
        self._append(label)

    def add_file_card(self, obj) -> None:
        """接受 ArtifactRef 或 Artifact（Phase 2.2：卡片点击都打开 Preview）。"""
        card = FileCard(obj)
        card.card_clicked.connect(self.file_card_clicked.emit)
        self._append(card)

    # ------------------------------------------------------------------

    def _emit_send(self) -> None:
        question = self.input.text().strip()
        if not question:
            return
        self.input.clear()
        self.send_question.emit(question)

    def _append(self, widget: QWidget) -> None:
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.addWidget(widget, 1)
        self.stream_layout.insertWidget(self.stream_layout.count() - 1, row)
        self._scroll_to_bottom()

    def _wrap(self, layout: QHBoxLayout) -> QWidget:
        row = QWidget()
        row.setLayout(layout)
        self._scroll_to_bottom()
        return row

    def _scroll_to_bottom(self) -> None:
        bar = self.stream_area.verticalScrollBar()
        bar.setValue(bar.maximum())
