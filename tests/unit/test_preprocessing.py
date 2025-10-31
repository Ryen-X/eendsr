from pathlib import Path

import fitz
import pytest

from evidence_extractor.core.preprocess import (
    clean_and_consolidate_text,
    extract_text_from_doc,
)


@pytest.fixture(scope="module")
def ingested_document(mock_pdf_path: Path) -> fitz.Document:
    doc = fitz.open(str(mock_pdf_path))
    yield doc
    doc.close()


def test_extract_text_from_doc(ingested_document: fitz.Document):
    pages_text = extract_text_from_doc(ingested_document)

    assert isinstance(pages_text, dict)
    assert len(pages_text) == 2
    assert 0 in pages_text
    assert 1 in pages_text
    assert "This is the first page." in pages_text[0]
    assert "simple text for extraction" in pages_text[0]
    assert "This is the second page" in pages_text[1]
    assert "hyphen-\nated word" in pages_text[1]


def test_clean_and_consolidate_text():
    mock_pages_text = {
        0: "This is the first page.",
        1: "This is the second page, with a hyphen-\nated word.",
        2: "And a page number\n 3 \n at the bottom.",
    }

    text_with_newlines, consolidated_text = clean_and_consolidate_text(mock_pages_text)
    assert "hyphenated word" in text_with_newlines
    assert "\n" in text_with_newlines
    assert "hyphenated word" in consolidated_text
    assert "page number at the bottom" in consolidated_text
    assert "\n" not in consolidated_text
    assert "  " not in consolidated_text
