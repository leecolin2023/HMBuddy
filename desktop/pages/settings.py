"""Settings 页（规格 G7 / 第 30-31 节）：General / Model / Paths 三个分区。

Effective Value 全部展示来源（AC-08）；环境变量覆盖时 UI 不假装修改
config.json 就能改变 Effective Value。
"""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from ..controller import AppController
from application.config import AppConfig, ConfigSource


class SettingsPage:
    def __init__(self, parent, controller: AppController, shell):
        self.controller = controller
        self.shell = shell
        self.root = parent.winfo_toplevel()

        self.frame = ttk.Frame(parent, padding=4)

        header = ttk.Frame(self.frame)
        header.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(header, text="Settings", style="Title.TLabel").pack(side=tk.LEFT)
        ttk.Label(header, text="  配置立即生效（插件/模型变更会自动重建运行时）", style="Subtitle.TLabel").pack(
            side=tk.LEFT, pady=(6, 0)
        )

        if controller.config_errors:
            error_box = tk.Text(
                self.frame, height=3, wrap=tk.WORD, relief=tk.SOLID, borderwidth=1,
                foreground="#b00020",
            )
            error_box.pack(fill=tk.X, pady=(0, 8))
            error_box.insert("1.0", "Config 错误：\n" + "\n".join(controller.config_errors))
            error_box.configure(state=tk.DISABLED)

        general = ttk.LabelFrame(self.frame, text="General", style="Section.TLabelframe", padding=10)
        general.pack(fill=tk.X, pady=(0, 8))

        self.restore_var = tk.BooleanVar(
            value=bool(self.controller.config.desktop.restore_last_workspace)
        )
        ttk.Checkbutton(
            general, text="启动时恢复最近工作区", variable=self.restore_var
        ).pack(anchor=tk.W)

        row = ttk.Frame(general)
        row.pack(fill=tk.X, pady=(6, 0))
        ttk.Label(row, text="Recent Workspace 数量上限").pack(side=tk.LEFT)
        self.ws_limit_var = tk.StringVar(
            value=str(self.controller.config.desktop.recent_workspace_limit)
        )
        ttk.Entry(row, textvariable=self.ws_limit_var, width=8).pack(side=tk.LEFT, padx=(8, 16))
        ttk.Label(row, text="Recent Activity 数量上限").pack(side=tk.LEFT)
        self.activity_limit_var = tk.StringVar(
            value=str(self.controller.config.desktop.recent_activity_limit)
        )
        ttk.Entry(row, textvariable=self.activity_limit_var, width=8).pack(
            side=tk.LEFT, padx=(8, 0)
        )

        model = ttk.LabelFrame(self.frame, text="Model", style="Section.TLabelframe", padding=10)
        model.pack(fill=tk.X, pady=(0, 8))
        model.columnconfigure(1, weight=1)

        effective = self.controller.effective_config
        ttk.Label(model, text="Base URL").grid(row=0, column=0, sticky=tk.W)
        self.base_url_var = tk.StringVar(value=str(effective.llm_base_url.value))
        ttk.Entry(model, textvariable=self.base_url_var).grid(row=0, column=1, sticky=tk.EW, padx=8)
        ttk.Label(model, text=_source_text(effective.llm_base_url), foreground="#666").grid(
            row=0, column=2, sticky=tk.W
        )

        ttk.Label(model, text="Model").grid(row=1, column=0, sticky=tk.W, pady=(6, 0))
        self.model_var = tk.StringVar(value=str(effective.llm_model.value))
        ttk.Entry(model, textvariable=self.model_var).grid(row=1, column=1, sticky=tk.EW, padx=8, pady=(6, 0))
        ttk.Label(model, text=_source_text(effective.llm_model), foreground="#666").grid(
            row=1, column=2, sticky=tk.W, pady=(6, 0)
        )

        ttk.Label(model, text="API Key 来源").grid(row=2, column=0, sticky=tk.W, pady=(6, 0))
        self.api_key_env_var = tk.StringVar(value=str(effective.api_key_env.value))
        ttk.Entry(model, textvariable=self.api_key_env_var).grid(
            row=2, column=1, sticky=tk.EW, padx=8, pady=(6, 0)
        )
        ttk.Label(
            model,
            text="只保存环境变量名，不保存明文密钥（FR-C03）",
            foreground="#666",
        ).grid(row=2, column=2, sticky=tk.W, pady=(6, 0))

        paths = ttk.LabelFrame(self.frame, text="Paths", style="Section.TLabelframe", padding=10)
        paths.pack(fill=tk.X, pady=(0, 8))
        paths.columnconfigure(1, weight=1)

        ttk.Label(paths, text="OCR 模型目录").grid(row=0, column=0, sticky=tk.W)
        self.model_dir_var = tk.StringVar(value=str(effective.model_dir.value))
        ttk.Entry(paths, textvariable=self.model_dir_var).grid(row=0, column=1, sticky=tk.EW, padx=8)
        ttk.Label(paths, text=_source_text(effective.model_dir), foreground="#666").grid(
            row=0, column=2, sticky=tk.W
        )

        ttk.Label(paths, text="外部插件目录").grid(row=1, column=0, sticky=tk.NW, pady=(6, 0))
        dirs_frame = ttk.Frame(paths)
        dirs_frame.grid(row=1, column=1, sticky=tk.EW, padx=8, pady=(6, 0))
        self.dirs_list = tk.Listbox(dirs_frame, height=4)
        for path, source in effective.external_plugin_dirs:
            self.dirs_list.insert(tk.END, f"{path}（{source.value}）")
        self.dirs_list.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(
            paths,
            text="增删请到 Plugins 页；\n环境变量来源不可在 UI 删除",
            foreground="#666",
        ).grid(row=1, column=2, sticky=tk.W, pady=(6, 0))

        actions = ttk.Frame(self.frame)
        actions.pack(fill=tk.X)
        ttk.Button(actions, text="保存并应用", command=self.save).pack(side=tk.LEFT)
        ttk.Button(
            actions, text="打开 Plugins 管理", command=lambda: self.shell.navigate("plugins")
        ).pack(side=tk.LEFT, padx=(8, 0))

    def save(self) -> None:
        try:
            ws_limit = max(int(self.ws_limit_var.get().strip() or 10), 0)
            activity_limit = max(int(self.activity_limit_var.get().strip() or 20), 0)
        except ValueError:
            messagebox.showerror("输入无效", "数量上限必须是整数。")
            return
        config = AppConfig()
        config.desktop.restore_last_workspace = bool(self.restore_var.get())
        config.desktop.recent_workspace_limit = ws_limit
        config.desktop.recent_activity_limit = activity_limit
        config.llm.base_url = self.base_url_var.get().strip()
        config.llm.model = self.model_var.get().strip()
        config.llm.api_key_env = self.api_key_env_var.get().strip() or "HMBUDDY_LLM_API_KEY"
        config.paths.model_dir = self.model_dir_var.get().strip()
        # external_plugin_dirs / disabled_plugin_ids 由 Plugins 页管理，这里保留
        config.paths.external_plugin_dirs = list(self.controller.config.paths.external_plugin_dirs)
        config.plugins.disabled_plugin_ids = list(self.controller.config.plugins.disabled_plugin_ids)

        self.controller.save_settings(config)
        self.shell.refresh_status()
        messagebox.showinfo("已保存", "设置已保存并应用（配置写入 config.json）。")


def _source_text(effective_value) -> str:
    detail = f" {effective_value.detail}" if effective_value.detail else ""
    return f"来源：{effective_value.source.value}{detail}"
