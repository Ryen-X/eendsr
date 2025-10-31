import logging
import os
from typing import Optional

import fitz

logger = logging.getLogger(__name__)


def ingest_pdf(pdf_path: str) -> Optional[fitz.Document]:
    logger.info(f"Attempting to ingest PDF from: {pdf_path}")
    if not os.path.exists(pdf_path):
        logger.error(f"File not found at path: '{pdf_path}'")
        return None
    if not pdf_path.lower().endswith(".pdf"):
        logger.error(f"File '{pdf_path}' is not a PDF. Ingestion failed.")
        return None

    doc = None
    try:
        doc = fitz.open(pdf_path)
        if doc.page_count == 0:
            logger.error(f"PDF validation failed: '{pdf_path}' contains no pages.")
            doc.close()
            return None
    except Exception as e:
        logger.error(f"Failed to open or process PDF '{pdf_path}'. PyMuPDF error: {e}")
        if doc:
            doc.close()
        return None

    logger.info(f"Successfully ingested PDF. Document has {doc.page_count} pages.")
    return doc
