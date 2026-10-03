"""Plugins 页（规格 G6 / 第 22-29 节）：现有 File Capability Runtime 的产品视图。"""
from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from ..controller import AppController


class PluginsPage:
    def __init__(self, parent, controller: AppController, shell):
        self.controller = controller
        self.shell = shell
        self.root = parent.winfo_toplevel()

        self.frame = ttk.Frame(parent, padding=4)

        header = ttk.Frame(self.frame)
        header.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(header, text="Plugins", style="Title.TLabel").pack(side=tk.LEFT)
        ttk.Label(
            header,
            text="  File Capability Runtime 的产品视图（Enable/Disable 记录在 AppConfig，不修改插件文件）",
            style="Subtitle.TLabel",
        ).pack(side=tk.LEFT, pady=(6, 0))

        actions = ttk.Frame(self.frame)
        actions.pack(fill=tk.X, pady=(0, 8))
        ttk.Button(actions, text="启用", command=lambda: self.set_enabled(True)).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(actions, text="禁用", command=lambda: self.set_enabled(False)).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(actions, text="Rescan（重新发现并加载）", command=self.rescan).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(actions, text="添加外部插件目录", command=self.add_external_dir).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(
            actions, text="移除选中外部目录", command=self.remove_external_dir
        ).pack(side=tk.LEFT)

        columns = (
            "status", "name", "plugin_id", "version", "source",
            "extensions", "capabilities", "permissions", "availability", "error",
        )
        self.plugin_tree = ttk.Treeview(
            self.frame, columns=columns, show="headings", selectmode="browse"
        )
        headers = (
            ("status", "状态", 90),
            ("name", "名称", 150),
            ("plugin_id", "Plugin ID", 190),
            ("version", "版本", 60),
            ("source", "来源", 66),
            ("extensions", "扩展名", 110),
            ("capabilities", "能力", 120),
            ("permissions", "权限（声明/生效）", 150),
            ("availability", "可用性", 130),
            ("error", "加载错误", 200),
        )
        for column_id, text, width in headers:
            self.plugin_tree.heading(column_id, text=text)
            self.plugin_tree.column(column_id, width=width, anchor=tk.W)
        scroll = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.plugin_tree.yview)
        self.plugin_tree.configure(yscrollcommand=scroll.set)
        self.plugin_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.detail_var = tk.StringVar(value="")
        ttk.Label(self.frame, textvariable=self.detail_var, wraplength=900).pack(
            fill=tk.X, pady=(8, 0)
        )
        self.plugin_tree.bind("<<TreeviewSelect>>", self._on_selected)

        self.refresh()

    def refresh(self) -> None:
        self.views = self.controller.plugin_views()
        for item in self.plugin_tree.get_children():
            self.plugin_tree.delete(item)
        for index, view in enumerate(self.views):
            self.plugin_tree.insert(
                "",
                tk.END,
                iid=str(index),
                values=(
                    view.status_display(),
                    view.name,
                    view.plugin_id,
                    view.version,
                    "内置" if view.is_builtin else "外部",
                    " ".join(view.extensions),
                    " ".join(view.capabilities),
                    f"{' '.join(view.declared_permissions) or '-'}"
                    f" / {' '.join(view.effective_permissions) or '-'}",
                    view.availability_reason or "可用",
                    view.load_error or "",
                ),
            )

    def _selected_view(self):
        selected = self.plugin_tree.selection()
        if not selected:
            return None
        try:
            return self.views[int(selected[0])]
        except (ValueError, IndexError):
            return None

    def _on_selected(self, _event=None) -> None:
        view = self._selected_view()
        if view is None:
            return
        detail = f"{view.name}（{view.plugin_id}）v{view.version} · API v{view.api_version} · 来源 {view.source}"
        if view.providers:
            # INT-010：Provider 明细放详情区域
            provider_lines = [
                f"  · {item.provider_id}（{', '.join(item.capabilities)}，"
                f"priority={item.priority}，"
                f"{'可用' if item.available else '不可用：' + item.availability_reason}）"
                for item in view.providers
            ]
            detail += "\nProviders（" + str(len(view.providers)) + "）：\n" + "\n".join(
                provider_lines
            )
        if view.load_error:
            detail += f"\n加载错误：{view.load_error}"
        if view.availability_reason and view.status != "Disabled":
            detail += f"\n可用性：{view.availability_reason}"
        self.detail_var.set(detail)

    def set_enabled(self, enabled: bool) -> None:
        view = self._selected_view()
        if view is None:
            messagebox.showinfo("未选择插件", "请先选择一个插件。")
            return
        if not enabled and view.is_builtin:
            # 规格第 26 节：允许禁用内置插件，但必须提示影响
            confirm = messagebox.askyesno(
                "禁用内置插件",
                f"禁用 {view.name} 后，当前 Runtime 可能失去 "
                f"{', '.join(view.extensions) or view.plugin_id} 的读取能力。确定继续？",
            )
            if not confirm:
                return
        self.controller.set_plugin_enabled(view.plugin_id, enabled)
        self.refresh()
        self.shell.refresh_status()

    def rescan(self) -> None:
        self.controller.rescan_plugins()
        self.refresh()
        self.shell.refresh_status()
        messagebox.showinfo("Rescan 完成", "已按当前配置重新发现并加载插件。")

    def add_external_dir(self) -> None:
        selected = filedialog.askdirectory(title="添加外部插件目录（其子目录各为一个插件）")
        if not selected:
            return
        config = self.controller.config
        dirs = list(config.paths.external_plugin_dirs)
        if selected not in dirs:
            dirs.append(selected)
            config.paths.external_plugin_dirs = dirs
            self.controller.save_settings(config)
        self.refresh()
        self.shell.refresh_status()

    def remove_external_dir(self) -> None:
        view = self._selected_view()
        selected = filedialog.askdirectory(title="选择要移除的外部插件目录")
        if not selected:
            return
        config = self.controller.config
        # 环境变量来源的路径不能由 UI 假装删除（规格第 27 节）
        env_dirs = self.controller.effective_config.external_plugin_dirs
        env_only = {
            path for path, source in env_dirs if str(source.value) == "Environment"
        }
        if Path(selected).resolve() in {Path(item).resolve() for item in env_only}:
            messagebox.showwarning(
                "无法移除",
                "该目录来自环境变量 HMBUDDY_PLUGIN_PATH，请修改环境变量后重启生效。",
            )
            return
        if selected in config.paths.external_plugin_dirs:
            config.paths.external_plugin_dirs.remove(selected)
            self.controller.save_settings(config)
        self.refresh()
        self.shell.refresh_status()
