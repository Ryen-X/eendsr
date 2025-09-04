import pytest
from unittest.mock import MagicMock
from evidence_extractor.extraction.llm_orchestrator import orchestrate_llm_extraction

@pytest.fixture
def mock_gemini_client():
    return MagicMock()

def test_orchestrator_happy_path(mock_gemini_client):
    mock_response = """
    {
        "pico": {
            "population": "Test Population",
            "intervention": "Test Intervention",
            "comparison": "Test Comparison",
            "outcome": "Test Outcome"
        },
        "quality": {
            "score_name": "Methodological Quality",
            "score_value": "High",
            "justification": "It was a test RCT."
        },
        "claims": [
            {"claim_text": "Claim 1"},
            {"claim_text": "Claim 2"}
        ]
    }
    """
    mock_gemini_client.query.return_value = mock_response
    result = orchestrate_llm_extraction(mock_gemini_client, "some text")
    assert result is not None
    assert result["pico"]["population"] == "Test Population"
    assert result["quality"]["score_value"] == "High"
    assert len(result["claims"]) == 2
    assert result["claims"][0]["claim_text"] == "Claim 1"

def test_orchestrator_malformed_json(mock_gemini_client):
    mock_response = '{"pico": {"population": "Test"}'
    mock_gemini_client.query.return_value = mock_response
    result = orchestrate_llm_extraction(mock_gemini_client, "some text")
    assert result is None

def test_orchestrator_no_response(mock_gemini_client):
    mock_gemini_client.query.return_value = None
    result = orchestrate_llm_extraction(mock_gemini_client, "some text")
    assert result is None