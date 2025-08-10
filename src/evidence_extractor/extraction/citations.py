import logging
import re
from typing import Dict, Optional, Tuple
from evidence_extractor.models.schemas import BibliographyItem

logger = logging.getLogger(__name__)

def find_references_section(full_text: str) -> Optional[Tuple[str, int]]:
    reference_headers = [
        r"references",
        r"literature cited",
        r"bibliography",
        r"works cited"
    ]
    pattern = re.compile(r"^\s*(" + "|".join(reference_headers) + r")\s*$", re.IGNORECASE | re.MULTILINE)
    match = pattern.search(full_text)
    if not match:
        logger.warning("Could not find a standard 'References' or 'Bibliography' section header.")
        return None
    start_index = match.end()
    logger.info(f"Found references section header: '{match.group(0).strip()}'")
    return full_text[start_index:].strip(), start_index

def parse_bibliography(references_text: str) -> Dict[str, BibliographyItem]:
    bibliography = {}
    potential_citations = re.split(r'\n\s*\n*', references_text)
    ref_count = 0
    for i, entry in enumerate(potential_citations):
        if len(entry.strip()) > 20:
            ref_count += 1
            key = f"ref_{ref_count}"
            bibliography[key] = BibliographyItem(
                citation_key=key,
                full_citation=entry.strip()
            )
            
    logger.info(f"Parsed {len(bibliography)} potential bibliography entries.")
    return bibliography