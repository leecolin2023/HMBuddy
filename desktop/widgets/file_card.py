"""File Card（规格第 19 节）：会话中可点击的 Artifact 对象。"""
from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from desktop.theme import COLORS


class FileCard(QFrame):
    """显示 文件名 + 类型·大小，点击打开右侧 Preview（规格第 19 节）。"""

    card_clicked = Signal(object)  # ArtifactRef

    def __init__(self, ref, parent=None):
        super().__init__(parent)
        self.ref = ref
        self.setObjectName("FileCard")
        self.setCursor(self.cursor().shape())  # keep default; clickable via mouse press

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self.name_label = QLabel(ref.name)
        self.name_label.setObjectName("FileCardName")
        type_size = _type_size_text(ref)
        self.meta_label = QLabel(type_size)
        self.meta_label.setObjectName("FileCardMeta")

        layout.addWidget(self.name_label)
        layout.addWidget(self.meta_label)

    def mousePressEvent(self, event) -> None:  # noqa: N802 (Qt 命名约定)
        self.card_clicked.emit(self.ref)
        super().mousePressEvent(event)


def _type_size_text(obj) -> str:
    size = getattr(obj, "size", None)
    if size is None:
        size = (getattr(obj, "provenance", None) or {}).get("file_size", 0)
    if size >= 1024 * 1024:
        size_text = f"{size / 1024 / 1024:.1f} MB"
    elif size >= 1024:
        size_text = f"{size / 1024:.0f} KB"
    else:
        size_text = f"{size} B"
    return f"{getattr(obj, 'artifact_type', '').upper()} · {size_text}"
