import logging
import os
from pathlib import Path
import google.generativeai as genai
from typing import Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self, model_name: str = "gemini-pro"):
        self.model = None
        self._configure_api()
        if self.api_key:
            self.model = genai.GenerativeModel(model_name)

    def _configure_api(self):
        load_dotenv()
        
        self.api_key = os.getenv("GEMINI_API_KEY")

        if not self.api_key or self.api_key == "YOUR_API_KEY_HERE":
            logger.error("Gemini API key not found. Please create a .env file and set GEMINI_API_KEY.")
            self.api_key = None
            return
        try:
            genai.configure(api_key=self.api_key)
            logger.info("Successfully configured Gemini API client from environment variable.")
        except Exception as e:
            logger.error(f"Failed to configure Gemini API: {e}")
            self.api_key = None
    def is_configured(self) -> bool:
        return self.model is not None

    def query(self, prompt: str) -> Optional[str]:
        if not self.is_configured():
            logger.error("Cannot query Gemini API. Client is not configured.")
            return None
        
        logger.info("Sending query to Gemini API...")
        try:
            response = self.model.generate_content(prompt)
            if response.parts:
                return response.text
            else:
                logger.warning("Gemini API returned an empty or blocked response.")
                return None
        except Exception as e:
            logger.error(f"An error occurred while querying the Gemini API: {e}")
            return None