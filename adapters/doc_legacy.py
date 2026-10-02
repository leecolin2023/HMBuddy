"""DOC 遗留格式适配器（移植自 fce 的 .doc 链路）：Word/WPS COM 兼容方式。

仅产出段落级结构（.doc 二进制格式无法无损提取标题层级）；
依赖 pywin32 + 本机 Word/WPS，缺失时返回带明确提示的解析错误。
"""
from __future__ import annotations

import os
from pathlib import Path

from workspace.artifact import Artifact, ArtifactBlock
from workspace.errors import ArtifactParseError

from .base import ArtifactAdapter, assign_block_ids


class DocLegacyAdapter(ArtifactAdapter):
    artifact_type = "doc"
    supported_extensions = (".doc",)
    parser_library = "pywin32 (Word/WPS COM)"

    def read(self, path: Path, artifact_id: str) -> Artifact:
        if os.name != "nt":
            raise ArtifactParseError(
                path,
                adapter=type(self).__name__,
                cause=".doc 为二进制格式，当前平台无 Word/WPS COM 兼容方式，无法读取",
            )

        content, extractor = self._read_via_com(path)
        blocks: list[ArtifactBlock] = []
        line_index = 0
        for raw_line in content.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
            line = raw_line.strip()
            if not line:
                continue
            blocks.append(
                ArtifactBlock("", "paragraph", line, {"line_index": line_index}, {})
            )
            line_index += 1

        metadata = {
            "title": path.stem,
            "line_count": line_index,
            "extractor": extractor,
        }
        assign_block_ids(blocks)
        return self.build_artifact(
            path,
            artifact_id,
            blocks=blocks,
            metadata=metadata,
            content=content,
            file_stat=path.stat(),
        )

    @staticmethod
    def _read_via_com(path: Path) -> tuple[str, str]:
        try:
            import win32com.client as win32  # type: ignore
        except ImportError as exc:
            raise ArtifactParseError(
                path,
                adapter="DocLegacyAdapter",
                cause="缺少 pywin32，无法读取 .doc。请安装 hmbuddy[legacy] 依赖组",
            ) from exc

        prog_ids = ["Word.Application", "Kwps.Application", "Wps.Application"]
        errors: list[str] = []

        for prog_id in prog_ids:
            app = None
            document = None
            try:
                app = win32.DispatchEx(prog_id)
                app.Visible = False
                document = app.Documents.Open(str(path), ReadOnly=True)
                content = (document.Content.Text or "").strip()
                if not content:
                    raise ArtifactParseError(
                        path,
                        adapter="DocLegacyAdapter",
                        cause="{0} 已打开文档，但未读取到文字内容".format(prog_id),
                    )
                return content, prog_id
            except ArtifactParseError:
                raise
            except Exception as exc:
                errors.append("{0}: {1}".format(prog_id, exc))
            finally:
                try:
                    if document is not None:
                        document.Close(False)
                except Exception:
                    pass
                try:
                    if app is not None:
                        app.Quit()
                except Exception:
                    pass

        raise ArtifactParseError(
            path,
            adapter="DocLegacyAdapter",
            cause="无法通过 Word/WPS 打开 .doc：{0}".format(" | ".join(errors)),
        )
