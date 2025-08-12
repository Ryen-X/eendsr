import logging
import yaml
from pathlib import Path
import google.generativeai as genai
from typing import Optional

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self, model_name: str = "gemini-2.5-pro"):
        self.model = None
        self._configure_api()
        if self.api_key:
            self.model = genai.GenerativeModel(model_name)

    def _configure_api(self):
        self.api_key = None
        config_path = Path(__file__).parent.parent.parent.parent / "config" / "settings.yaml"
        
        if not config_path.exists():
            logger.error("Configuration file 'config/settings.yaml' not found.")
            return

        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            self.api_key = config.get("gemini_api_key")

        if not self.api_key or self.api_key == "YOUR_API_KEY_HERE":
            logger.error("Gemini API key is missing or not set in 'config/settings.yaml'.")
            self.api_key = None
            return
        
        try:
            genai.configure(api_key=self.api_key)
            logger.info("Successfully configured Gemini API client.")
        except Exception as e:
            logger.error(f"Failed to configure Gemini API: {e}")
            self.api_key = None

    def is_configured(self) -> bool:
        return self.model is not None

    def query(self, prompt: str) -> Optional[str]:
        """
        Args:
            prompt: The prompt to send to the model.
        Returns:
            The model's text response, or None if an error occurs.
        """
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