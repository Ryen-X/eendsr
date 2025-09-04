import pytest
from evidence_extractor.models.schemas import (
    ArticleExtraction,
    Claim,
    Provenance,
    ValidationStatus,
    CorrectionMetadata
)

def test_provenance_creation():
    p = Provenance(source_filename="test.pdf", page_number=1)
    assert p.source_filename == "test.pdf"
    assert p.page_number == 1
    assert p.line_number is None

def test_claim_creation_and_defaults():
    p = Provenance(source_filename="test.pdf", page_number=5)
    claim = Claim(claim_text="This is a test claim.", provenance=p)
    
    assert claim.claim_text == "This is a test claim."
    assert claim.provenance.page_number == 5
    assert claim.linked_citations == []
    assert claim.uncertainty_annotation is None
    assert isinstance(claim.correction_metadata, CorrectionMetadata)
    assert claim.correction_metadata.status == ValidationStatus.UNVERIFIED
    assert claim.correction_metadata.reviewer_comment is None

def test_article_extraction_creation_and_defaults():
    article = ArticleExtraction(source_filename="article.pdf")
    
    assert article.source_filename == "article.pdf"
    assert article.authors == []
    assert article.claims == []
    assert article.quality_scores == []
    assert article.tables == []
    assert article.figures == []
    assert article.bibliography == {}
    assert article.summary is None
    assert article.pico_elements is None
    assert article.records_excluded_count == 0

def test_correction_metadata_defaults():
    meta = CorrectionMetadata()
    assert meta.status == ValidationStatus.UNVERIFIED
    assert meta.reviewer_comment is None
    assert meta.last_reviewed is None

def test_validation_status_enum():
    assert ValidationStatus.UNVERIFIED == "unverified"
    assert ValidationStatus.VERIFIED == "verified"
    assert ValidationStatus.REJECTED == "rejected"
    assert ValidationStatus.EDITED == "edited"