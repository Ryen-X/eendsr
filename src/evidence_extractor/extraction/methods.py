import logging
import json
from typing import Optional
from evidence_extractor.integration.gemini_client import GeminiClient
from evidence_extractor.models.schemas import QualityScore

logger = logging.getLogger(__name__)

def extract_methods_and_quality(client: GeminiClient, text_snippet: str) -> Optional[QualityScore]:
    if not client.is_configured():
        logger.warning("Cannot extract methods/quality; Gemini client is not configured.")
        return None

    prompt = f"""
    Analyze the following text from a scientific paper to assess its methodology.
    
    First, identify the primary study design (e.g., Randomized Controlled Trial, Cohort Study, Case-Control Study, Systematic Review, Case Report, etc.).
    
    Second, based on the study design, assign a quality score according to this rubric:
    - "High": Randomized Controlled Trial (RCT) or Systematic Review/Meta-Analysis.
    - "Medium": Cohort Study or Case-Control Study.
    - "Low": Case Report, Cross-Sectional Study, or if the methodology is unclear.

    Return a single, valid JSON object with three keys:
    1. "score_name": This should always be the string "Methodological Quality".
    2. "score_value": The assigned score ("High", "Medium", or "Low").
    3. "justification": A brief summary of the study design that justifies the score.

    Do not include any explanatory text or markdown formatting before or after the JSON object.

    --- TEXT ---
    {text_snippet}
    --- END TEXT ---

    JSON Response:
    """

    logger.info("Querying Gemini for methodology and quality assessment.")
    response_text = client.query(prompt)

    if not response_text:
        logger.error("Received no response from Gemini for quality assessment.")
        return None

    try:
        cleaned_response = response_text.strip().replace("```json", "").replace("```", "").strip()
        quality_data = json.loads(cleaned_response)
        
        quality_model = QualityScore(**quality_data)
        logger.info("Successfully extracted and parsed methodological quality score.")
        return quality_model
    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON from Gemini for quality assessment. Response was:\n{response_text}")
        return None
    except Exception as e:
        logger.error(f"An error occurred while creating QualityScore model: {e}")
        return None