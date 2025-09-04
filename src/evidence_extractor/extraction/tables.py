import logging
import json
import io
from typing import List
import camelot
import fitz
from PIL import Image
from evidence_extractor.models.schemas import ExtractedTable, Provenance
from evidence_extractor.integration.gemini_client import GeminiClient

logger = logging.getLogger(__name__)

def extract_tables_with_llm(
    doc: fitz.Document, 
    client: GeminiClient
) -> List[ExtractedTable]:
    if not client.is_configured():
        logger.warning("Skipping table extraction; Gemini client is not configured.")
        return []

    extracted_tables = []
    logger.info("Starting advanced table extraction process.")
    
    try:
        tables_lattice = camelot.read_pdf(doc.name, pages='all', flavor='lattice')
        tables_stream = camelot.read_pdf(doc.name, pages='all', flavor='stream')
        all_tables = tables_lattice + tables_stream
        logger.info(f"Camelot identified {len(all_tables)} potential table areas.")
    except Exception as e:
        logger.error(f"Camelot failed to process the PDF. Error: {e}")
        return []

    for i, table_area in enumerate(all_tables):
        page_num = table_area.page - 1
        page = doc.load_page(page_num)
        
        x0, y0, x1, y1 = table_area._bbox
        rect = fitz.Rect(x0, y1, x1, y0)
        
        try:
            pix = page.get_pixmap(clip=rect, dpi=300)
            image = Image.open(io.BytesIO(pix.tobytes()))
        except Exception as e:
            logger.warning(f"Failed to capture screenshot for table area {i+1}. Skipping. Error: {e}")
            continue

        prompt = """
        Analyze the following image of a table from a research paper.

        Your task is to:
        1.  Identify the column headers.
        2.  Extract the data for each row.
        3.  Provide a one-sentence summary of the table's main finding.

        Return a single, valid JSON object with two keys: "summary" and "structured_data".
        - The value for "summary" should be the summary string.
        - The value for "structured_data" should be a JSON array of objects, where each object represents a row and the keys are the column headers.

        If a cell spans multiple rows, repeat its value for each row it covers.
        If the table is unreadable, return an empty "structured_data" array.
        Do not include any explanatory text or markdown formatting around the JSON object.
        """

        response_text = client.query_with_image(prompt, image)
        if not response_text:
            logger.warning(f"Gemini provided no response for table area {i+1}.")
            continue

        try:
            cleaned_response = response_text.strip().replace("```json", "").replace("```", "").strip()
            data = json.loads(cleaned_response)
            
            if data.get("structured_data"):
                provenance = Provenance(
                    source_filename=doc.name,
                    page_number=table_area.page,
                    bounding_box=list(table_area._bbox)
                )
                structured_table = ExtractedTable(
                    summary=data.get("summary"),
                    table_data=data["structured_data"],
                    provenance=provenance
                )
                extracted_tables.append(structured_table)
                logger.info(f"Successfully parsed table on page {table_area.page}. Summary: {data.get('summary')}")

        except (json.JSONDecodeError, KeyError):
            logger.error(f"Failed to parse Gemini's response for table on page {table_area.page}.")

    logger.info(f"Advanced table extraction complete. Found {len(extracted_tables)} structured tables.")
    return extracted_tables