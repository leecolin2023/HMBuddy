"""HMBuddy Desktop — Application Composition Root（Phase 2.1 / 规格第 34 节）。

只负责组装：config / state / plugin runtime / llm client / desktop shell。
页面业务逻辑在 desktop/pages/*，应用逻辑在 desktop/controller.py 与
application/*。任何 Config / State / 插件 / LLM 错误都不阻断进入 Home
（规格第 33 节）。
"""
from __future__ import annotations

import logging
import tkinter as tk
from pathlib import Path

from .controller import bootstrap_controller
from .shell import DesktopShell

LOGGER = logging.getLogger("hmbuddy.desktop")


def _setup_file_logging() -> None:
    """把应用日志写入用户数据目录 logs/（规格第 40 节；失败则仅控制台）。"""
    try:
        from application.config import app_logs_dir

        logs_dir = app_logs_dir()
        logs_dir.mkdir(parents=True, exist_ok=True)
        log_file = logs_dir / "hmbuddy.log"
        handler = logging.FileHandler(log_file, encoding="utf-8")
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
        )
        logging.getLogger("hmbuddy").addHandler(handler)
        LOGGER.info("file logging enabled path=%s", log_file)
    except OSError as exc:
        LOGGER.warning("file logging disabled: %s", exc)


def main() -> int:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s"
    )
    _setup_file_logging()

    # 启动流程（规格第 33 节）：任何部分失败都不阻断进入 Home
    controller = bootstrap_controller()

    root = tk.Tk()
    root.title("HMBuddy · 本地办公助手")
    root.geometry("1180x780")
    root.minsize(980, 640)
    DesktopShell(root, controller)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
