import logging
import json
from typing import Optional
from evidence_extractor.integration.gemini_client import GeminiClient
from evidence_extractor.models.schemas import PICO

logger = logging.getLogger(__name__)

def extract_pico_elements(client: GeminiClient, text_snippet: str) -> Optional[PICO]:
    if not client.is_configured():
        logger.warning("Cannot extract PICO elements; Gemini client is not configured.")
        return None

    prompt = f"""
    Analyze the following text from a scientific paper to identify the PICO elements.
    PICO stands for:
    - Population: The specific patient group or problem being addressed.
    - Intervention: The main treatment, technology, or approach being studied.
    - Comparison: The alternative or control against which the intervention is compared.
    - Outcome: The primary results or effects that were measured.

    Extract these four elements and return them as a single, valid JSON object.
    The JSON object should have the keys "population", "intervention", "comparison", and "outcome".
    If a specific element cannot be found in the text, its value should be null.
    Do not include any explanatory text or markdown formatting before or after the JSON object.

    --- TEXT ---
    {text_snippet}
    --- END TEXT ---

    JSON Response:
    """

    logger.info("Querying Gemini for PICO element extraction.")
    response_text = client.query(prompt)

    if not response_text:
        logger.error("Received no response from Gemini for PICO extraction.")
        return None

    try:
        cleaned_response = response_text.strip().replace("```json", "").replace("```", "").strip()
        pico_data = json.loads(cleaned_response)
        pico_model = PICO(**pico_data)
        logger.info("Successfully extracted and parsed PICO elements.")
        return pico_model
    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON response from Gemini for PICO extraction. Response was:\n{response_text}")
        return None
    except Exception as e:
        logger.error(f"An error occurred while creating PICO model: {e}")
        return None