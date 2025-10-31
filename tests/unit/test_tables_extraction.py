import base64
from unittest.mock import MagicMock

import pytest

from evidence_extractor.extraction.tables import extract_tables_with_llm

MINIMAL_PNG_B64 = ("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=")


@pytest.fixture
def mock_gemini_client(mocker):
    client = MagicMock()
    client.is_configured.return_value = True
    mock_response = """
    {
        "summary": "This table shows participant demographics.",
        "structured_data": [
            {"Characteristic": "Age", "Value": "45"},
            {"Characteristic": "Gender", "Value": "Female"}
        ]
    }
    """
    client.query_with_image.return_value = mock_response
    return client


@pytest.fixture
def mock_document_and_camelot(mocker):
    mock_doc = MagicMock()
    mock_doc.name = "mock.pdf"
    mock_page = MagicMock()

    mock_pixmap = MagicMock()
    mock_pixmap.tobytes.return_value = base64.b64decode(MINIMAL_PNG_B64)
    mock_page.get_pixmap.return_value = mock_pixmap

    mock_doc.load_page.return_value = mock_page

    mock_table_area = MagicMock()
    mock_table_area.page = 1
    mock_table_area._bbox = (10, 10, 100, 100)
    mock_read_pdf = mocker.patch("camelot.read_pdf")
    mock_read_pdf.side_effect = [[mock_table_area], []]

    return mock_doc


def test_extract_tables_with_llm_success(mock_document_and_camelot, mock_gemini_client):
    doc = mock_document_and_camelot
    client = mock_gemini_client
    extracted_tables = extract_tables_with_llm(doc, client)

    assert len(extracted_tables) == 1
    table = extracted_tables[0]
    assert table.summary == "This table shows participant demographics."
    assert len(table.table_data) == 2
    assert table.table_data[0]["Characteristic"] == "Age"
    assert table.table_data[1]["Value"] == "Female"
    assert table.provenance.page_number == 1
    assert table.provenance.source_filename == "mock.pdf"


def test_extract_tables_with_llm_no_gemini(mock_document_and_camelot):
    doc = mock_document_and_camelot
    client = MagicMock()
    client.is_configured.return_value = False
    extracted_tables = extract_tables_with_llm(doc, client)
    assert extracted_tables == []
