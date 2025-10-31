import logging
from typing import Dict

from thefuzz import fuzz

logger = logging.getLogger(__name__)


def find_claim_provenance(claim_text: str, pages_text: Dict[int, str]) -> int:
    if not claim_text:
        return -1

    best_score = 0
    best_page = -1

    # Work each page to find best possible match
    for page_num, page_content in pages_text.items():
        if not page_content:
            continue
        score = fuzz.partial_ratio(claim_text.lower(), page_content.lower())

        if score > best_score:
            best_score = score
            best_page = page_num + 1

    if best_score > 90:
        logger.debug(
            f"Found provenance for claim '{claim_text[:50]}...' on page {best_page} "
            f"with score {best_score}."
        )
        return best_page
    else:
        logger.warning(
            f"Could not find strong provenance for claim: '{claim_text[:50]}...'. "
            f"Best score {best_score}."
        )
        return -1
