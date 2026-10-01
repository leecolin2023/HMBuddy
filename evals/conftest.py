"""evals 共享 fixtures：把 6 个标准样例文件各读取一次，供 Parser / Context / QA Eval 复用。"""
from pathlib import Path

import pytest

from services.artifact_reader import ArtifactReader

FIXTURES_DIR = Path(__file__).parent / "fixtures"

EXPECTED_FIXTURES = {
    "sample.docx",
    "complex.docx",
    "sample.pdf",
    "sample.xlsx",
    "sample_multisheet.xlsx",
    "sample.pptx",
}


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    missing = EXPECTED_FIXTURES - {p.name for p in FIXTURES_DIR.iterdir()}
    if missing:
        pytest.fail(
            f"缺少 fixtures: {sorted(missing)}，请先运行 "
            f"python evals/fixtures/generate_fixtures.py"
        )
    return FIXTURES_DIR


@pytest.fixture(scope="session")
def reader() -> ArtifactReader:
    return ArtifactReader()


@pytest.fixture(scope="session")
def docx_standard(reader, fixtures_dir):
    return reader.read_artifact(fixtures_dir / "sample.docx")


@pytest.fixture(scope="session")
def docx_complex(reader, fixtures_dir):
    return reader.read_artifact(fixtures_dir / "complex.docx")


@pytest.fixture(scope="session")
def pdf_standard(reader, fixtures_dir):
    return reader.read_artifact(fixtures_dir / "sample.pdf")


@pytest.fixture(scope="session")
def xlsx_standard(reader, fixtures_dir):
    return reader.read_artifact(fixtures_dir / "sample.xlsx")


@pytest.fixture(scope="session")
def xlsx_multisheet(reader, fixtures_dir):
    return reader.read_artifact(fixtures_dir / "sample_multisheet.xlsx")


@pytest.fixture(scope="session")
def pptx_standard(reader, fixtures_dir):
    return reader.read_artifact(fixtures_dir / "sample.pptx")
