import io
import json
import logging
from typing import List

import camelot
import fitz
from PIL import Image

from evidence_extractor.integration.gemini_client import GeminiClient
from evidence_extractor.models.schemas import ExtractedTable, Provenance

from .prompts import TABLE_PARSING_PROMPT

logger = logging.getLogger(__name__)


def extract_tables_with_llm(
    doc: fitz.Document, client: GeminiClient
) -> List[ExtractedTable]:
    if not client.is_configured():
        logger.warning("Skipping table extraction; Gemini client is not configured.")
        return []

    extracted_tables = []
    logger.info("Starting advanced table extraction process.")

    try:
        tables_lattice = camelot.read_pdf(doc.name, pages="all", flavor="lattice")
        tables_stream = camelot.read_pdf(doc.name, pages="all", flavor="stream")
        all_tables = list(tables_lattice)
        all_tables.extend(list(tables_stream))

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
            logger.warning(
                f"Failed to capture screenshot for table area {i + 1}. "
                f"Skipping. Error: {e}"
            )
            continue

        response_text = client.query_with_image(TABLE_PARSING_PROMPT, image)
        if not response_text:
            logger.warning(f"Gemini provided no response for table area {i + 1}.")
            continue

        try:
            cleaned_response = (
                response_text.strip().replace("```json", "").replace("```", "").strip()
            )
            data = json.loads(cleaned_response)

            if data.get("structured_data"):
                provenance = Provenance(
                    source_filename=doc.name,
                    page_number=table_area.page,
                    bounding_box=list(table_area._bbox),
                )
                structured_table = ExtractedTable(
                    summary=data.get("summary"),
                    table_data=data["structured_data"],
                    provenance=provenance,
                )
                extracted_tables.append(structured_table)
                logger.info(
                    f"Successfully parsed table on page {table_area.page}. "
                    f"Summary: {data.get('summary')}"
                )
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(
                "Failed to parse Gemini's response for table on page "
                f"{table_area.page}. Error: {e}"
            )

    logger.info(
        f"Advanced table extraction complete. Found {len(extracted_tables)} "
        "structured tables."
    )
    return extracted_tables
