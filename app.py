"""Phase 1 最小演示（规格第 30 节）。

用法：
  python app.py <文件路径>              # 读取文件 → 摘要 → 交互问答（需配置 LLM）
  python app.py <文件路径> --no-llm     # 只读取并打印摘要
  python app.py <文件路径> --show-context
  python app.py <目录路径>              # 扫描目录，列出可发现的 Artifact

LLM 环境变量（OpenAI 兼容协议，可指向内网私有化端点）：
  HMBUDDY_LLM_BASE_URL / HMBUDDY_LLM_MODEL / HMBUDDY_LLM_API_KEY
"""
from __future__ import annotations

import argparse
import logging
import sys
from collections import Counter
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from llm.client import LLMError, client_from_env  # noqa: E402
from llm.context import artifact_to_context  # noqa: E402
from services.artifact_reader import read_artifact  # noqa: E402
from workspace.errors import ArtifactRuntimeError  # noqa: E402
from workspace.workspace import Workspace  # noqa: E402

BLOCK_TYPE_LABELS = {
    "heading": "Heading",
    "paragraph": "Paragraph",
    "list_item": "ListItem",
    "table": "Table",
    "image_reference": "Image",
    "text_block": "TextBlock",
    "textbox": "Textbox",
    "slide": "Slide",
}


def print_summary(artifact) -> None:
    """按 Artifact 的通用字段打印摘要，不出现格式判断（P2）。"""
    print("成功读取：")
    print(f"  类型：{artifact.artifact_type.upper()}")
    title = artifact.metadata.get("title")
    if title:
        print(f"  标题：{title}")
    counts = Counter(block.block_type for block in artifact.blocks)
    summary = "  ".join(
        f"{BLOCK_TYPE_LABELS.get(block_type, block_type)}：{count}"
        for block_type, count in sorted(counts.items())
    )
    if summary:
        print(f"  {summary}")
    sheets = artifact.metadata.get("sheets")
    if sheets:
        print("  Sheets：" + "、".join(sheet["name"] for sheet in sheets))
    page_count = artifact.metadata.get("page_count")
    if page_count is not None:
        print(f"  Pages：{page_count}")
    provenance = artifact.provenance
    print(
        f"  解析耗时：{provenance.get('parse_duration_ms', '?')} ms"
        f"（adapter={provenance.get('adapter', '?')}）"
    )


def scan_directory(directory: Path) -> int:
    workspace = Workspace(directory)
    refs = workspace.list_artifacts()
    print(f"Workspace: {workspace.root_path}")
    print(f"发现 {len(refs)} 个支持的文件：")
    for ref in refs:
        print(f"  [{ref.artifact_type.upper():4}] {ref.path}  ({ref.size} bytes)")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="HMBuddy Phase 1 — Local Office Artifact Runtime 演示"
    )
    parser.add_argument("path", help="要读取的文件路径，或要扫描的目录路径")
    parser.add_argument("--scan", action="store_true", help="仅扫描目录，不读取内容")
    parser.add_argument("--no-llm", action="store_true", help="不进入问答环节")
    parser.add_argument(
        "--show-context", action="store_true", help="打印将交给 LLM 的 Context"
    )
    parser.add_argument("--max-size-mb", type=int, default=50, help="读取大小阈值（MB）")
    args = parser.parse_args(argv)

    target = Path(args.path)
    if args.scan or target.is_dir():
        try:
            return scan_directory(target)
        except (FileNotFoundError, NotADirectoryError) as exc:
            print(f"[错误] {exc}")
            return 1

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s"
    )

    try:
        artifact = read_artifact(target, max_file_size=args.max_size_mb * 1024 * 1024)
    except ArtifactRuntimeError as exc:
        print(f"[读取失败] {type(exc).__name__}: {exc}")
        return 1

    print_summary(artifact)

    if args.show_context:
        print("\n----- LLM Context -----")
        print(artifact_to_context(artifact))

    if args.no_llm:
        return 0

    client = client_from_env()
    if client is None:
        print(
            "\n未配置 LLM（HMBUDDY_LLM_BASE_URL / HMBUDDY_LLM_MODEL），跳过问答。\n"
            "可加 --show-context 查看将交给 LLM 的上下文。"
        )
        return 0

    print(f"\nLLM: {client.model_name}。请输入问题（空行或 q 退出）：")
    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not question or question.lower() in {"q", "quit", "exit"}:
            break
        try:
            print()
            print(client.ask(artifact, question))
            print()
        except LLMError as exc:
            print(f"[LLM 错误] {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
