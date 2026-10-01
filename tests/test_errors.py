"""错误类型体系单元测试（规格第 18 节 ER-01 ~ ER-05）。"""
import pytest

from workspace.errors import (
    ArtifactNotFoundError,
    ArtifactParseError,
    ArtifactRuntimeError,
    ArtifactTooLargeError,
    EncryptedArtifactError,
    UnsupportedArtifactTypeError,
    WorkspaceBoundaryError,
)


def test_error_hierarchy():
    for exc_type in (
        UnsupportedArtifactTypeError,
        ArtifactNotFoundError,
        WorkspaceBoundaryError,
        ArtifactTooLargeError,
        ArtifactParseError,
    ):
        assert issubclass(exc_type, ArtifactRuntimeError)
    assert issubclass(EncryptedArtifactError, ArtifactParseError)


def test_unsupported_type_message_contains_path_and_extension():
    exc = UnsupportedArtifactTypeError("D:/ws/old.doc", extension=".doc")
    assert "old.doc" in str(exc)
    assert ".doc" in str(exc)
    assert exc.extension == ".doc"


def test_parse_error_records_adapter_and_cause():
    cause = ValueError("boom")
    exc = ArtifactParseError("D:/ws/a.docx", adapter="DocxAdapter", cause=cause)
    assert exc.adapter == "DocxAdapter"
    assert exc.cause is cause
    assert "DocxAdapter" in str(exc)
    assert "boom" in str(exc)


def test_encrypted_error_is_parse_error_with_reason():
    exc = EncryptedArtifactError("D:/ws/a.xlsx", adapter="XlsxAdapter", reason="pwd")
    assert isinstance(exc, ArtifactParseError)
    assert exc.reason == "pwd"


def test_boundary_and_too_large_messages():
    boundary = WorkspaceBoundaryError("D:/outside/x.docx", "D:/ws")
    assert "D:/ws" in str(boundary)
    assert "outside" in str(boundary)
    too_large = ArtifactTooLargeError("D:/ws/big.pdf", size=100, max_size=50)
    assert too_large.size == 100
    assert too_large.max_size == 50


def test_artifact_not_found():
    exc = ArtifactNotFoundError("D:/ws/ghost.docx")
    assert "ghost.docx" in str(exc)
