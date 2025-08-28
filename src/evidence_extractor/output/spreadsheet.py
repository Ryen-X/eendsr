import logging
from openpyxl import Workbook
from evidence_extractor.models.schemas import ArticleExtraction

logger = logging.getLogger(__name__)

def export_to_excel(extraction: ArticleExtraction, output_path: str):
    logger.info(f"Starting export of findings to Excel file: '{output_path}'")
    wb = Workbook()
    if "Sheet" in wb.sheetnames:
        wb.remove(wb["Sheet"])

    ws_summary = wb.create_sheet("Summary")
    ws_summary.append(["Field", "Value", "Validation Status"])
    ws_summary.append(["Source Filename", extraction.source_filename, "N/A"])
    ws_summary.append(["Extracted Title", extraction.title, "N/A"])
    if extraction.pico_elements:
        pico = extraction.pico_elements
        ws_summary.append(["PICO - Population", pico.population, pico.correction_metadata.status.value])
        ws_summary.append(["PICO - Intervention", pico.intervention, pico.correction_metadata.status.value])
        ws_summary.append(["PICO - Comparison", pico.comparison, pico.correction_metadata.status.value])
        ws_summary.append(["PICO - Outcome", pico.outcome, pico.correction_metadata.status.value])
    
    for score in extraction.quality_scores:
        ws_summary.append([f"Quality Score - {score.score_name}", score.score_value, score.correction_metadata.status.value])
        ws_summary.append([f"Quality Justification", score.justification, score.correction_metadata.status.value])

    if extraction.claims:
        ws_claims = wb.create_sheet("Claims")
        ws_claims.append([
            "Claim Text", "Page Number", "Validation Status", "Reviewer Comment"
        ])
        for claim in extraction.claims:
            ws_claims.append([
                claim.claim_text,
                claim.provenance.page_number,
                claim.correction_metadata.status.value,
                claim.correction_metadata.reviewer_comment
            ])

    if extraction.figures:
        ws_figures = wb.create_sheet("Figures")
        ws_figures.append([
            "Caption", "Page Number", "Validation Status", "Reviewer Comment"
        ])
        for fig in extraction.figures:
            ws_figures.append([
                fig.caption,
                fig.provenance.page_number,
                fig.correction_metadata.status.value,
                fig.correction_metadata.reviewer_comment
            ])

    try:
        wb.save(output_path)
        logger.info(f"Successfully exported data to '{output_path}'.")
    except IOError as e:
        logger.error(f"Failed to save Excel file. Check permissions for '{output_path}'. Error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during Excel export: {e}")