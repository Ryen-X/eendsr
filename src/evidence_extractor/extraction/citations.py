import logging
import re
from typing import Dict, Optional, Tuple, List, Set
from evidence_extractor.models.schemas import BibliographyItem
from thefuzz import fuzz

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
            author_year_match = re.search(r'([A-Za-z,.\s&]+?)\s*\(?(\d{4})\)?', entry)
            if author_year_match:
                author = author_year_match.group(1).split(',')[0].strip()
                year = author_year_match.group(2)
                key = f"{author.replace(' ', '')}{year}"
            else:
                key = f"ref_{ref_count}"
            
            bibliography[key] = BibliographyItem(
                citation_key=key,
                full_citation=entry.strip()
            )
            
    logger.info(f"Parsed {len(bibliography)} potential bibliography entries.")
    return bibliography

def link_in_text_citations(
    main_body_text: str, 
    bibliography: Dict[str, BibliographyItem]
) -> Dict[str, List[str]]:
    logger.info("Starting in-text citation linking.")
    citation_pattern = re.compile(r'\(.+?\d{4}.*?\)|\[[\d,\s-]+\]')
    
    in_text_mentions = citation_pattern.findall(main_body_text)
    
    links: Dict[str, Set[str]] = {key: set() for key in bibliography}

    bib_authors = {key: item.full_citation.split(',')[0].lower() for key, item in bibliography.items()}

    for mention in set(in_text_mentions):
        mention_text = mention.lower().strip('()[]')
        for key, author in bib_authors.items():
            if fuzz.partial_ratio(author, mention_text) > 90:
                links[key].add(mention)
        year_match = re.search(r'(\d{4})', mention_text)
        if year_match:
            year = year_match.group(1)
            for key, item in bibliography.items():
                if year in item.full_citation:
                    author_in_mention = any(
                        fuzz.partial_ratio(name.strip(), mention_text) > 90 
                        for name in bib_authors[key].split()
                    )
                    if author_in_mention:
                        links[key].add(mention)
    final_links = {key: list(value) for key, value in links.items() if value}
    logger.info(f"Successfully linked {len(final_links)} bibliography entries to in-text citations.")
    return final_links