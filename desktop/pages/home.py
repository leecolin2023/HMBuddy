"""Home 页（规格 G3 / 第 20 节）：导航与状态入口，不承担业务逻辑。"""
from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from ..controller import AppController


class HomePage:
    def __init__(self, parent, controller: AppController, shell):
        self.controller = controller
        self.shell = shell

        self.frame = ttk.Frame(parent, padding=4)

        header = ttk.Frame(self.frame)
        header.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(header, text="Home", style="Title.TLabel").pack(side=tk.LEFT)
        ttk.Label(header, text="  从这里进入最近的工作环境", style="Subtitle.TLabel").pack(
            side=tk.LEFT, pady=(6, 0)
        )

        quick = ttk.LabelFrame(self.frame, text="快速开始", style="Section.TLabelframe", padding=10)
        quick.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(quick, text="打开 Workspace", command=self.open_workspace_dialog).pack(
            side=tk.LEFT, padx=(0, 8)
        )
        ttk.Button(quick, text="打开文件", command=self.open_file_dialog).pack(side=tk.LEFT)

        body = ttk.Frame(self.frame)
        body.pack(fill=tk.BOTH, expand=True)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        recent_frame = ttk.LabelFrame(
            body, text="Recent Workspaces", style="Section.TLabelframe", padding=8
        )
        recent_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        activity_frame = ttk.LabelFrame(
            body, text="Recent Activity", style="Section.TLabelframe", padding=8
        )
        activity_frame.grid(row=0, column=1, sticky="nsew")

        columns = ("name", "path", "opened", "pinned")
        self.recent_tree = ttk.Treeview(
            recent_frame, columns=columns, show="headings", selectmode="browse"
        )
        for column_id, text, width, anchor in (
            ("name", "名称", 130, tk.W),
            ("path", "路径", 240, tk.W),
            ("opened", "最近打开", 140, tk.CENTER),
            ("pinned", "置顶", 46, tk.CENTER),
        ):
            self.recent_tree.heading(column_id, text=text)
            self.recent_tree.column(column_id, width=width, anchor=anchor)
        self.recent_tree.pack(fill=tk.BOTH, expand=True)
        self.recent_tree.bind("<Double-1>", lambda _e: self.open_selected_recent())

        recent_actions = ttk.Frame(recent_frame)
        recent_actions.pack(fill=tk.X, pady=(6, 0))
        ttk.Button(recent_actions, text="打开", command=self.open_selected_recent).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        self.pin_button = ttk.Button(
            recent_actions, text="置顶/取消", command=self.toggle_pin
        )
        self.pin_button.pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(
            recent_actions, text="移除", command=self.remove_selected
        ).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(
            recent_actions, text="清空（保留置顶）", command=self.clear_recent
        ).pack(side=tk.LEFT)

        self.activity_tree = ttk.Treeview(
            activity_frame,
            columns=("type", "title", "opened"),
            show="headings",
            selectmode="browse",
        )
        for column_id, text, width in (
            ("type", "类型", 70),
            ("title", "内容", 280),
            ("opened", "时间", 140),
        ):
            self.activity_tree.heading(column_id, text=text)
            self.activity_tree.column(column_id, width=width, anchor=tk.W)
        self.activity_tree.pack(fill=tk.BOTH, expand=True)
        self.activity_tree.bind("<Double-1>", lambda _e: self.open_selected_activity())

        self.status_frame = ttk.LabelFrame(
            self.frame, text="System Status", style="Section.TLabelframe", padding=8
        )
        self.status_frame.pack(fill=tk.X, pady=(10, 0))
        self.status_text = tk.Text(
            self.status_frame,
            height=6,
            wrap=tk.WORD,
            font=("Microsoft YaHei UI", 9),
            relief=tk.FLAT,
        )
        self.status_text.pack(fill=tk.X)
        self.status_text.configure(state=tk.DISABLED)

        self.refresh()

    # ------------------------------------------------------------------

    def refresh(self) -> None:
        self._render_recent()
        self._render_activity()
        self._render_status()

    def _render_recent(self) -> None:
        """INT-006：iid 使用稳定 workspace_id，不依赖 list index。"""
        self.workspaces_by_id = {
            entry.workspace_id: entry for entry in self.controller.recent_workspaces()
        }
        for item in self.recent_tree.get_children():
            self.recent_tree.delete(item)
        for entry in self.controller.recent_workspaces():
            missing = not Path(entry.path).is_dir()
            self.recent_tree.insert(
                "",
                tk.END,
                iid=entry.workspace_id,
                values=(
                    ("[Missing] " if missing else "") + entry.display_name,
                    entry.path,
                    entry.last_opened_at[:19].replace("T", " "),
                    "是" if entry.pinned else "",
                ),
            )

    def _render_activity(self) -> None:
        """INT-006：iid 使用稳定 entry_id，Tk 自动 iid（I001）不再参与选择映射。"""
        self.activity_by_id = {
            entry.entry_id: entry for entry in self.controller.recent_activity()
        }
        for item in self.activity_tree.get_children():
            self.activity_tree.delete(item)
        type_labels = {"workspace": "工作区", "artifact": "文件", "artifact_qa": "问答"}
        for entry in self.controller.recent_activity():
            self.activity_tree.insert(
                "",
                tk.END,
                iid=entry.entry_id,
                values=(
                    type_labels.get(entry.activity_type, entry.activity_type),
                    entry.title or entry.artifact_path or entry.workspace_path,
                    entry.last_opened_at[:19].replace("T", " "),
                ),
            )

    def _render_status(self) -> None:
        status = self.controller.system_status()
        lines = [
            f"LLM：{status.llm}" + (f"（{status.llm_detail}）" if status.llm_detail else ""),
            f"Plugins：Loaded {status.plugins_loaded} · Disabled {status.plugins_disabled}"
            f" · Error {status.plugins_error}",
            f"Model Directory：{status.model_dir}"
            + (f"（{status.model_dir_detail}）" if status.model_dir_detail else ""),
            f"Last Workspace：{status.last_workspace}"
            + (f"（{status.last_workspace_detail}）" if status.last_workspace_detail else ""),
        ]
        self.status_text.configure(state=tk.NORMAL)
        self.status_text.delete("1.0", tk.END)
        self.status_text.insert("1.0", "\n".join(lines))
        self.status_text.configure(state=tk.DISABLED)

    # ------------------------------------------------------------------

    def _selected_recent_path(self) -> str | None:
        selected = self.recent_tree.selection()
        if not selected:
            return None
        entry = self.workspaces_by_id.get(selected[0])
        return entry.path if entry is not None else None

    def _file_dialog_filters(self) -> list[tuple[str, str]]:
        """INT-009 / AC-I12：File Picker 从 Capability Catalog 动态生成，
        并保留"所有文件"作为用户显式兜底。"""
        extensions = sorted(self.controller.app_runtime.catalog.artifact_extensions())
        patterns = " ".join(f"*{ext}" for ext in extensions) or "*.*"
        return [("支持的文件", patterns), ("所有文件", "*.*")]

    def open_workspace_dialog(self) -> None:
        selected = filedialog.askdirectory(title="选择 HMBuddy 工作目录")
        if not selected:
            return
        self.open_workspace_path(selected)

    def open_file_dialog(self) -> None:
        selected = filedialog.askopenfilename(
            title="选择办公文件",
            filetypes=self._file_dialog_filters(),
        )
        if not selected:
            return
        path = Path(selected).resolve()
        snapshot = self.open_workspace_path(path.parent, quiet=True)
        # 打开文件所在工作区后进入 workspace 页并选中该文件
        self.shell.navigate("workspace", {"workspace_path": str(path.parent)})
        self.shell.pages["workspace"].select_and_load(path)

    def open_workspace_path(self, raw: str, quiet: bool = False) -> object:
        try:
            snapshot = self.controller.open_workspace(raw)
        except (FileNotFoundError, NotADirectoryError, OSError) as exc:
            if not quiet:
                messagebox.showerror("工作区不可用", str(exc))
            return None
        if not quiet:
            self.shell.navigate("workspace", {"workspace_path": str(snapshot.workspace.root_path)})
        return snapshot

    def open_selected_recent(self) -> None:
        path = self._selected_recent_path()
        if not path:
            return
        if not Path(path).is_dir():
            # RW-02 Missing：提供 Remove / Relocate 而不删除历史
            answer = messagebox.askyesnocancel(
                "工作区路径缺失",
                f"路径不存在：\n{path}\n\n是：重新定位该目录\n否：从 Recent 移除\n取消：不做任何操作",
            )
            if answer is True:
                relocated = filedialog.askdirectory(title="重新定位工作目录")
                if relocated:
                    self.controller.remove_recent_workspace(path)
                    self.open_workspace_path(relocated)
                    self.refresh()
            elif answer is False:
                self.controller.remove_recent_workspace(path)
                self.refresh()
            return
        self.open_workspace_path(path)
        self.refresh()

    def toggle_pin(self) -> None:
        path = self._selected_recent_path()
        if not path:
            return
        entry = next(
            (item for item in self.controller.recent_workspaces() if item.path == path),
            None,
        )
        if entry is not None:
            self.controller.pin_workspace(path, not entry.pinned)
            self.refresh()

    def remove_selected(self) -> None:
        path = self._selected_recent_path()
        if path:
            self.controller.remove_recent_workspace(path)
            self.refresh()

    def clear_recent(self) -> None:
        self.controller.clear_recent_workspaces()
        self.refresh()

    def open_selected_activity(self) -> None:
        selected = self.activity_tree.selection()
        if not selected:
            return
        entry = self.activity_by_id.get(selected[0])
        if entry is None:
            return
        if entry.workspace_path and Path(entry.workspace_path).is_dir():
            self.controller.open_workspace(entry.workspace_path)
            self.shell.navigate("workspace", {"workspace_path": entry.workspace_path})
            if entry.artifact_path and Path(entry.artifact_path).is_file():
                self.shell.pages["workspace"].select_and_load(Path(entry.artifact_path))
        elif entry.workspace_path:
            messagebox.showwarning("路径缺失", f"工作区路径不存在：\n{entry.workspace_path}")
