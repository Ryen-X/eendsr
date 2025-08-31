import logging
import json
from typing import List
from evidence_extractor.integration.gemini_client import GeminiClient
from evidence_extractor.models.schemas import Claim

logger = logging.getLogger(__name__)

def annotate_claims_in_batch(client: GeminiClient, claims: List[Claim]):
    if not client.is_configured() or not claims:
        logger.warning("Cannot annotate uncertainty; client not configured or no claims provided.")
        return
    formatted_claims = "\n".join([f'{i+1}. {claim.claim_text}' for i, claim in enumerate(claims)])

    prompt = f"""
    Analyze the linguistic certainty for each scientific claim in the numbered list below.
    For each claim, classify its confidence level as "High", "Medium", or "Low" based on its wording.

    - "High": Definitive language (e.g., "we demonstrate", "proves", "shows a significant increase").
    - "Medium": Cautious language (e.g., "suggests", "is associated with", "may indicate").
    - "Low": Speculative language (e.g., "could potentially", "further research is needed").

    Return a single, valid JSON array where each object corresponds to a claim in the original list.
    Each object must have two keys:
    1. "claim_index": The original number of the claim (e.g., 1, 2, 3...).
    2. "annotation": A string that includes the confidence level and a brief justification.

    Example format for a single claim object:
    {{"claim_index": 1, "annotation": "Confidence: High. Justification: The claim uses definitive language..."}}

    --- CLAIM LIST ---
    {formatted_claims}
    --- END CLAIM LIST ---

    JSON Response:
    """

    logger.info(f"Querying Gemini for batch uncertainty annotation of {len(claims)} claims.")
    response_text = client.query(prompt)

    if not response_text:
        logger.error("Received no response from Gemini for batch uncertainty annotation.")
        return

    try:
        cleaned_response = response_text.strip().replace("```json", "").replace("```", "").strip()
        annotations_data = json.loads(cleaned_response)
        
        if not isinstance(annotations_data, list):
            logger.error("Gemini response for batch annotation was not a JSON list.")
            return

        for annotation_data in annotations_data:
            idx = annotation_data.get("claim_index")
            annotation = annotation_data.get("annotation")
            if idx is not None and isinstance(idx, int) and 0 < idx <= len(claims):
                claims[idx - 1].uncertainty_annotation = annotation
        logger.info("Successfully applied batch uncertainty annotations.")
    except (json.JSONDecodeError, AttributeError):
        logger.error(f"Failed to decode JSON for batch uncertainty annotation. Response was:\n{response_text}")