import logging
from typing import Optional
import fitz

logger = logging.getLogger(__name__)

def ingest_pdf(pdf_path: str) -> Optional[fitz.Document]:
    logger.info(f"Attempting to ingest PDF from: {pdf_path}")
    try:
        doc = fitz.open(pdf_path)
        if doc.page_count == 0:
            logger.error(f"PDF validation failed: '{pdf_path}' contains no pages.")
            doc.close()
            return None
        
        logger.info(f"Successfully ingested PDF. Document has {doc.page_count} pages.")
        return doc
    except Exception as e:
        logger.error(f"Failed to open or process PDF '{pdf_path}'. Error: {e}")
        return None