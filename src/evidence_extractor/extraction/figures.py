import logging
import io
from typing import List
import fitz
from PIL import Image
from .prompts import FIGURE_CAPTION_PROMPT
from evidence_extractor.integration.gemini_client import GeminiClient
from evidence_extractor.models.schemas import ExtractedFigure, Provenance

logger = logging.getLogger(__name__)

def extract_figures_and_captions(doc: fitz.Document, client: GeminiClient) -> List[ExtractedFigure]:
    if not client.is_configured():
        logger.warning("Skipping figure extraction; Gemini client is not configured.")
        return []
        
    extracted_figures = []
    logger.info("Starting figure and caption extraction.")
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        image_list = page.get_images(full=True)
        
        if not image_list:
            continue
            
        logger.info(f"Found {len(image_list)} potential images on page {page_num + 1}.")
        
        for img_index, img_info in enumerate(image_list):
            xref = img_info[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            
            try:
                image = Image.open(io.BytesIO(image_bytes))
            except Exception as e:
                logger.warning(f"Could not open image {img_index+1} on page {page_num+1}. Skipping. Error: {e}")
                continue
            
            caption_text = client.query_with_image(FIGURE_CAPTION_PROMPT, image)

            if caption_text and "no caption found" not in caption_text.lower():
                provenance = Provenance(source_filename=doc.name, page_number=page_num + 1, bounding_box=list(page.get_image_bbox(img_info)))
                figure = ExtractedFigure(caption=caption_text.strip(), figure_type="Figure", provenance=provenance)
                extracted_figures.append(figure)
                logger.info(f"Extracted caption for figure on page {page_num + 1}: '{caption_text[:50]}...'")
            else:
                logger.info(f"No caption found by Gemini for figure on page {page_num + 1}.")
                
    logger.info(f"Completed figure extraction. Found {len(extracted_figures)} figures with captions.")
    return extracted_figures