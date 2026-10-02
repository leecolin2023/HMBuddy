from datetime import datetime, timezone

from desktop.presenter import artifact_summary_text, format_file_size
from workspace.artifact import Artifact, ArtifactBlock


def test_format_file_size():
    assert format_file_size(512) == "512 B"
    assert format_file_size(1536) == "1.5 KB"
    assert format_file_size(2 * 1024 * 1024) == "2.0 MB"


def test_artifact_summary_contains_core_information():
    artifact = Artifact(
        artifact_id="a_demo",
        name="demo.docx",
        path="/workspace/demo.docx",
        artifact_type="docx",
        metadata={"title": "Demo"},
        content="hello world",
        blocks=[
            ArtifactBlock(block_id="b1", block_type="heading", text="Demo"),
            ArtifactBlock(block_id="b2", block_type="paragraph", text="hello world"),
        ],
        provenance={"adapter": "DocxAdapter", "parse_duration_ms": 12},
    )

    text = artifact_summary_text(artifact)

    assert "demo.docx" in text
    assert "DOCX" in text
    assert "Heading: 1" in text
    assert "Paragraph: 1" in text
    assert "DocxAdapter" in text
    assert "a_demo" in text
    assert "hello world" in text


def test_artifact_preview_is_bounded():
    artifact = Artifact(
        artifact_id="a_demo",
        name="demo.pdf",
        path="/workspace/demo.pdf",
        artifact_type="pdf",
        content="x" * 5000,
        provenance={},
    )
    text = artifact_summary_text(artifact)
    assert "预览已截断" in text
    assert len(text) < 4000
