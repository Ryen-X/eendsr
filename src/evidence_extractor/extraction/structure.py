import logging
import re
from typing import List, Tuple

logger = logging.getLogger(__name__)

COMMON_SECTION_HEADERS = [
    "abstract",
    "introduction",
    "background",
    "related work",
    "methods",
    "methodology",
    "materials and methods",
    "experimental setup",
    "results",
    "findings",
    "discussion",
    "conclusion",
    "summary",
    "acknowledgements",
    "acknowledgments",
]
def detect_sections(text_with_newlines: str) -> List[Tuple[str, int]]:
    detected_sections = []
    pattern_text = r"^\s*(?:\d{1,2}\.?\s*|[A-Z]\.\s*|[IVXLCDM]+\.?\s*)?(" + "|".join(COMMON_SECTION_HEADERS) + r")\s*$"
    pattern = re.compile(pattern_text, re.IGNORECASE | re.MULTILINE)
    for match in pattern.finditer(text_with_newlines):
        section_title = match.group(1).strip().lower()
        start_index = match.start()
        if start_index == 0 or text_with_newlines[start_index-1] == '\n':
            detected_sections.append((section_title, start_index))
            logger.debug(f"Detected section '{section_title}' at index {start_index}.")
    detected_sections.sort(key=lambda x: x[1])

    logger.info(f"Detected {len(detected_sections)} potential sections.")
    return detected_sections