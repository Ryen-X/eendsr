from unittest.mock import MagicMock

import pytest

from evidence_extractor.extraction.uncertainty import annotate_claims_in_batch
from evidence_extractor.models.schemas import Claim, Provenance


@pytest.fixture
def mock_gemini_client():
    return MagicMock()


@pytest.fixture
def mock_claims_list():
    p = Provenance(source_filename="test.pdf", page_number=1)
    return [
        Claim(claim_text="Claim A", provenance=p),
        Claim(claim_text="Claim B", provenance=p),
    ]


def test_annotate_claims_in_batch_happy_path(mock_gemini_client, mock_claims_list):
    mock_response = """
    [
        {"claim_index": 1, "annotation": "Confidence: High. "
                                         "Justification: Strong words."},
        {"claim_index": 2, "annotation": "Confidence: Low. Justification: Weak words."}
    ]
    """
    mock_gemini_client.query.return_value = mock_response
    annotate_claims_in_batch(mock_gemini_client, mock_claims_list)
    assert mock_claims_list[0].uncertainty_annotation is not None
    assert "Confidence: High" in mock_claims_list[0].uncertainty_annotation
    assert mock_claims_list[1].uncertainty_annotation is not None
    assert "Confidence: Low" in mock_claims_list[1].uncertainty_annotation


def test_annotate_claims_in_batch_malformed_json(mock_gemini_client, mock_claims_list):
    mock_response = '[{"claim_index": 1, "annotation": "Confidence: High"}'
    mock_gemini_client.query.return_value = mock_response
    annotate_claims_in_batch(mock_gemini_client, mock_claims_list)
    assert mock_claims_list[0].uncertainty_annotation is None
    assert mock_claims_list[1].uncertainty_annotation is None
