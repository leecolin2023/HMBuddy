"""Desktop Navigation Shell（规格第 21 / G8 节）。

左侧固定导航（Home / Workspace / Plugins / Settings），右侧内容区按
current_page 切换页面帧。Artifact 是 Workspace 页内视图，不是独立页面。
不做 SPA Router，只维护 current_page + navigate。
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .controller import AppController

NAV_ITEMS = (
    ("home", "Home"),
    ("workspace", "Workspace"),
    ("plugins", "Plugins"),
    ("settings", "Settings"),
)


class DesktopShell:
    def __init__(self, root: tk.Tk, controller: AppController):
        self.root = root
        self.controller = controller
        self.pages: dict[str, ttk.Frame] = {}

        self._configure_style()
        self._build_layout()
        self.navigate(controller.current_page or "home")

    def _configure_style(self) -> None:
        style = ttk.Style()
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("Title.TLabel", font=("Microsoft YaHei UI", 16, "bold"))
        style.configure("Subtitle.TLabel", font=("Microsoft YaHei UI", 9))
        style.configure("Section.TLabelframe.Label", font=("Microsoft YaHei UI", 10, "bold"))
        style.configure("Treeview", rowheight=26, font=("Microsoft YaHei UI", 9))
        style.configure("Treeview.Heading", font=("Microsoft YaHei UI", 9, "bold"))
        style.configure(
            "Nav.TButton", font=("Microsoft YaHei UI", 10), anchor="w", padding=(12, 8)
        )

    def _build_layout(self) -> None:
        container = ttk.Frame(self.root, padding=0)
        container.pack(fill=tk.BOTH, expand=True)

        nav = ttk.Frame(container, width=168, padding=10)
        nav.pack(side=tk.LEFT, fill=tk.Y)
        nav.pack_propagate(False)

        ttk.Label(nav, text="HMBuddy", style="Title.TLabel").pack(anchor=tk.W)
        ttk.Label(nav, text="本地办公助手", style="Subtitle.TLabel").pack(
            anchor=tk.W, pady=(0, 12)
        )
        self.nav_buttons: dict[str, ttk.Button] = {}
        for page_id, label in NAV_ITEMS:
            button = ttk.Button(
                nav,
                text=label,
                style="Nav.TButton",
                command=lambda page_id=page_id: self.navigate(page_id),
            )
            button.pack(fill=tk.X, pady=2)
            self.nav_buttons[page_id] = button

        self.status_var = tk.StringVar(value="")
        ttk.Label(nav, textvariable=self.status_var, wraplength=140).pack(
            side=tk.BOTTOM, anchor=tk.W
        )

        self.content = ttk.Frame(container, padding=(14, 12))
        self.content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 页面按需构建、切换时隐藏/显示，保持各页面内部状态
        self._build_pages()

    def _build_pages(self) -> None:
        # 延迟导入避免循环依赖（页面需要回访 shell 的能力时通过 controller）
        from .pages.home import HomePage
        from .pages.plugins import PluginsPage
        from .pages.settings import SettingsPage
        from .pages.workspace import WorkspacePage

        builders = {
            "home": HomePage,
            "workspace": WorkspacePage,
            "plugins": PluginsPage,
            "settings": SettingsPage,
        }
        for page_id, page_class in builders.items():
            frame = page_class(self.content, self.controller, self)
            self.pages[page_id] = frame.frame

    def navigate(self, page_id: str) -> None:
        if page_id not in self.pages:
            raise ValueError(f"unknown page: {page_id!r}")
        self.controller.navigate(page_id)
        for page, frame in self.pages.items():
            if page == page_id:
                frame.pack(fill=tk.BOTH, expand=True)
            else:
                frame.pack_forget()
        for page_id_key, button in self.nav_buttons.items():
            button.state(["pressed"] if page_id_key == page_id else ["!pressed"])
        self.refresh_status()

    def refresh_status(self) -> None:
        status = self.controller.system_status()
        self.status_var.set(
            f"LLM: {status.llm}\nPlugins: {status.plugins_loaded}"
            f"（禁用 {status.plugins_disabled} / 错误 {status.plugins_error}）"
        )
