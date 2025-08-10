import logging
import re
from typing import Dict
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

def extract_text_from_doc(document: fitz.Document) -> Dict[int, str]:
    extracted_data = {}
    logger.info(f"Starting text extraction from {document.page_count} pages.")
    
    total_chars = 0
    for page_num in range(document.page_count):
        try:
            page = document.load_page(page_num)
            page_text = page.get_text("text")
            extracted_data[page_num] = page_text
            total_chars += len(page_text)
            logger.debug(f"Extracted {len(page_text)} characters from page {page_num + 1}.")
        except Exception as e:
            logger.error(f"Could not extract text from page {page_num + 1}. Error: {e}")
            extracted_data[page_num] = ""
    logger.info(f"Text extraction complete. Total characters extracted: {total_chars}.")
    return extracted_data

def clean_and_consolidate_text(pages_text: Dict[int, str]) -> str:
    logger.info("Starting text cleaning and consolidation.")
    full_text = "\n".join(pages_text.values())
    original_len = len(full_text)
    cleaned_text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', full_text)
    cleaned_text = re.sub(r'\n\s*\d+\s*\n', '\n', cleaned_text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    
    final_len = len(cleaned_text)
    logger.info(f"Text cleaning complete. Character count reduced from {original_len} to {final_len}.")
    
    return cleaned_text