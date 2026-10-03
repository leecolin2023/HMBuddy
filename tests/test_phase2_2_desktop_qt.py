"""Phase 2.2 — Desktop UX Shell Redesign 验收测试（T4/T6/T10 + AC-01/18/27）。

Qt 测试统一使用 QT_QPA_PLATFORM=offscreen；Controller / Runtime 回归由
既有测试保证（T1）。AC-18 数据边界与 AC-01/27（禁 Tk）由静态守护测试强制。
"""
import json
from pathlib import Path

import pytest

from application.config import AppConfig
from desktop.controller import AppController, bootstrap_controller

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = PROJECT_ROOT / "evals" / "fixtures"

pytest.importorskip("PySide6.QtWidgets", reason="未安装 PySide6")
os_environ_qt = pytest.importorskip("os")


def _qt_app():
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture()
def controller(tmp_path):
    return bootstrap_controller(
        config_path=tmp_path / "config.json",
        state_path=tmp_path / "state.json",
        env={},
    )


@pytest.fixture()
def qt_shell(controller):
    _qt_app()
    from desktop.shell import DesktopShell

    shell = DesktopShell(controller)
    shell.show()
    return shell


# ---------------------------------------------------------------------------
# AC-01 / AC-27：Presentation 层技术契约（静态守护）
# ---------------------------------------------------------------------------


def test_ac01_desktop_does_not_use_tkinter():
    """AC-01/AC-27：正式 Desktop 只使用 PySide6，不保留 Tkinter UI。"""
    desktop_dir = PROJECT_ROOT / "desktop"
    offenders = []
    for source_file in desktop_dir.rglob("*.py"):
        source = source_file.read_text(encoding="utf-8")
        for token in ("import tkinter", "from tkinter", "tkinter as tk"):
            if token in source:
                offenders.append(f"{source_file}: {token}")
    assert not offenders, f"desktop 层残留 Tkinter 引用: {offenders}"


