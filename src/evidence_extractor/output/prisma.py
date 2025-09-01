import logging
from datetime import datetime
from evidence_extractor.models.schemas import ArticleExtraction

logger = logging.getLogger(__name__)

def generate_prisma_text_report(extraction: ArticleExtraction) -> str:
    logger.info("Generating PRISMA text report.")
    
    report_lines = []
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    report_lines.append("=" * 50)
    report_lines.append("PRISMA-Style Extraction Report (Single Article)")
    report_lines.append(f"Generated on: {now}")
    report_lines.append("=" * 50)
    report_lines.append(f"\nSource Document: {extraction.source_filename}")
    report_lines.append(f"Extracted Title: {extraction.title or 'Not Found'}")
    report_lines.append("\n--- Identification & Screening ---")
    report_lines.append("1. Record identified for extraction: 1")
    report_lines.append("2. Record screened: 1")
    report_lines.append("3. Record included in synthesis: 1")
    report_lines.append("\n--- Data Extraction Summary ---")
    if extraction.pico_elements:
        pico_status = extraction.pico_elements.correction_metadata.status.value
        report_lines.append(f"- PICO Elements: Found (Status: {pico_status})")
    else:
        report_lines.append("- PICO Elements: Not Found")
    num_scores = len(extraction.quality_scores)
    if num_scores > 0:
        score_status = extraction.quality_scores[0].correction_metadata.status.value
        report_lines.append(f"- Quality Scores: {num_scores} Found (Primary Status: {score_status})")
    else:
        report_lines.append("- Quality Scores: Not Found")
    num_claims = len(extraction.claims)
    verified_claims = sum(1 for c in extraction.claims if c.correction_metadata.status == "verified")
    report_lines.append(f"- Claims: {num_claims} Found ({verified_claims} verified)")
    num_tables = len(extraction.tables)
    num_figures = len(extraction.figures)
    report_lines.append(f"- Tables: {num_tables} Found")
    report_lines.append(f"- Figures: {num_figures} Found")
    num_refs = len(extraction.bibliography)
    report_lines.append(f"- Bibliography Entries: {num_refs} Found")

    report_lines.append("\n" + "=" * 50)
    report_lines.append("End of Report")
    report_lines.append("=" * 50)

    return "\n".join(report_lines)

def save_prisma_report(report_content: str, output_path: str):
    logger.info(f"Saving PRISMA report to '{output_path}'...")
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        logger.info("PRISMA report saved successfully.")
    except IOError as e:
        logger.error(f"Failed to save PRISMA report to '{output_path}'. Error: {e}")