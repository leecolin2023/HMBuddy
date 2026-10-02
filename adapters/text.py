"""纯文本 Adapter（移植自 fce 的 extract_plain_text + 多编码回退）。

覆盖 txt / md / csv / log 等办公文本格式；编码按 utf-8-sig → utf-8 →
gb18030 → utf-16 → latin-1 顺序回退（内网历史文件常见 GBK 系编码）。
"""
from __future__ import annotations

from pathlib import Path

from workspace.artifact import Artifact, ArtifactBlock, ArtifactLocator

from .base import ArtifactAdapter, assign_block_ids

TEXT_ENCODINGS = ("utf-8-sig", "utf-8", "gb18030", "utf-16", "latin-1")


def read_text_with_fallbacks(path: Path) -> str:
    for encoding in TEXT_ENCODINGS:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="ignore")


class TextAdapter(ArtifactAdapter):
    artifact_type = "text"
    supported_extensions = (".txt", ".md", ".markdown", ".rst", ".csv", ".tsv", ".log")
    parser_library = "stdlib"

    def read(self, path: Path, artifact_id: str) -> Artifact:
        try:
            text = read_text_with_fallbacks(path)
        except Exception:
            raise  # Reader 统一包装为 ArtifactParseError

        blocks: list[ArtifactBlock] = []
        line_index = 0
        for raw_line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
            line = raw_line.strip()
            line_index += 1  # line_index 记录原始行号（含空行），便于定位
            if not line:
                continue
            blocks.append(
                ArtifactBlock(
                    "",
                    "paragraph",
                    line,
                    {"line_index": line_index - 1},
                    {},
                    locator=ArtifactLocator("text", {"line_index": line_index - 1}),
                )
            )

        metadata = {
            "line_count": line_index,
            "title": path.stem,
        }
        content = text.strip()
        assign_block_ids(blocks)
        return self.build_artifact(
            path,
            artifact_id,
            blocks=blocks,
            metadata=metadata,
            content=content,
            file_stat=path.stat(),
            # artifact_type 按具体扩展名区分（txt/md/csv），供上层语义化使用
            artifact_type=path.suffix.lstrip(".").lower(),
        )
