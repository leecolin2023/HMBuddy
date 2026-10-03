"""Preview Pane（规格第 20-25 节）：按需出现的右侧工作面板。

- Header：File Name / File Type / Close；
- Markdown：Qt setMarkdown 阅读视图（不执行脚本、不加载远程资源）；
- TXT：只读文本视图；
- Unsupported：明确区分"可读取"与"可 Preview"。
内容一律来自 Artifact（规格第 21 节硬性边界），不直接读文件。
"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QStackedWidget,
    QTextBrowser,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from .renderers import PreviewModel

INDEX_MARKDOWN = 0
INDEX_TEXT = 1
INDEX_UNSUPPORTED = 2
INDEX_EMPTY = 3


class PreviewPane(QWidget):
    """右侧 Preview 面板：默认隐藏，由 Shell 控制显示/关闭。"""

    close_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PreviewPane")
        self.setMinimumWidth(320)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QWidget()
        header.setObjectName("PreviewHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 8, 8, 8)
        self.title_label = QLabel("Preview")
        self.title_label.setObjectName("ConversationTitle")
        self.type_label = QLabel("")
        self.type_label.setObjectName("ConversationSubtitle")
        close_button = QToolButton()
        close_button.setText("✕")
        close_button.setToolTip("关闭预览")
        close_button.clicked.connect(self.close_requested.emit)
        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.type_label)
        header_layout.addStretch(1)
        header_layout.addWidget(close_button)
        layout.addWidget(header)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)

        # Markdown 阅读视图（Qt Markdown；不自动加载远程资源）
        self.markdown_view = QTextBrowser()
        self.markdown_view.setObjectName("PreviewContent")
        self.markdown_view.setOpenExternalLinks(False)
        self.stack.addWidget(self.markdown_view)

        # TXT 只读视图
        self.text_view = QTextBrowser()
        self.text_view.setObjectName("PreviewContent")
        self.text_view.setOpenExternalLinks(False)
        self.stack.addWidget(self.text_view)

        # Unsupported
        self.unsupported_label = QLabel("")
        self.unsupported_label.setObjectName("PreviewContent")
        self.unsupported_label.setWordWrap(True)
        self.unsupported_label.setAlignment(Qt.AlignTop)
        self.unsupported_label.setContentsMargins(16, 16, 16, 16)
        self.stack.addWidget(self.unsupported_label)

        # Empty
        self.empty_label = QLabel("")
        self.stack.addWidget(self.empty_label)
        self.stack.setCurrentIndex(INDEX_EMPTY)

    def show_empty(self) -> None:
        self.stack.setCurrentIndex(INDEX_EMPTY)

    def render(self, model: PreviewModel) -> None:
        """渲染 PreviewModel（来自 Artifact，规格第 21 节）。"""
        self.title_label.setText(model.name)
        self.type_label.setText(model.artifact_type)
        if not model.supported:
            size_text = f"{model.size} bytes" if model.size else "未知大小"
            self.unsupported_label.setText(
                "当前版本暂不支持此格式的桌面预览。\n\n"
                f"文件：{model.name}\n类型：{model.artifact_type}\n大小：{size_text}\n\n"
                "该格式仍可通过文档问答正常读取与分析。"
            )
            self.stack.setCurrentIndex(INDEX_UNSUPPORTED)
            return
        if model.artifact_type.lower() in ("md", "markdown"):
            self.markdown_view.setMarkdown(model.content)
            self.stack.setCurrentIndex(INDEX_MARKDOWN)
            return
        # TXT：只读、可选中复制、可滚动
        self.text_view.setPlainText(model.content)
        self.stack.setCurrentIndex(INDEX_TEXT)
