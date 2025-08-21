import logging
import json
from typing import List
from evidence_extractor.integration.gemini_client import GeminiClient

logger = logging.getLogger(__name__)

def extract_claim_texts(
    client: GeminiClient, 
    text_snippet: str
) -> List[str]:
    if not client.is_configured():
        logger.warning("Cannot extract claims; Gemini client is not configured.")
        return []

    prompt = f"""
    Analyze the following text from a scientific research paper. Your task is to identify and extract the main factual claims or findings.
    A "claim" is a specific, verifiable statement about the results or conclusions of the study.
    Examples of good claims:
    - "Treatment with Drug X resulted in a 35% reduction in tumor size."
    - "The algorithm achieved an accuracy of 92% on the test dataset."
    - "There was a significant correlation between protein A and disease B (p < 0.05)."
    
    Do NOT extract general statements, background information, or descriptions of methods.

    Return your findings as a single, valid JSON array of objects. Each object in the array should represent one claim and must have a single key: "claim_text".
    The value of "claim_text" should be the verbatim text of the claim as found in the paper.

    --- TEXT ---
    {text_snippet}
    --- END TEXT ---

    JSON Response:
    """

    logger.info("Querying Gemini for key claim extraction.")
    response_text = client.query(prompt)

    if not response_text:
        logger.error("Received no response from Gemini for claim extraction.")
        return []

    extracted_claim_texts = []
    try:
        cleaned_response = response_text.strip().replace("```json", "").replace("```", "").strip()
        claims_data = json.loads(cleaned_response)
        
        if not isinstance(claims_data, list):
            logger.error("Gemini response for claims was not a JSON list.")
            return []

        for claim_dict in claims_data:
            claim_text = claim_dict.get("claim_text")
            if claim_text:
                extracted_claim_texts.append(claim_text)
        
        logger.info(f"Successfully extracted text for {len(extracted_claim_texts)} claims.")
        return extracted_claim_texts
    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON from Gemini for claim extraction. Response was:\n{response_text}")
        return []
    except Exception as e:
        logger.error(f"An error occurred while parsing claim response: {e}")
        return []