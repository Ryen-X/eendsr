import logging
from typing import List
import camelot
from evidence_extractor.models.schemas import ExtractedTable, Provenance

logger = logging.getLogger(__name__)

def extract_tables_from_pdf(pdf_path: str) -> List[ExtractedTable]:
    extracted_tables = []
    logger.info(f"Starting table extraction from '{pdf_path}' using Camelot.")
    try:
        tables = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
    except Exception as e:
        logger.error(f"Camelot failed to process the PDF. Ensure Ghostscript is installed. Error: {e}")
        return []
    logger.info(f"Camelot found {tables.n} potential tables.")
    for i, table in enumerate(tables):
        if table.parsing_report['accuracy'] < 90:
            logger.warning(
                f"Skipping table {i+1} on page {table.page} due to low accuracy "
                f"({table.parsing_report['accuracy']:.2f}%)."
            )
            continue
        header = [str(col) for col in table.df.columns]
        rows = [[str(item) for item in row] for row in table.df.values.tolist()]
        table_data = [header] + rows
        provenance = Provenance(
            source_filename=pdf_path,
            page_number=table.page,
            bounding_box=table._bbox
        )
        extracted_table = ExtractedTable(
            caption=None,
            table_data=table_data,
            provenance=provenance
        )
        extracted_tables.append(extracted_table)
        logger.debug(f"Successfully parsed table {i+1} on page {table.page}.")

    return extracted_tables