"""HMBuddy Desktop — Application Composition Root（Phase 2.2 / 规格第 34 节）。

PySide6 Presentation Shell。只负责组装：config / state / plugin runtime /
llm client / Qt shell。页面业务逻辑在 desktop/controller.py 与 application/*。
任何 Config / State / 插件 / LLM 错误都不阻断进入 Shell（规格第 34 节）。
"""
from __future__ import annotations

import logging
import sys

from PySide6.QtWidgets import QApplication

from .controller import bootstrap_controller
from .shell import DesktopShell

LOGGER = logging.getLogger("hmbuddy.desktop")


def _setup_file_logging() -> None:
    """把应用日志写入用户数据目录 logs/（规格 2.1 第 40 节；失败则仅控制台）。"""
    try:
        from application.config import app_logs_dir

        logs_dir = app_logs_dir()
        logs_dir.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(logs_dir / "hmbuddy.log", encoding="utf-8")
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
        )
        logging.getLogger("hmbuddy").addHandler(handler)
        LOGGER.info("file logging enabled path=%s", logs_dir / "hmbuddy.log")
    except OSError as exc:
        LOGGER.warning("file logging disabled: %s", exc)


def main() -> int:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s"
    )
    _setup_file_logging()

    # 启动流程（规格第 34 节）：Resolve Config/State → Assemble Runtime →
    # Build Controller → Start Qt Application → Build Shell → Restore。
    controller = bootstrap_controller()

    app = QApplication(sys.argv)
    app.setApplicationName("HMBuddy")
    shell = DesktopShell(controller)
    shell.show()

    # Restore Last Workspace if enabled（不阻断启动）
    if (
        controller.effective_config.restore_last_workspace.value
        and controller.state.last_view.workspace_path
    ):
        shell.open_workspace_path(controller.state.last_view.workspace_path)

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
