import click
import sys
import logging
from evidence_extractor.utils.logging_config import setup_logging
from evidence_extractor.core.ingest import ingest_pdf
from evidence_extractor.core.preprocess import extract_text_from_doc, clean_and_consolidate_text
from evidence_extractor.extraction.citations import find_references_section, parse_bibliography
from evidence_extractor.models.schemas import ArticleExtraction

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

    document = ingest_pdf(pdf_path)
    if not document:
        logger.error("Halting execution due to ingestion failure.")
        sys.exit(1)
    pages_text = extract_text_from_doc(document)
    text_with_newlines, cleaned_text = clean_and_consolidate_text(pages_text)
    if not cleaned_text:
        logger.error("Text cleaning resulted in an empty string.")
        document.close()
        sys.exit(1)
    references_tuple = find_references_section(text_with_newlines)
    if references_tuple:
        references_text, _ = references_tuple
        bibliography = parse_bibliography(references_text)
        extraction_result.bibliography = bibliography
    
    logger.info(f"Found and parsed {len(extraction_result.bibliography)} bibliography entries.")
    logger.warning("(Note: Further analysis and output generation not yet implemented.)")
    
    document.close()
    logger.info("Processing complete.")
    sys.exit(0)

if __name__ == "__main__":
    cli()