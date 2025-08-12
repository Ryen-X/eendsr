import logging
import os
from typing import Optional
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self, text_model_name: str = "gemini-1.5-flash-latest", vision_model_name: str = "gemini-pro-vision"):
        self.text_model = None
        self.vision_model = None
        self.api_key = None
        self._configure_api()
        if self.api_key:
            self.text_model = genai.GenerativeModel(text_model_name)
            self.vision_model = genai.GenerativeModel(vision_model_name)
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
        return self.api_key is not None
    def query(self, prompt: str) -> Optional[str]:
        if not self.text_model:
            logger.error("Cannot query text model. Client is not configured.")
            return None
        logger.info(f"Sending text query to model '{self.text_model.model_name}'...")
        try:
            response = self.text_model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"An error occurred during text query: {e}")
            return None
    def query_with_image(self, prompt: str, image: Image.Image) -> Optional[str]:
        if not self.vision_model:
            logger.error("Cannot query vision model. Client is not configured.")
            return None
            
        logger.info(f"Sending multimodal query to model '{self.vision_model.model_name}'...")
        try:
            response = self.vision_model.generate_content([prompt, image])
            return response.text
        except Exception as e:
            logger.error(f"An error occurred during multimodal query: {e}")
            return None