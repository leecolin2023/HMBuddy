"""Workspace 页（规格 G8）：工作区浏览 + Artifact 阅读 + 问答（沿用 Phase 2 交互）。"""
from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from ..controller import AppController
from ..presenter import artifact_summary_text, format_datetime, format_file_size


class WorkspacePage:
    def __init__(self, parent, controller: AppController, shell):
        self.controller = controller
        self.shell = shell
        self.root = parent.winfo_toplevel()

        self.frame = ttk.Frame(parent, padding=4)
        self.workspace_var = tk.StringVar()
        self.status_var = tk.StringVar(value="请选择一个工作目录")
        self.file_count_var = tk.StringVar(value="0 个文件")
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        header = ttk.Frame(self.frame)
        header.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(header, text="Workspace", style="Title.TLabel").pack(side=tk.LEFT)
        ttk.Label(
            header, text="  选择工作目录，读取并阅读 Artifact", style="Subtitle.TLabel"
        ).pack(side=tk.LEFT, pady=(6, 0))

        workspace_frame = ttk.LabelFrame(
            self.frame, text="工作区", style="Section.TLabelframe", padding=10
        )
        workspace_frame.pack(fill=tk.X, pady=(0, 12))
        workspace_frame.columnconfigure(0, weight=1)

        self.workspace_entry = ttk.Entry(workspace_frame, textvariable=self.workspace_var)
        self.workspace_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ttk.Button(workspace_frame, text="选择目录", command=self.choose_workspace).grid(
            row=0, column=1, padx=(0, 6)
        )
        ttk.Button(workspace_frame, text="选择文件", command=self.choose_file).grid(
            row=0, column=2, padx=(0, 6)
        )
        self.refresh_button = ttk.Button(
            workspace_frame, text="刷新", command=self.refresh_workspace
        )
        self.refresh_button.grid(row=0, column=3)
        self.workspace_entry.bind("<Return>", lambda _event: self.open_workspace_path())

        main = ttk.Panedwindow(self.frame, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(main, padding=(0, 0, 8, 0))
        right = ttk.Frame(main, padding=(8, 0, 0, 0))
        main.add(left, weight=2)
        main.add(right, weight=3)

        left_header = ttk.Frame(left)
        left_header.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(
            left_header, text="工作区文件", font=("Microsoft YaHei UI", 10, "bold")
        ).pack(side=tk.LEFT)
        ttk.Label(left_header, textvariable=self.file_count_var).pack(side=tk.RIGHT)

        columns = ("type", "name", "size", "modified")
        self.file_tree = ttk.Treeview(
            left, columns=columns, show="headings", selectmode="browse"
        )
        for column_id, text, width, anchor in (
            ("type", "类型", 62, tk.CENTER),
            ("name", "文件名", 280, tk.W),
            ("size", "大小", 82, tk.E),
            ("modified", "修改时间", 142, tk.CENTER),
        ):
            self.file_tree.heading(column_id, text=text)
            self.file_tree.column(column_id, width=width, anchor=anchor)

        tree_scroll = ttk.Scrollbar(left, orient=tk.VERTICAL, command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=tree_scroll.set)
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_tree.bind("<<TreeviewSelect>>", self._on_file_selected)
        self.file_tree.bind("<Double-1>", lambda _event: self.load_selected_artifact())

        notebook = ttk.Notebook(right)
        notebook.pack(fill=tk.BOTH, expand=True)

        overview_tab = ttk.Frame(notebook, padding=12)
        qa_tab = ttk.Frame(notebook, padding=12)
        notebook.add(overview_tab, text="文件概览")
        notebook.add(qa_tab, text="文档问答")

        overview_actions = ttk.Frame(overview_tab)
        overview_actions.pack(fill=tk.X, pady=(0, 8))
        self.read_button = ttk.Button(
            overview_actions,
            text="读取选中文件",
            command=self.load_selected_artifact,
            state=tk.DISABLED,
        )
        self.read_button.pack(side=tk.LEFT)
        ttk.Label(
            overview_actions, text="双击文件也可读取；读取沿用 Capability Runtime"
        ).pack(side=tk.LEFT, padx=(10, 0))

        self.summary_text = tk.Text(
            overview_tab,
            wrap=tk.WORD,
            font=("Consolas", 10),
            relief=tk.SOLID,
            borderwidth=1,
            padx=12,
            pady=12,
        )
        summary_scroll = ttk.Scrollbar(
            overview_tab, orient=tk.VERTICAL, command=self.summary_text.yview
        )
        self.summary_text.configure(yscrollcommand=summary_scroll.set)
        self.summary_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        summary_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self._set_text(self.summary_text, "请选择工作区中的文件。")

        ttk.Label(qa_tab, text="问题", font=("Microsoft YaHei UI", 10, "bold")).pack(
            anchor=tk.W
        )
        question_row = ttk.Frame(qa_tab)
        question_row.pack(fill=tk.X, pady=(6, 10))
        self.question_entry = ttk.Entry(question_row)
        self.question_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self.question_entry.bind("<Return>", lambda _event: self.ask_question())
        self.ask_button = ttk.Button(
            question_row, text="提问", command=self.ask_question, state=tk.DISABLED
        )
        self.ask_button.pack(side=tk.RIGHT)

        ttk.Label(qa_tab, text="回答", font=("Microsoft YaHei UI", 10, "bold")).pack(
            anchor=tk.W
        )
        self.answer_text = tk.Text(
            qa_tab,
            wrap=tk.WORD,
            font=("Microsoft YaHei UI", 10),
            relief=tk.SOLID,
            borderwidth=1,
            padx=12,
            pady=12,
        )
        answer_scroll = ttk.Scrollbar(
            qa_tab, orient=tk.VERTICAL, command=self.answer_text.yview
        )
        self.answer_text.configure(yscrollcommand=answer_scroll.set)
        self.answer_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(6, 0))
        answer_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=(6, 0))
        self._set_text(
            self.answer_text,
            "读取文件后即可提问。若模型未配置，请到 Settings → Model 配置。",
        )

        status = ttk.Frame(self.frame)
        status.pack(fill=tk.X, pady=(10, 0))
        ttk.Separator(status, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(0, 8))
        ttk.Label(status, textvariable=self.status_var).pack(side=tk.LEFT)

    # ------------------------------------------------------------------

    def refresh(self) -> None:
        """页面被导航显示时刷新：同步 Controller 的最近工作区与 LLM 状态。"""
        state = self.controller.state
        if self.controller.workspace is None and state.last_view.workspace_path:
            if Path(state.last_view.workspace_path).is_dir():
                if self.controller.effective_config.restore_last_workspace.value:
                    try:
                        self.controller.open_workspace(state.last_view.workspace_path)
                    except (OSError, FileNotFoundError):
                        pass
        if self.controller.workspace is not None:
            self.workspace_var.set(str(self.controller.workspace.root_path))
            self._render_refs()
        llm = self.controller.app_runtime
        status = f"模型：{llm.llm_status}"
        if llm.llm_client is not None:
            status = f"模型：{llm.llm_client.model_name}"

    def choose_workspace(self) -> None:
        initial = self.workspace_var.get().strip() or str(Path.cwd())
        selected = filedialog.askdirectory(title="选择 HMBuddy 工作目录", initialdir=initial)
        if selected:
            self.open_workspace_path(selected)

    def choose_file(self) -> None:
        selected = filedialog.askopenfilename(
            title="选择办公文件",
            filetypes=[
                ("支持的文件", "*.docx *.pdf *.xlsx *.xls *.pptx *.doc *.txt *.md *.csv"),
                ("所有文件", "*.*"),
            ],
        )
        if not selected:
            return
        path = Path(selected).resolve()
        self.workspace_var.set(str(path.parent))
        self.open_workspace_path(str(path.parent), select_path=path)

    def open_workspace_path(
        self, raw: str | None = None, select_path: Path | None = None
    ) -> None:
        target = (raw or self.workspace_var.get()).strip()
        if not target:
            self.status_var.set("请输入或选择工作目录")
            return
        try:
            snapshot = self.controller.open_workspace(target)
        except (FileNotFoundError, NotADirectoryError, OSError) as exc:
            messagebox.showerror("工作区不可用", str(exc))
            self.status_var.set("工作区加载失败")
            return
        self.workspace_var.set(str(snapshot.workspace.root_path))
        self._render_refs(select_path=select_path)
        self.status_var.set(f"已加载工作区：{snapshot.workspace.root_path}")

    def refresh_workspace(self) -> None:
        if not self.workspace_var.get().strip():
            self.choose_workspace()
            return
        self.open_workspace_path()

    def select_and_load(self, path: Path) -> None:
        """Home 页"打开文件"入口：定位并读取指定文件。"""
        if self.controller.workspace is None or not str(path).startswith(
            str(self.controller.workspace.root_path)
        ):
            try:
                self.controller.open_workspace(path.parent)
            except (FileNotFoundError, NotADirectoryError, OSError) as exc:
                messagebox.showerror("工作区不可用", str(exc))
                return
        self.workspace_var.set(str(self.controller.workspace.root_path))
        self._render_refs(select_path=path)
        self.load_selected_artifact()

    def _render_refs(self, select_path: Path | None = None) -> None:
        self.current_artifact = None
        self.read_button.configure(state=tk.DISABLED)
        self.ask_button.configure(state=tk.DISABLED)
        self._set_text(self.summary_text, "请选择工作区中的文件。")
        self._set_text(self.answer_text, "读取文件后即可提问。")

        for item in self.file_tree.get_children():
            self.file_tree.delete(item)

        selected_iid = None
        for index, ref in enumerate(self.controller.refs):
            iid = str(index)
            self.file_tree.insert(
                "",
                tk.END,
                iid=iid,
                values=(
                    ref.artifact_type.upper(),
                    ref.name,
                    format_file_size(ref.size),
                    format_datetime(ref.modified_at),
                ),
            )
            if select_path is not None and Path(ref.path).resolve() == select_path:
                selected_iid = iid

        self.file_count_var.set(f"{len(self.controller.refs)} 个文件")
        if selected_iid is not None:
            self.file_tree.selection_set(selected_iid)
            self.file_tree.focus(selected_iid)
            self.file_tree.see(selected_iid)
            self._on_file_selected()

    def _selected_ref(self):
        selected = self.file_tree.selection()
        if not selected:
            return None
        try:
            return self.controller.refs[int(selected[0])]
        except (ValueError, IndexError):
            return None

    def _on_file_selected(self, _event=None) -> None:
        ref = self._selected_ref()
        self.read_button.configure(state=tk.NORMAL if ref else tk.DISABLED)
        if ref:
            self.status_var.set(f"已选择：{ref.name}")

    def load_selected_artifact(self) -> None:
        ref = self._selected_ref()
        if ref is None or self.controller.workspace is None:
            return
        self._set_busy(True, f"正在读取 {ref.name}…")

        def work():
            return self.controller.open_artifact(ref)

        def done(artifact) -> None:
            self._set_text(self.summary_text, artifact_summary_text(artifact))
            llm_ready = self.controller.app_runtime.llm_client is not None
            self.ask_button.configure(state=tk.NORMAL if llm_ready else tk.DISABLED)
            self.status_var.set(f"读取完成：{artifact.name}")
            self._set_busy(False)

        self._background(work, done, "读取文件失败")

    def ask_question(self) -> None:
        question = self.question_entry.get().strip()
        if not question:
            return
        if self.controller.current_artifact is None:
            messagebox.showinfo("尚未读取文件", "请先读取一个文件。")
            return
        llm_client = self.controller.app_runtime.llm_client
        if llm_client is None:
            messagebox.showinfo(
                "模型未配置",
                "请到 Settings → Model 配置 Base URL 与 Model（API Key 从 "
                f"{self.controller.effective_config.api_key_env.value} 环境变量读取）。",
            )
            return

        ref = self._selected_ref()
        artifact = self.controller.current_artifact
        self._set_busy(True, "正在生成回答…")
        self._set_text(self.answer_text, "正在生成回答…")

        def work():
            return llm_client.ask(artifact, question)

        def done(answer: str) -> None:
            self._set_text(self.answer_text, answer)
            self.status_var.set(f"回答完成：{artifact.name}")
            self.controller.record_qa(ref, question)
            self._set_busy(False)

        self._background(work, done, "LLM 调用失败")

    def _background(self, work, done, error_title: str) -> None:
        import threading

        def runner() -> None:
            try:
                result = work()
            except Exception as exc:  # UI 边界：所有后台错误统一呈现
                import logging

                logging.getLogger("hmbuddy.desktop").exception("%s", error_title)
                message = str(exc)
                self.root.after(
                    0,
                    lambda: self._show_background_error(error_title, message),
                )
                return
            self.root.after(0, lambda: done(result))

        threading.Thread(target=runner, daemon=True).start()

    def _show_background_error(self, title: str, message: str) -> None:
        self._set_busy(False)
        self.status_var.set(title)
        messagebox.showerror(title, message)

    def _set_busy(self, busy: bool, status: str | None = None) -> None:
        if status:
            self.status_var.set(status)
        self.root.configure(cursor="watch" if busy else "")
        self.refresh_button.configure(state=tk.DISABLED if busy else tk.NORMAL)
        self.read_button.configure(
            state=tk.DISABLED if busy or self._selected_ref() is None else tk.NORMAL
        )
        llm_ready = self.controller.app_runtime.llm_client is not None
        ask_ready = not busy and self.controller.current_artifact is not None and llm_ready
        self.ask_button.configure(state=tk.NORMAL if ask_ready else tk.DISABLED)

    @staticmethod
    def _set_text(widget: tk.Text, text: str) -> None:
        widget.configure(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        widget.insert("1.0", text)
        widget.configure(state=tk.DISABLED)
