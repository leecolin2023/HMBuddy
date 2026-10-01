"""领域模型单元测试（规格 Step 2：领域模型稳定之前不开始 Adapter）。"""
from workspace.artifact import Artifact, ArtifactBlock, ArtifactRef, make_artifact_id


def test_make_artifact_id_is_stable(tmp_path):
    file_path = tmp_path / "a.docx"
    file_path.write_bytes(b"x")
    first = make_artifact_id(file_path)
    second = make_artifact_id(file_path)
    assert first == second
    assert first.startswith("a_")


def test_make_artifact_id_distinguishes_paths(tmp_path):
    path_a = tmp_path / "a.docx"
    path_b = tmp_path / "sub"
    path_b.mkdir()
    file_b = path_b / "a.docx"
    path_a.write_bytes(b"x")
    file_b.write_bytes(b"x")
    assert make_artifact_id(path_a) != make_artifact_id(file_b)


def test_artifact_block_defaults_are_independent():
    block1 = ArtifactBlock(block_id="b0001", block_type="paragraph", text="hello")
    block2 = ArtifactBlock(block_id="b0002", block_type="paragraph", text="world")
    assert block1.text == "hello"
    assert block2.text is not None
    block1.location["page"] = 1
    assert "page" not in block2.location
    block1.metadata["level"] = 2
    assert "level" not in block2.metadata


def test_artifact_defaults_are_independent():
    artifact1 = Artifact(
        artifact_id="a_1", name="x.docx", path="/tmp/x.docx", artifact_type="docx"
    )
    artifact2 = Artifact(
        artifact_id="a_2", name="y.docx", path="/tmp/y.docx", artifact_type="docx"
    )
    artifact1.blocks.append(ArtifactBlock("b0001", "paragraph", "t"))
    assert artifact2.blocks == []
    artifact1.metadata["k"] = 1
    assert "k" not in artifact2.metadata


def test_artifact_blocks_of_type():
    artifact = Artifact(
        artifact_id="a_1", name="x.docx", path="/tmp/x.docx", artifact_type="docx",
        blocks=[
            ArtifactBlock("b0001", "heading", "标题"),
            ArtifactBlock("b0002", "paragraph", "正文"),
            ArtifactBlock("b0003", "heading", "标题2"),
        ],
    )
    headings = artifact.blocks_of_type("heading")
    assert [b.text for b in headings] == ["标题", "标题2"]


def test_artifact_ref_fields():
    from datetime import datetime, timezone

    ref = ArtifactRef(
        artifact_id="a_abc",
        name="报表.xlsx",
        path="D:/ws/报表.xlsx",
        extension="xlsx",
        size=123,
        modified_at=datetime(2026, 10, 1, tzinfo=timezone.utc),
        artifact_type="xlsx",
    )
    assert ref.artifact_type == "xlsx"
    assert ref.extension == "xlsx"
    assert ref.size == 123
