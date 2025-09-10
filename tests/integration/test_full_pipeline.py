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

@pytest.fixture(scope="module")
def extraction_result(runner: CliRunner, mock_pdf_path: Path, tmp_path_factory) -> ArticleExtraction:
    output_dir = tmp_path_factory.mktemp("integration_output")
    output_file = output_dir / "output.json"
    
    args = ["extract", "--pdf", str(mock_pdf_path), "--output", str(output_file)]
    result = runner.invoke(cli, args)
    
    assert result.exit_code == 0, f"CLI command failed with output:\n{result.output}"
    assert output_file.exists(), "Output JSON file was not created."
    
    with open(output_file, 'r') as f:
        data = json.load(f)
    
    return ArticleExtraction(**data)

def test_pipeline_creates_valid_schema(extraction_result: ArticleExtraction):
    assert extraction_result is not None
    assert isinstance(extraction_result, ArticleExtraction)

def test_pipeline_extracts_pico(extraction_result: ArticleExtraction):
    assert extraction_result.pico_elements is not None

def test_pipeline_extracts_claims_with_provenance(extraction_result: ArticleExtraction):
    assert extraction_result.claims is not None
    
    if not extraction_result.claims:
        pytest.skip("No claims were extracted by the LLM from the mock PDF.")

    first_claim = extraction_result.claims[0]
    assert first_claim.claim_text is not None
    assert first_claim.provenance.page_number in [1, 2], \
        f"Claim '{first_claim.claim_text}' was not found on a valid page."

def test_pipeline_generates_summary(extraction_result: ArticleExtraction):
    if extraction_result.claims:
        assert extraction_result.summary is not None
        assert len(extraction_result.summary) > 10
    else:
        pytest.skip("Skipping summary test because no claims were extracted.")

def test_pipeline_parses_bibliography(extraction_result: ArticleExtraction):
    assert extraction_result.bibliography is not None
    assert isinstance(extraction_result.bibliography, dict)