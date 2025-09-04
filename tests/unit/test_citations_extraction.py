import pytest
from evidence_extractor.extraction.citations import (
    find_references_section,
    parse_bibliography,
    link_in_text_citations
)
from evidence_extractor.models.schemas import BibliographyItem

@pytest.fixture
def mock_document_text() -> str:
    return """
Introduction
This is the main body of the paper. We cite Smith (2022) and Jones et al. [2021].
The findings are significant. Another citation is to Miller (2020).

2. Methods
More text here.

REFERENCES
[1] Smith, J. (2022). A Study of Things. Journal of Science, 1(1), 1-10.
[2] Jones, A., & Baker, C. (2021). Another Study. Research Today, 2(3), 20-30.

Miller, K. (2020). Older Research. Legacy Publishing.
    """

def test_find_references_section(mock_document_text: str):
    result = find_references_section(mock_document_text)
    assert result is not None
    references_text, start_index = result
    assert "[1] Smith, J. (2022)" in references_text
    assert "Introduction" not in references_text
    assert start_index > 0

def test_find_references_section_not_found():
    text = "This document has no references section."
    result = find_references_section(text)
    assert result is None

def test_parse_bibliography(mock_document_text: str):
    references_text, _ = find_references_section(mock_document_text)
    bibliography = parse_bibliography(references_text)
    assert len(bibliography) == 3
    assert any("Smith2022" in key for key in bibliography)
    assert any("Jones2021" in key for key in bibliography)
    assert any("Miller2020" in key for key in bibliography)
    smith_key = next(key for key in bibliography if "Smith2022" in key)
    assert bibliography[smith_key].full_citation.startswith("[1] Smith, J.")

def test_link_in_text_citations():
    main_body = "We cite Smith (2022) and Jones et al. [2021]. Not Miller."
    bibliography = {
        "Smith2022": BibliographyItem(citation_key="Smith2022", full_citation="Smith, J. (2022)."),
        "Jones2021": BibliographyItem(citation_key="Jones2021", full_citation="Jones, A. (2021)."),
        "Miller2020": BibliographyItem(citation_key="Miller2020", full_citation="Miller, K. (2020)."),
    }
    links = link_in_text_citations(main_body, bibliography)
    assert len(links) == 2
    assert "Smith2022" in links
    assert "Jones2021" in links
    assert "Miller2020" not in links
    assert "Smith (2022)" in links["Smith2022"]