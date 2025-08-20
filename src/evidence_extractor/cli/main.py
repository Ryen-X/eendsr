import click
import sys
import logging
from evidence_extractor.utils.logging_config import setup_logging
from evidence_extractor.core.ingest import ingest_pdf
from evidence_extractor.core.preprocess import extract_text_from_doc, clean_and_consolidate_text
from evidence_extractor.extraction.citations import find_references_section, parse_bibliography, link_in_text_citations
from evidence_extractor.extraction.structure import detect_sections
from evidence_extractor.extraction.tables import extract_tables_from_pdf
from evidence_extractor.extraction.pico import extract_pico_elements
from evidence_extractor.extraction.methods import extract_methods_and_quality
from evidence_extractor.extraction.figures import extract_figures_and_captions
from evidence_extractor.extraction.claims import extract_claims
from evidence_extractor.models.schemas import ArticleExtraction
from evidence_extractor.integration.gemini_client import GeminiClient

logger = logging.getLogger(__name__)

@click.group()
@click.version_option(package_name="evidence_extractor")
def cli():
    setup_logging()

@cli.command()
@click.option(
    "--pdf",
    "pdf_path",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    required=True,
    help="The path to the PDF file to be processed.",
)
@click.option(
    "--output",
    "output_path",
    type=click.Path(dir_okay=False, writable=True, resolve_path=True),
    required=True,
    help="The path to save the structured JSON output.",
)
def extract(pdf_path: str, output_path: str):
    logger.info("--- Evidence Extractor ---")
    logger.info(f"Received request to process PDF: {pdf_path}")
    
    extraction_result = ArticleExtraction(source_filename=pdf_path)

    gemini_client = GeminiClient()
    if not gemini_client.is_configured():
        logger.warning("Gemini client is not configured. LLM-based extraction will be skipped.")

    document = ingest_pdf(pdf_path)
    if not document:
        sys.exit(1)

    pages_text = extract_text_from_doc(document)
    text_with_newlines, cleaned_text = clean_and_consolidate_text(pages_text)
    if not cleaned_text:
        document.close()
        sys.exit(1)
    text_snippet_for_claims = cleaned_text[:16000]

    if gemini_client.is_configured():
        text_snippet_for_metadata = cleaned_text[:8000]
        
        title = gemini_client.query(f"Extract the title of this paper: {text_snippet_for_metadata[:4000]}")
        if title:
            extraction_result.title = title.strip()
        
        pico_results = extract_pico_elements(gemini_client, text_snippet_for_metadata)
        if pico_results:
            extraction_result.pico_elements = pico_results
        
        quality_score = extract_methods_and_quality(gemini_client, text_snippet_for_metadata)
        if quality_score:
            extraction_result.quality_scores.append(quality_score)
        
        figures = extract_figures_and_captions(document, gemini_client)
        if figures:
            extraction_result.figures = figures
        claims = extract_claims(gemini_client, text_snippet_for_claims, pdf_path)
        if claims:
            extraction_result.claims = claims
            for i, claim in enumerate(claims[:3]):
                logger.info(f"  - Extracted Claim {i+1}: {claim.claim_text[:100]}...")

    sections = detect_sections(text_with_newlines)
    extracted_tables = extract_tables_from_pdf(pdf_path)
    if extracted_tables:
        extraction_result.tables = extracted_tables

    references_tuple = find_references_section(text_with_newlines)
    if references_tuple:
        references_text, start_index = references_tuple
        bibliography = parse_bibliography(references_text)
        extraction_result.bibliography = bibliography
        main_body_text = text_with_newlines[:start_index]
        link_in_text_citations(main_body_text, extraction_result.bibliography)

    logger.warning("(Note: Further analysis and output generation not yet implemented.)")
    
    document.close()
    logger.info("Processing complete.")
    sys.exit(0)

if __name__ == "__main__":
    cli()