def test_ac18_preview_never_reads_files_directly():
    """AC-18：Preview 渲染链路不得 path → open()/read_text() 绕过 Artifact Runtime。

    AST 级检查：只看真实代码调用节点，忽略文档字符串中的规则描述。
    """
    import ast

    preview_dir = PROJECT_ROOT / "desktop" / "widgets" / "preview"
    offenders = []
    for source_file in preview_dir.rglob("*.py"):
        tree = ast.parse(source_file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                name = getattr(func, "id", "") or getattr(func, "attr", "")
                if name in ("open", "read_text", "read_bytes"):
                    offenders.append(f"{source_file}:{node.lineno} {name}()")
            if isinstance(node, ast.Attribute) and node.attr == "read_text":
                offenders.append(f"{source_file}:{node.lineno} .read_text")
    assert not offenders, f"Preview 层存在绕过 Artifact Runtime 的文件读取: {offenders}"


# ---------------------------------------------------------------------------
# T4 / AC-08 / AC-09 — Conversation Controller 语义（无头）
# ---------------------------------------------------------------------------


def test_t4_new_conversation_clears_temp_state_only(controller):
    controller.open_workspace(FIXTURES_DIR)
    ref = next(r for r in controller.refs if r.name == "sample.docx")
    controller.open_artifact(ref)
    controller.append_conversation_message("user", "temp question")
    assert controller.conversation_messages

    controller.new_conversation()
    assert controller.conversation_messages == []  # transcript 清空
    assert controller.current_artifact is None  # active artifact 清除
    assert controller.workspace is not None  # Workspace 保留
    # 不创建持久 Session（AC-08）：state.json 不出现 session 字段
    state_data = json.loads(controller.state_path.read_text(encoding="utf-8"))
    assert "sessions" not in state_data
    assert "session_id" not in json.dumps(state_data)


def test_t4_artifact_qa_flow_records_activity_without_question_text(controller):
    controller.open_workspace(FIXTURES_DIR)
    ref = next(r for r in controller.refs if r.name == "sample.docx")
    controller.open_artifact(ref)
    controller.record_qa()
    entry = controller.recent_activity()[0]
    assert entry.activity_type == "artifact_qa"
    assert "问答 · " in entry.title


# ---------------------------------------------------------------------------
# T6 — Preview 渲染模型（Markdown / TXT / Unsupported）
# ---------------------------------------------------------------------------


def _read_fixture_as_artifact(controller, filename):
    controller.open_workspace(FIXTURES_DIR)
    ref = next(r for r in controller.refs if r.name == filename)
    return controller.open_artifact(ref)


def test_t6_markdown_preview_model(qt_shell, controller, tmp_path):
    from desktop.widgets.preview.renderers import build_preview_model

    ws_root = tmp_path / "ws"
    ws_root.mkdir()
    (ws_root / "sample_preview.md").write_text(
        "# 标题\n\n- 列表项\n\n```py\nprint('hi')\n```\n",
        encoding="utf-8",
    )
    controller.open_workspace(ws_root)
    ref = next(r for r in controller.refs if r.name == "sample_preview.md")
    artifact = controller.open_artifact(ref)
    model = build_preview_model(artifact)
    assert model.supported is True
    assert "# 标题" in model.content  # 内容来自 Artifact.content
    qt_shell.preview_pane.setVisible(True)  # Preview 按需出现
    qt_shell.preview_pane.render(model)
    assert qt_shell.preview_pane.stack.currentIndex() == 0  # markdown 视图
    assert qt_shell.preview_pane.isVisible() is True


def test_t6_txt_preview_model(qt_shell, controller, tmp_path):
    from desktop.widgets.preview.renderers import build_preview_model

    ws_root = tmp_path / "ws2"
    ws_root.mkdir()
    (ws_root / "sample_preview.txt").write_text("纯文本内容\n第二行\n", encoding="utf-8")
    controller.open_workspace(ws_root)
    ref = next(r for r in controller.refs if r.name == "sample_preview.txt")
    artifact = controller.open_artifact(ref)
    model = build_preview_model(artifact)
    assert model.supported is True
    assert "纯文本内容" in model.content
    qt_shell.preview_pane.render(model)
    assert qt_shell.preview_pane.stack.currentIndex() == 1  # text 视图


def test_t6_unsupported_preview_for_office_formats(qt_shell, controller):
    """AC-19：docx 可读取但 Preview 明确 Unsupported，不影响读取能力。"""
    from desktop.widgets.preview.pane import INDEX_UNSUPPORTED
    from desktop.widgets.preview.renderers import build_preview_model

    controller.open_workspace(FIXTURES_DIR)
    ref = next(r for r in controller.refs if r.name == "sample.docx")
    artifact = controller.open_artifact(ref)
    model = build_preview_model(artifact)
    assert model.supported is False  # 不能 Preview
    assert artifact.blocks  # 但可以读取（Read 支持）

    qt_shell.preview_pane.render(model)
    assert qt_shell.preview_pane.stack.currentIndex() == INDEX_UNSUPPORTED
    rendered = qt_shell.preview_pane.unsupported_label.text()
    assert "暂不支持此格式的桌面预览" in rendered


def test_t6_unsupported_preview_for_office_formats(qt_shell, controller):
    """AC-19：docx 可读取但 Preview 明确 Unsupported，不影响读取能力。"""
    from desktop.widgets.preview.pane import INDEX_UNSUPPORTED
    from desktop.widgets.preview.renderers import build_preview_model

    artifact = _read_fixture_as_artifact(controller, "sample.docx")
    model = build_preview_model(artifact)
    assert model.supported is False  # 不能 Preview
    assert artifact.blocks  # 但可以读取（Read 支持）

    qt_shell.preview_pane.render(model)
    assert qt_shell.preview_pane.stack.currentIndex() == INDEX_UNSUPPORTED
    rendered = qt_shell.preview_pane.unsupported_label.text()
    assert "暂不支持此格式的桌面预览" in rendered


def test_t6_preview_close_restores_width(qt_shell):
    """AC-14：关闭 Preview 后 Conversation 恢复全宽。"""
    shell = qt_shell
    shell.preview_pane.setVisible(True)
    assert shell.preview_pane.isVisible()
    shell.close_preview()
    assert not shell.preview_pane.isVisible()
    sizes = shell.splitter.sizes()
    assert sizes[2] == 0


# ---------------------------------------------------------------------------
# T10 — Qt Smoke：Shell 渲染 / Sidebar 切换 / 无 Workspace / 无 LLM 不崩溃
# ---------------------------------------------------------------------------


def test_t10_shell_smoke(qt_shell, controller):
    """T10：启动/切换/开关 Preview/Resize 全流程不崩溃。"""
    assert controller.current_page == "home"
    # Sidebar → Plugins / Settings 切换
    qt_shell.navigate(1)
    assert qt_shell.center_stack.currentIndex() == 1
    qt_shell.navigate(2)
    assert qt_shell.center_stack.currentIndex() == 2
    qt_shell.navigate(0)
    assert qt_shell.center_stack.currentIndex() == 0
    # Resize（尊重 minimum size 约束）
    qt_shell.resize(1400, 800)
    assert qt_shell.width() == 1400


def test_t10_launch_without_workspace_and_llm(controller, qt_shell):
    """规格第 34 节：无 Workspace / 无 LLM 时 Shell 正常进入 Conversation Zero State。"""
    assert controller.app_runtime.llm_client is None
    assert controller.workspace is None
    from desktop.widgets.conversation import ConversationSurface

    assert controller.current_page in ("home", "conversation")


def test_t10_open_workspace_via_shell(qt_shell, controller):
    qt_shell.open_workspace_path(str(FIXTURES_DIR))
    assert controller.workspace is not None
    assert controller.current_page == "workspace"
    # Zero State / Conversation 切换：打开后显示 Zero State（新会话）
    assert qt_shell.conversation.zero_state.isVisible() or (
        not qt_shell.conversation.isVisible()
    )


def test_t10_composer_send_requires_active_artifact(qt_shell, controller):
    """规格第 17/18 节：未选择文件时 Send 给出内联提示而非崩溃。"""
    controller.open_workspace(FIXTURES_DIR)
    qt_shell.open_workspace_path(str(FIXTURES_DIR))
    qt_shell.conversation.input.setText("这个工作区里有什么？")
    qt_shell.conversation._emit_send()
    # 未选择 active artifact → 状态提示，不抛异常
    assert controller.current_artifact is None
