import logging
import re
from typing import Dict, Optional, Tuple, List, Set
from evidence_extractor.models.schemas import BibliographyItem

logger = logging.getLogger(__name__)

def find_references_section(full_text: str) -> Optional[Tuple[str, int]]:
    reference_headers = [r"references", r"literature cited", r"bibliography", r"works cited"]
    pattern = re.compile(r"^\s*(" + "|".join(reference_headers) + r")\s*$", re.IGNORECASE | re.MULTILINE)
    match = pattern.search(full_text)
    if not match:
        return None
    start_index = match.end()
    return full_text[start_index:].strip(), start_index

def parse_bibliography(references_text: str) -> Dict[str, BibliographyItem]:
    bibliography = {}
    potential_citations = re.split(r'\n\s*\n*', references_text)
    ref_count = 0
    for i, entry in enumerate(potential_citations):
        if len(entry.strip()) > 20:
            ref_count += 1
            author_year_match = re.search(r'([A-Za-z,.\s&]+?)\s*\(?(\d{4})\)?', entry)
            if author_year_match:
                author = author_year_match.group(1).split(',')[0].strip()
                year = author_year_match.group(2)
                key = f"{author.replace(' ', '')}{year}"
            else:
                key = f"ref_{ref_count}"
            bibliography[key] = BibliographyItem(citation_key=key, full_citation=entry.strip())
    return bibliography

def link_in_text_citations(
    main_body_text: str, 
    bibliography: Dict[str, BibliographyItem]
) -> Dict[str, List[str]]:
    logger.info("Starting in-text citation linking.")
    links: Dict[str, Set[str]] = {key: set() for key in bibliography}
    
    for key, item in bibliography.items():
        author_match = item.full_citation.split(',')[0]
        year_match = re.search(r'(\d{4})', item.full_citation)
        if not year_match:
            continue
        year = year_match.group(1)
        pattern = re.compile(r'({}.{{0,20}}{}[\)\]])'.format(re.escape(author_match), year), re.IGNORECASE)
        for match in pattern.finditer(main_body_text):
            links[key].add(match.group(1))
    final_links = {key: list(value) for key, value in links.items() if value}
    logger.info(f"Successfully linked {len(final_links)} bibliography entries to in-text citations.")
    return final_links