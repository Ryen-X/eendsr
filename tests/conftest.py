import pytest
import fitz 
from pathlib import Path
from typing import Generator

@pytest.fixture(scope="session")
def mock_pdf_path(tmp_path_factory) -> Generator[Path, None, None]:
    pdf_dir = tmp_path_factory.mktemp("pdf_data")
    file_path = pdf_dir / "test_document.pdf"

    doc = fitz.open()
    
    page1 = doc.new_page()
    page1.insert_text((50, 72), "This is the first page.")
    page1.insert_text((50, 100), "It contains some simple text for extraction.")

    page2 = doc.new_page()
    page2.insert_text((50, 72), "This is the second page, with a hyphen-\nated word.")
    page2.insert_text((50, 100), "And a page number\n 2 \n at the bottom.")

    doc.save(file_path)
    doc.close()
    
    yield file_path