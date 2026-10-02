"""HMBuddy Phase 2 desktop entry.

A thin Tkinter shell over the Phase 1 runtime:
Workspace -> ArtifactRef -> read_artifact -> optional LLM Q&A.
"""
from __future__ import annotations

import logging
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from llm.client import LLMError, client_from_env
from services.artifact_reader import read_artifact
from workspace.errors import ArtifactRuntimeError
from workspace.workspace import Workspace

from .presenter import artifact_summary_text, format_datetime, format_file_size

LOGGER = logging.getLogger("hmbuddy.desktop")


class HMBuddyDesktopApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("HMBuddy · 本地办公助手")
        self.root.geometry("1120x760")
        self.root.minsize(920, 620)

        self.workspace: Workspace | None = None
        self.refs = []
        self.current_artifact = None
        self.llm_client = client_from_env()

        self.workspace_var = tk.StringVar()
        self.status_var = tk.StringVar(value="请选择一个工作目录")
        self.file_count_var = tk.StringVar(value="0 个文件")
        self.llm_status_var = tk.StringVar(
            value=f"模型：{self.llm_client.model_name}" if self.llm_client else "模型：未配置"
        )

        self._configure_style()
        self._build_ui()

    def _configure_style(self) -> None:
        style = ttk.Style()
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("Title.TLabel", font=("Microsoft YaHei UI", 18, "bold"))
        style.configure("Subtitle.TLabel", font=("Microsoft YaHei UI", 10))
        style.configure("Section.TLabelframe.Label", font=("Microsoft YaHei UI", 10, "bold"))
        style.configure("Treeview", rowheight=28, font=("Microsoft YaHei UI", 9))
        style.configure("Treeview.Heading", font=("Microsoft YaHei UI", 9, "bold"))

    def _build_ui(self) -> None:
        container = ttk.Frame(self.root, padding=18)
        container.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(container)
        header.pack(fill=tk.X, pady=(0, 14))
        ttk.Label(header, text="HMBuddy", style="Title.TLabel").pack(side=tk.LEFT)
        ttk.Label(
            header,
            text="  本地办公助手 · Phase 2 Desktop Entry",
            style="Subtitle.TLabel",
        ).pack(side=tk.LEFT, pady=(7, 0))
        ttk.Label(header, textvariable=self.llm_status_var).pack(side=tk.RIGHT, pady=(7, 0))

        workspace_frame = ttk.LabelFrame(
            container, text="工作区", style="Section.TLabelframe", padding=10
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

        main = ttk.Panedwindow(container, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(main, padding=(0, 0, 8, 0))
        right = ttk.Frame(main, padding=(8, 0, 0, 0))
        main.add(left, weight=2)
        main.add(right, weight=3)

        left_header = ttk.Frame(left)
        left_header.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(left_header, text="工作区文件", font=("Microsoft YaHei UI", 10, "bold")).pack(
            side=tk.LEFT
        )
        ttk.Label(left_header, textvariable=self.file_count_var).pack(side=tk.RIGHT)

        columns = ("type", "name", "size", "modified")
        self.file_tree = ttk.Treeview(left, columns=columns, show="headings", selectmode="browse")
        self.file_tree.heading("type", text="类型")
        self.file_tree.heading("name", text="文件名")
        self.file_tree.heading("size", text="大小")
        self.file_tree.heading("modified", text="修改时间")
        self.file_tree.column("type", width=62, anchor=tk.CENTER, stretch=False)
        self.file_tree.column("name", width=280, anchor=tk.W)
        self.file_tree.column("size", width=82, anchor=tk.E, stretch=False)
        self.file_tree.column("modified", width=142, anchor=tk.CENTER, stretch=False)

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
            overview_actions,
            text="双击文件也可读取；读取沿用 Phase 1 Artifact Runtime",
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
        answer_scroll = ttk.Scrollbar(qa_tab, orient=tk.VERTICAL, command=self.answer_text.yview)
        self.answer_text.configure(yscrollcommand=answer_scroll.set)
        self.answer_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(6, 0))
        answer_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=(6, 0))
        self._set_text(
            self.answer_text,
            "读取文件后即可提问。若顶部显示“模型：未配置”，请先配置 HMBUDDY_LLM_* 环境变量。",
        )

        status = ttk.Frame(container)
        status.pack(fill=tk.X, pady=(10, 0))
        ttk.Separator(status, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(0, 8))
        ttk.Label(status, textvariable=self.status_var).pack(side=tk.LEFT)

    def choose_workspace(self) -> None:
        initial = self.workspace_var.get().strip() or str(Path.cwd())
        selected = filedialog.askdirectory(title="选择 HMBuddy 工作目录", initialdir=initial)
        if selected:
            self.workspace_var.set(selected)
            self.open_workspace_path()

    def choose_file(self) -> None:
        selected = filedialog.askopenfilename(
            title="选择办公文件",
            filetypes=[
                ("Office 文件", "*.docx *.pdf *.xlsx *.pptx"),
                ("Word", "*.docx"),
                ("PDF", "*.pdf"),
                ("Excel", "*.xlsx"),
                ("PowerPoint", "*.pptx"),
            ],
        )
        if not selected:
            return
        path = Path(selected).resolve()
        self.workspace_var.set(str(path.parent))
        self.open_workspace_path(select_path=path)

    def open_workspace_path(self, select_path: Path | None = None) -> None:
        raw = self.workspace_var.get().strip()
        if not raw:
            self.status_var.set("请输入或选择工作目录")
            return
        try:
            workspace = Workspace(raw)
            refs = workspace.list_artifacts()
        except (FileNotFoundError, NotADirectoryError, OSError) as exc:
            messagebox.showerror("工作区不可用", str(exc))
            self.status_var.set("工作区加载失败")
            return

        self.workspace = workspace
        self.refs = refs
        self.workspace_var.set(str(workspace.root_path))
        self._render_refs(select_path=select_path)
        self.status_var.set(f"已加载工作区：{workspace.root_path}")

    def refresh_workspace(self) -> None:
        if not self.workspace_var.get().strip():
            self.choose_workspace()
            return
        self.open_workspace_path()

    def _render_refs(self, select_path: Path | None = None) -> None:
        self.current_artifact = None
        self.read_button.configure(state=tk.DISABLED)
        self.ask_button.configure(state=tk.DISABLED)
        self._set_text(self.summary_text, "请选择工作区中的文件。")
        self._set_text(self.answer_text, "读取文件后即可提问。")

        for item in self.file_tree.get_children():
            self.file_tree.delete(item)

        selected_iid = None
        for index, ref in enumerate(self.refs):
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

        self.file_count_var.set(f"{len(self.refs)} 个文件")
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
            return self.refs[int(selected[0])]
        except (ValueError, IndexError):
            return None

    def _on_file_selected(self, _event=None) -> None:
        ref = self._selected_ref()
        self.read_button.configure(state=tk.NORMAL if ref else tk.DISABLED)
        if ref:
            self.status_var.set(f"已选择：{ref.name}")

    def load_selected_artifact(self) -> None:
        ref = self._selected_ref()
        if ref is None:
            return
        self._set_busy(True, f"正在读取 {ref.name}…")

        def work():
            return read_artifact(ref)

        def done(artifact) -> None:
            self.current_artifact = artifact
            self._set_text(self.summary_text, artifact_summary_text(artifact))
            self.ask_button.configure(
                state=tk.NORMAL if self.llm_client is not None else tk.DISABLED
            )
            self.status_var.set(f"读取完成：{artifact.name}")
            self._set_busy(False)

        self._background(work, done, "读取文件失败")

    def ask_question(self) -> None:
        question = self.question_entry.get().strip()
        if not question:
            return
        if self.current_artifact is None:
            messagebox.showinfo("尚未读取文件", "请先读取一个文件。")
            return
        if self.llm_client is None:
            messagebox.showinfo(
                "模型未配置",
                "请配置 HMBUDDY_LLM_BASE_URL、HMBUDDY_LLM_MODEL 和可选的 HMBUDDY_LLM_API_KEY。",
            )
            return

        artifact = self.current_artifact
        self._set_busy(True, "正在生成回答…")
        self._set_text(self.answer_text, "正在生成回答…")

        def work():
            return self.llm_client.ask(artifact, question)

        def done(answer: str) -> None:
            self._set_text(self.answer_text, answer)
            self.status_var.set(f"回答完成：{artifact.name}")
            self._set_busy(False)

        self._background(work, done, "LLM 调用失败")

    def _background(self, work, done, error_title: str) -> None:
        def runner() -> None:
            try:
                result = work()
            except (ArtifactRuntimeError, LLMError, OSError, RuntimeError) as exc:
                LOGGER.exception("%s", error_title)
                self.root.after(0, lambda: self._show_background_error(error_title, exc))
                return
            except Exception as exc:  # defensive UI boundary
                LOGGER.exception("unexpected desktop error")
                self.root.after(0, lambda: self._show_background_error(error_title, exc))
                return
            self.root.after(0, lambda: done(result))

        threading.Thread(target=runner, daemon=True).start()

    def _show_background_error(self, title: str, exc: Exception) -> None:
        self._set_busy(False)
        self.status_var.set(title)
        messagebox.showerror(title, f"{type(exc).__name__}: {exc}")

    def _set_busy(self, busy: bool, status: str | None = None) -> None:
        if status:
            self.status_var.set(status)
        cursor = "watch" if busy else ""
        self.root.configure(cursor=cursor)
        self.refresh_button.configure(state=tk.DISABLED if busy else tk.NORMAL)
        self.read_button.configure(
            state=tk.DISABLED if busy or self._selected_ref() is None else tk.NORMAL
        )
        ask_ready = (
            not busy and self.current_artifact is not None and self.llm_client is not None
        )
        self.ask_button.configure(state=tk.NORMAL if ask_ready else tk.DISABLED)

    @staticmethod
    def _set_text(widget: tk.Text, text: str) -> None:
        widget.configure(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        widget.insert("1.0", text)
        widget.configure(state=tk.DISABLED)


def main() -> int:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s"
    )
    root = tk.Tk()
    HMBuddyDesktopApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
