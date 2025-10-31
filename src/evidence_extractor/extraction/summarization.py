import logging
from typing import List, Optional

from evidence_extractor.integration.gemini_client import GeminiClient
from evidence_extractor.models.schemas import Claim

from .prompts import SUMMARY_PROMPT

logger = logging.getLogger(__name__)


def generate_summary(client: GeminiClient, claims: List[Claim]) -> Optional[str]:
    if not client.is_configured() or not claims:
        logger.warning(
            "Cannot generate summary; client not configured or no claims provided."
        )
        return None

    claim_texts = [claim.claim_text for claim in claims]
    formatted_claims = "\n".join([f"- {text}" for text in claim_texts])

    prompt = SUMMARY_PROMPT.format(formatted_claims=formatted_claims)

    logger.info("Querying Gemini to generate evidence summary.")
    summary_text = client.query(prompt)

    if not summary_text:
        logger.error("Received no response from Gemini for summary generation.")
        return None

    logger.info("Successfully generated evidence summary.")
    return summary_text.strip()
