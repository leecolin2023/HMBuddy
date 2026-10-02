"""ArtifactReader Eval（FR-A01 ~ FR-A04 + 第 18 节错误处理 + 第 22-B 节 Parser 成功率）。"""
import base64
from pathlib import Path
import zipfile

import pytest

from evals.conftest import EXPECTED_FIXTURES
from services.artifact_reader import ArtifactReader, read_artifact
from workspace.artifact import make_artifact_id
from workspace.errors import (
    ArtifactNotFoundError,
    ArtifactParseError,
    ArtifactTooLargeError,
    EncryptedArtifactError,
    UnsupportedArtifactTypeError,
    WorkspaceBoundaryError,
)
from workspace.workspace import Workspace

EXPECTED_TYPE = {
    "sample.docx": "docx",
    "complex.docx": "docx",
    "sample.pdf": "pdf",
    "sample_table.pdf": "pdf",
    "sample.xlsx": "xlsx",
    "sample_multisheet.xlsx": "xlsx",
    "sample.xls": "xls",
    "sample.pptx": "pptx",
}


@pytest.mark.parametrize("filename", sorted(EXPECTED_FIXTURES))
def test_parser_success_rate_is_100_percent(reader, fixtures_dir, filename):
    """22-B：Eval fixtures 全部无异常读取。"""
    artifact = reader.read_artifact(fixtures_dir / filename)
    assert artifact.artifact_type == EXPECTED_TYPE[filename]
    assert artifact.blocks, f"{filename} 解析出了空 blocks"


@pytest.mark.parametrize("filename", sorted(EXPECTED_FIXTURES))
def test_provenance_complete(reader, fixtures_dir, filename):
    """FR-A04：provenance 至少包含路径/类型/读取时间/文件修改时间/adapter。"""
    artifact = reader.read_artifact(fixtures_dir / filename)
    provenance = artifact.provenance
    assert provenance["source_path"] == str(fixtures_dir / filename)
    assert provenance["artifact_type"] == EXPECTED_TYPE[filename]
    assert provenance["adapter"]
    assert provenance["parser_library"]
    assert provenance["read_at"]
    assert provenance["file_modified_at"]
    assert provenance["parse_duration_ms"] >= 0
    assert len(provenance["file_sha256"]) == 64
    assert provenance["file_size"] > 0


def test_read_by_ref_uses_ref_artifact_id(fixtures_dir):
    workspace = Workspace(fixtures_dir)
    ref = next(r for r in workspace.list_artifacts() if r.name == "sample.docx")
    artifact = read_artifact(ref, workspace=workspace)
    assert artifact.artifact_id == ref.artifact_id
    assert artifact.path == ref.path
    assert artifact.artifact_id == make_artifact_id(ref.path)


def test_workspace_ref_cannot_escape_trust_domain(fixtures_dir):
    """BUG-007 / AC-H07：Workspace Ref 脱离原 Workspace 时必须拒绝。"""
    workspace = Workspace(fixtures_dir)
    ref = next(r for r in workspace.list_artifacts() if r.name == "sample.docx")
    with pytest.raises(WorkspaceBoundaryError, match="workspace trust boundary"):
        read_artifact(ref)  # 未提供原 Workspace
    # 换一个 Workspace 也不行（信任域不匹配）
    import tempfile

    with tempfile.TemporaryDirectory() as other_root:
        with pytest.raises(WorkspaceBoundaryError):
            read_artifact(ref, workspace=Workspace(other_root))


def test_unsupported_type(tmp_path):
    target = tmp_path / "archive.zip"
    with zipfile.ZipFile(target, "w") as zf:
        zf.writestr("inner.txt", "hello")
    with pytest.raises(UnsupportedArtifactTypeError):
        read_artifact(target)
    binary = tmp_path / "payload.exe"
    binary.write_bytes(b"MZ fake binary")
    with pytest.raises(UnsupportedArtifactTypeError):
        read_artifact(binary)


def test_missing_file(tmp_path):
    with pytest.raises(ArtifactNotFoundError):
        read_artifact(tmp_path / "ghost.docx")


def test_too_large(tmp_path):
    target = tmp_path / "big.docx"
    target.write_bytes(b"x" * 100)
    reader = ArtifactReader(max_file_size=10)
    with pytest.raises(ArtifactTooLargeError):
        reader.read_artifact(target)


def test_workspace_boundary_blocks_outside_path(tmp_path):
    root = tmp_path / "ws"
    root.mkdir()
    outside = tmp_path / "outside.docx"
    outside.write_bytes(b"docx-bytes")
    with pytest.raises(WorkspaceBoundaryError):
        read_artifact(outside, workspace=Workspace(root))
    # 相对路径基于 root 解析后越界同样被拦截
    with pytest.raises(WorkspaceBoundaryError):
        read_artifact("../outside.docx", workspace=Workspace(root))


def test_read_mode_reserved_for_future(fixtures_dir):
    reader = ArtifactReader()
    with pytest.raises(ValueError):
        reader.read_artifact(fixtures_dir / "sample.docx", mode="outline")


def test_corrupt_docx_raises_parse_error(tmp_path):
    target = tmp_path / "broken.docx"
    target.write_bytes(b"this is not a zip archive")
    with pytest.raises(ArtifactParseError) as excinfo:
        read_artifact(target)
    # Phase 1.1：adapter 字段记录的是执行 Provider 的 id（可追溯到插件）
    assert "docx" in excinfo.value.adapter


def test_ole_magic_docx_raises_encrypted(tmp_path):
    """ER-03：OLE 魔数（加密 OOXML / 旧二进制格式）必须明确报加密错误。"""
    from adapters.base import OLE_MAGIC

    target = tmp_path / "protected.docx"
    target.write_bytes(OLE_MAGIC + b"\x00" * 64)
    with pytest.raises(EncryptedArtifactError) as excinfo:
        read_artifact(target)
    assert isinstance(excinfo.value, ArtifactParseError)
    assert excinfo.value.adapter == "DocxAdapter"


def test_ocr_enabled_without_models_degrades_gracefully(tmp_path):
    """开启 OCR 但模型目录缺失：不抛异常，保留 requires_ocr 标记并记录错误。"""
    import io

    pytest.importorskip("fpdf")
    from fpdf import FPDF

    from adapters.base import OcrOptions

    # 生成一个只有图片、没有文本层的 PDF（扫描件形态）
    png_1px = io.BytesIO(
        base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ"
            "AAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
        )
    )
    pdf = FPDF()
    pdf.add_page()
    pdf.image(png_1px, x=50, y=50)
    target = tmp_path / "scanned.pdf"
    pdf.output(str(target))

    reader = ArtifactReader(
        ocr_options=OcrOptions(enable_ocr=True, model_root=tmp_path / "no-such-models")
    )
    artifact = reader.read_artifact(target)
    assert artifact.metadata["requires_ocr"] is True
    assert artifact.metadata["ocr"]["status"] == "error"


def test_encrypted_error_detection_helper():
    from adapters.pdf import PdfAdapter, _is_encryption_error

    # pdfminer 的加密异常类名包含 Password / Encrypt
    class PDFPasswordIncorrect(Exception):
        pass

    class PDFEncryptionError(Exception):
        pass

    assert _is_encryption_error(PDFPasswordIncorrect("bad password"))
    assert _is_encryption_error(PDFEncryptionError("encrypted"))
    assert not _is_encryption_error(Exception("SomeOtherFailure"))
    adapter = PdfAdapter()
    assert adapter.supports(Path("a.pdf"))
    assert not adapter.supports(Path("a.docx"))
