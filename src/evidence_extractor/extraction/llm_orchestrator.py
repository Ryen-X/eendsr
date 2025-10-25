import logging
import json
from typing import Optional, Dict, Any
from evidence_extractor.integration.gemini_client import GeminiClient
from .prompts import ORCHESTRATION_PROMPT

logger = logging.getLogger(__name__)

def orchestrate_llm_extraction(client: GeminiClient, text_snippet: str) -> Optional[Dict[str, Any]]:
    if not client.is_configured():
        logger.warning("Cannot orchestrate extraction; Gemini client is not configured.")
        return None

    prompt = ORCHESTRATION_PROMPT.format(text_snippet=text_snippet)

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