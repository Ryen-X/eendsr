import pytest
from unittest.mock import MagicMock
from evidence_extractor.extraction.summarization import generate_summary
from evidence_extractor.models.schemas import Claim, Provenance

@pytest.fixture
def mock_gemini_client():
    return MagicMock()

@pytest.fixture
def mock_claims_list():
    p = Provenance(source_filename="test.pdf", page_number=1)
    return [Claim(claim_text="Finding 1.", provenance=p), Claim(claim_text="Finding 2.", provenance=p)]

def test_generate_summary_happy_path(mock_gemini_client, mock_claims_list):
    mock_response = "This is a synthesized summary of the findings."
    mock_gemini_client.query.return_value = mock_response
    summary = generate_summary(mock_gemini_client, mock_claims_list)
    assert summary is not None
    assert summary == mock_response

def test_generate_summary_no_response(mock_gemini_client, mock_claims_list):
    mock_gemini_client.query.return_value = None
    summary = generate_summary(mock_gemini_client, mock_claims_list)
    assert summary is None

def test_generate_summary_no_claims(mock_gemini_client):
    summary = generate_summary(mock_gemini_client, [])
    assert summary is None
    mock_gemini_client.query.assert_not_called()