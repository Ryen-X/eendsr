import logging
from typing import List, Optional
from evidence_extractor.integration.gemini_client import GeminiClient
from evidence_extractor.models.schemas import Claim

logger = logging.getLogger(__name__)

def generate_summary(client: GeminiClient, claims: List[Claim]) -> Optional[str]:
    if not client.is_configured() or not claims:
        logger.warning("Cannot generate summary; client not configured or no claims provided.")
        return None
    claim_texts = [claim.claim_text for claim in claims]
    formatted_claims = "\n".join([f"- {text}" for text in claim_texts])

    prompt = f"""
    Based on the following list of key findings extracted from a research paper, write a single, concise paragraph that summarizes the main conclusions of the study.
    Synthesize the points into a coherent narrative. Do not simply list them.
    The tone should be objective and academic.
    Start the paragraph directly, without any introductory phrases like "This paper concludes that...".

    --- KEY FINDINGS ---
    {formatted_claims}
    --- END KEY FINDINGS ---

    Summary Paragraph:
    """

    logger.info("Querying Gemini to generate evidence summary.")
    summary_text = client.query(prompt)

    if not summary_text:
        logger.error("Received no response from Gemini for summary generation.")
        return None

    logger.info("Successfully generated evidence summary.")
    return summary_text.strip()