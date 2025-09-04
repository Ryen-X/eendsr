import logging
import json
from typing import Optional, Dict, Any
from evidence_extractor.integration.gemini_client import GeminiClient

logger = logging.getLogger(__name__)

def orchestrate_llm_extraction(client: GeminiClient, text_snippet: str) -> Optional[Dict[str, Any]]:
    if not client.is_configured():
        logger.warning("Cannot orchestrate extraction; Gemini client is not configured.")
        return None

    prompt = f"""
    You are an expert research assistant. Analyze the following text from a scientific paper and extract the requested information.

    Return a single, valid JSON object with three top-level keys: "pico", "quality", and "claims".

    1.  **pico**: An object with keys "population", "intervention", "comparison", and "outcome".
    2.  **quality**: An object based on the study design. It must have keys "score_name" (always "Methodological Quality"), "score_value" ("High", "Medium", or "Low"), and "justification".
        - "High": Randomized Controlled Trial (RCT), Systematic Review.
        - "Medium": Cohort Study, Case-Control Study.
        - "Low": Case Report, Cross-Sectional Study, unclear methodology.
    3.  **claims**: A JSON array of objects. Each object represents a key factual finding and must have a single key: "claim_text".

    Do not include any explanatory text or markdown formatting around the final JSON object.

    --- TEXT ---
    {text_snippet}
    --- END TEXT ---

    JSON Response:
    """

    logger.info("Orchestrating main LLM extraction (PICO, Quality, Claims) in a single call.")
    response_text = client.query(prompt)
    if not response_text:
        logger.error("Received no response from Gemini for orchestrated extraction.")
        return None
    try:
        cleaned_response = response_text.strip().replace("```json", "").replace("```", "").strip()
        data = json.loads(cleaned_response)
        logger.info("Successfully parsed response from orchestrated LLM extraction.")
        return data
    except (json.JSONDecodeError, KeyError):
        logger.error(f"Failed to parse JSON from orchestrated extraction. Response was:\n{response_text}")
        return None