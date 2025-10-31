from pathlib import Path

import fitz

from evidence_extractor.core.ingest import ingest_pdf


def test_ingest_pdf_success(mock_pdf_path: Path):
    document = ingest_pdf(str(mock_pdf_path))
    assert document is not None
    assert isinstance(document, fitz.Document)
    assert document.page_count == 2
    document.close()


def test_ingest_pdf_file_not_found():
    non_existent_path = "path/to/non_existent_file.pdf"
    document = ingest_pdf(non_existent_path)
    assert document is None


def test_ingest_pdf_not_a_pdf(tmp_path: Path):
    not_a_pdf = tmp_path / "document.txt"
    not_a_pdf.write_text("This is not a PDF.")

    document = ingest_pdf(str(not_a_pdf))
    assert document is None
