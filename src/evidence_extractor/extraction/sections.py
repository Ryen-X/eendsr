import logging
import re
from typing import List

from evidence_extractor.models.schemas import Section

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
    "references",
    "bibliography",
    "literature cited",
]


def detect_sections(text_with_newlines: str) -> List[Section]:
    sections = []
    pattern = re.compile(
        r"^\s*(?:\d\.?|I{1,3}V?|VI{1,3})\s*("
        + "|".join(COMMON_SECTION_HEADERS)
        + r")\s*$",
        re.IGNORECASE | re.MULTILINE,
    )

    matches = list(pattern.finditer(text_with_newlines))

    if not matches:
        logger.warning("Could not detect any standard section headers.")
        return []

    logger.info(f"Found {len(matches)} potential section headers.")

    for i, match in enumerate(matches):
        section_title = match.group(1).strip().lower()
        start_char = match.end()
        end_char = (
            matches[i + 1].start() if i + 1 < len(matches) else len(text_with_newlines)
        )
        section_text = text_with_newlines[start_char:end_char].strip()
        sections.append(
            Section(
                title=section_title, text_content=section_text, start_char=match.start()
            )
        )

    return sections
