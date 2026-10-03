"""Desktop Shell（Phase 2.2 / 规格第 8-9、21、38 节）。

PySide6 三栏布局：Sidebar（导航）+ Center（Conversation / Plugins / Settings
QStackedWidget）+ Preview Pane（默认隐藏，按需打开，Splitter 可调宽）。
未来 Session 加入时：Sidebar 插入会话分区、中间换 Session-backed Conversation、
右侧继续扩展——布局不需要推翻（规格第 38 节）。
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QMainWindow,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from pathlib import Path

from application.state import workspace_entry_for
from desktop.theme import (
    PREVIEW_DEFAULT_WIDTH,
    PREVIEW_MIN_WIDTH,
    SIDEBAR_DEFAULT_WIDTH,
    build_qss,
)
from desktop.widgets.conversation import ConversationSurface
from desktop.widgets.preview.pane import PreviewPane
from desktop.widgets.preview.renderers import build_preview_model
from desktop.widgets.sidebar import Sidebar

PAGE_CONVERSATION = 0
PAGE_PLUGINS = 1
PAGE_SETTINGS = 2


class DesktopShell(QMainWindow):
    """组装三栏布局与页面切换；应用动作全部委托 Controller。"""

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("HMBuddy · 本地办公助手")
        self.resize(1280, 800)
        self.setMinimumSize(1020, 640)
        self.setObjectName("Root")
        self.setStyleSheet(build_qss())

        central = QWidget()
        central.setObjectName("Root")
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)

        # 左 Sidebar + 中间 Stack + 右 Preview（Preview 默认隐藏）
        self.splitter = QSplitter(Qt.Horizontal, central)
        root_layout.addWidget(self.splitter, 1)
        self.setCentralWidget(central)

        self.sidebar = Sidebar(controller)
        self.splitter.addWidget(self.sidebar)

        self.center_stack = QStackedWidget()
        self.splitter.addWidget(self.center_stack)

        from .pages.plugins import PluginsPage
        from .pages.settings import SettingsPage

        self.conversation = ConversationSurface()
        self.plugins_page = PluginsPage(controller)
        self.settings_page = SettingsPage(controller)
        self.center_stack.addWidget(self.conversation)  # PAGE_CONVERSATION
        self.center_stack.addWidget(self.plugins_page)  # PAGE_PLUGINS
        self.center_stack.addWidget(self.settings_page)  # PAGE_SETTINGS

        self.preview_pane = PreviewPane()
        self.splitter.addWidget(self.preview_pane)

        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)
        self.splitter.setCollapsible(2, False)
        self.splitter.setSizes([SIDEBAR_DEFAULT_WIDTH, 800, 0])
        self.preview_pane.setVisible(False)

        self._wire_signals()
        self._setup_shortcuts()
        self.sync_from_controller()

    # ------------------------------------------------------------------
    # 信号接线
    # ------------------------------------------------------------------

    def _wire_signals(self) -> None:
        sidebar = self.sidebar
        sidebar.new_conversation_clicked.connect(self.new_conversation)
        sidebar.workspace_open_requested.connect(self.open_workspace_path)
        sidebar.plugins_open_requested.connect(lambda: self.navigate(PAGE_PLUGINS))
        sidebar.settings_open_requested.connect(lambda: self.navigate(PAGE_SETTINGS))
        sidebar.search_file_selected.connect(self.open_preview_for_ref)
        sidebar.activity_open_requested.connect(self.open_recent_activity)
        sidebar.status_dot_clicked.connect(lambda: self.navigate(PAGE_SETTINGS))

        self.conversation.send_question.connect(self.ask_question)
        self.conversation.add_file_requested.connect(self.choose_file)
        self.conversation.file_card_clicked.connect(self.open_preview_for_ref)
        self.conversation.open_workspace_requested.connect(self.choose_workspace)

        self.preview_pane.close_requested.connect(self.close_preview)

    def _setup_shortcuts(self) -> None:
        QShortcut(QKeySequence("Ctrl+K"), self, self._focus_search)

    def _focus_search(self) -> None:
        self.sidebar.search_input.setFocus()

    # ------------------------------------------------------------------
    # 导航（规格第 21 节轻量机制）
    # ------------------------------------------------------------------

    def navigate(self, page_index: int) -> None:
        self.center_stack.setCurrentIndex(page_index)
        # 规格第 26 节：Plugin / Settings 页在中间主内容区打开，Preview 关闭
        if page_index != PAGE_CONVERSATION:
            self.close_preview()

    # ------------------------------------------------------------------
    # Workspace
    # ------------------------------------------------------------------

    def open_workspace_path(self, raw_path: str) -> None:
        try:
            self.controller.open_workspace(raw_path)
        except (FileNotFoundError, NotADirectoryError, OSError) as exc:
            self.conversation.add_status_notice(f"工作区不可用：{exc}", error=True)
            self.sidebar.refresh()
            return
        self.navigate(PAGE_CONVERSATION)
        self.conversation.clear_stream()
        self.conversation.show_zero_state(
            has_workspace=True,
            workspace_name=self.controller.workspace.root_path.name,
        )
        self.sidebar.refresh()
        self.close_preview()

    def open_recent_activity(self, entry) -> None:
        """Recent Activity 恢复（规格第 37 节）：打开工作区并按需恢复 Artifact。"""
        if not entry.workspace_path:
            return
        try:
            self.controller.open_workspace(entry.workspace_path)
        except (FileNotFoundError, NotADirectoryError, OSError) as exc:
            self.conversation.add_status_notice(f"工作区不可用：{exc}", error=True)
            self.sidebar.refresh()
            return
        self.navigate(PAGE_CONVERSATION)
        self.conversation.clear_stream()
        self.conversation.show_zero_state(
            has_workspace=True,
            workspace_name=self.controller.workspace.root_path.name,
        )
        self.sidebar.refresh()
        if entry.artifact_path and Path(entry.artifact_path).is_file():
            artifact = self.controller.open_ref_from_path(Path(entry.artifact_path))
            self.conversation.add_file_card(artifact)
            self.preview_pane.render(build_preview_model(artifact))
            self.preview_pane.setVisible(True)

    def choose_workspace(self) -> None:
        from PySide6.QtWidgets import QFileDialog

        selected = QFileDialog.getExistingDirectory(self, "选择 HMBuddy 工作目录")
        if selected:
            self.open_workspace_path(selected)

    def choose_file(self) -> None:
        """规格第 18 节 Composer [+]：选择文件并绑定为当前 active Artifact。"""
        from PySide6.QtWidgets import QFileDialog

        extensions = sorted(
            self.controller.app_runtime.catalog.artifact_extensions()
        )
        patterns = " ".join(f"*{ext}" for ext in extensions) or "*.*"
        selected, _selected_filter = QFileDialog.getOpenFileName(
            self, "选择办公文件", "", f"支持的文件 ({patterns});;所有文件 (*.*)"
        )
        if not selected:
            return
        self.open_ref_from_path(Path(selected))

    # ------------------------------------------------------------------
    # Conversation（规格第 14-19 节）
    # ------------------------------------------------------------------

    def new_conversation(self) -> None:
        """规格第 11 节：清空临时 UI 状态，保留当前 Workspace，不建 Session。"""
        self.controller.new_conversation()
        self.conversation.clear_stream()
        if self.controller.workspace is not None:
            self.conversation.show_zero_state(
                has_workspace=True,
                workspace_name=self.controller.workspace.root_path.name,
            )
        self.navigate(PAGE_CONVERSATION)

    def ask_question(self, question: str) -> None:
        """规格第 17 节：QA 复用 Workspace → Ref → Reader → Artifact → LLM。"""
        from PySide6.QtCore import QTimer

        controller = self.controller
        llm_client = controller.app_runtime.llm_client
        if controller.workspace is None:
            self.conversation.add_status_notice("请先选择一个工作区。", error=True)
            return
        if controller.current_artifact is None:
            self.conversation.add_status_notice(
                "请先通过 [ + ] 或搜索选择一个文件，再进行提问。", error=True
            )
            return
        if llm_client is None:
            self.conversation.add_status_notice(
                "模型未配置：请到 设置 → Models 配置 Base URL 与 Model。", error=True
            )
            return

        ref = controller.active_ref
        controller.append_conversation_message("user", question)
        self.conversation.add_user_message(question)
        notice = "正在生成回答……"

        def work():
            return llm_client.ask(controller.current_artifact, question)

        def done(answer: str) -> None:
            controller.append_conversation_message("assistant", answer)
            self.conversation.add_assistant_message(answer)
            controller.record_qa(ref)
            self._set_busy(False)

        self._set_busy(True)
        # Qt 主线程保护：QThread 不可跨线程直接更新 UI，用 QTimer 轮询完成标志
        self._run_background(work, done, notice, QTimer)

    def _run_background(self, work, done, notice: str, QTimer) -> None:
        import threading

        state = {"result": None, "error": None, "done": False}
        self.conversation.add_status_notice(notice)

        def runner():
            try:
                state["result"] = work()
            except Exception as exc:  # UI 边界：后台错误统一内联呈现（规格第 30 节）
                state["error"] = f"{type(exc).__name__}: {exc}"
            state["done"] = True

        threading.Thread(target=runner, daemon=True).start()

        def poll():
            if not state["done"]:
                QTimer.singleShot(120, poll)
                return
            self._set_busy(False)
            if state["error"] is not None:
                self.conversation.add_status_notice(state["error"], error=True)
            else:
                done(state["result"])

        QTimer.singleShot(120, poll)

    def _set_busy(self, busy: bool) -> None:
        self.conversation.send_button.setEnabled(not busy)
        self.conversation.add_file_button.setEnabled(not busy)
        self.conversation.input.setEnabled(not busy)

    # ------------------------------------------------------------------
    # Preview（规格第 20-25 节）
    # ------------------------------------------------------------------

    def open_preview_for_ref(self, ref) -> None:
        """File Card / Search 结果 → Preview；数据一律走 ArtifactReader（规格第 21 节）。"""
        try:
            artifact = self.controller.open_artifact(ref)
        except Exception as exc:
            self.conversation.add_status_notice(f"读取失败：{exc}", error=True)
            return
        controller = self.controller
        controller.active_ref = ref
        self.conversation.update_header(
            workspace_name=(
                controller.workspace.root_path.name if controller.workspace else ""
            ),
            artifact_name=artifact.name,
        )
        self.preview_pane.render(build_preview_model(artifact))
        self.preview_pane.setVisible(True)
        # 恢复 Preview 默认宽度（关闭后重开）
        self.splitter.setSizes([SIDEBAR_DEFAULT_WIDTH, 700, PREVIEW_DEFAULT_WIDTH])

    def close_preview(self) -> None:
        """AC-14：关闭后 Conversation 恢复可用宽度。"""
        self.preview_pane.setVisible(False)

    # ------------------------------------------------------------------
    # 与 Controller 同步
    # ------------------------------------------------------------------

    def sync_from_controller(self) -> None:
        controller = self.controller
        self.sidebar.refresh()
        if controller.workspace is not None:
            self.conversation.show_conversation(
                controller.workspace.root_path.name
            )
            self.conversation.show_zero_state(
                has_workspace=True,
                workspace_name=controller.workspace.root_path.name,
            )
        else:
            self.conversation.show_zero_state(has_workspace=False)
        if controller.current_artifact is not None:
            self.conversation.add_file_card(controller.current_artifact)
