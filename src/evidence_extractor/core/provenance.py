import logging
import re
from typing import Dict

logger = logging.getLogger(__name__)

def _normalize_text_for_search(text: str) -> str:
    return re.sub(r'[^a-z0-9]', '', text.lower())

def find_claim_provenance(claim_text: str, pages_text: Dict[int, str]) -> int:
    normalized_claim_snippet = _normalize_text_for_search(claim_text[:100])

    if not normalized_claim_snippet:
        return -1

    for page_num, page_content in pages_text.items():
        normalized_page_content = _normalize_text_for_search(page_content)
        if normalized_claim_snippet in normalized_page_content:
            logger.debug(f"Found provenance for claim '{claim_text[:50]}...' on page {page_num + 1}.")
            return page_num + 1

    logger.warning(f"Could not find provenance for claim: '{claim_text[:50]}...'")
    return -1