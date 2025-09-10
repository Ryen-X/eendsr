import pytest
import json
from click.testing import CliRunner
from pathlib import Path
from evidence_extractor.cli.main import cli
from evidence_extractor.models.schemas import ArticleExtraction

pytestmark = pytest.mark.integration

@pytest.fixture(scope="module")
def runner():
    return CliRunner()

def test_full_extraction_pipeline(runner: CliRunner, mock_pdf_path: Path, tmp_path: Path):
    output_file = tmp_path / "output.json"
    args = [
        "extract",
        "--pdf",
        str(mock_pdf_path),
        "--output",
        str(output_file),
    ]

    result = runner.invoke(cli, args)
    assert result.exit_code == 0, f"CLI command failed with output:\n{result.output}"
    assert "Processing complete." in result.output
    assert output_file.exists(), "Output JSON file was not created."
    try:
        with open(output_file, 'r') as f:
            data = json.load(f)
        extraction = ArticleExtraction(**data)
    except Exception as e:
        pytest.fail(f"Output JSON is not valid or does not match the ArticleExtraction schema. Error: {e}")

    assert extraction.source_filename == str(mock_pdf_path)
    assert extraction.title is not None or extraction.claims is not None