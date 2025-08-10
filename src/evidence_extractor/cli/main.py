import click
import sys
import logging
from evidence_extractor.utils.logging_config import setup_logging
from evidence_extractor.core.ingest import ingest_pdf
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
    document = ingest_pdf(pdf_path)
    if not document:
        logger.error("Halting execution due to ingestion failure.")
        sys.exit(1)

    logger.info(f"Output will be saved to: {output_path}")
    logger.warning("(Note: Text extraction and analysis not yet implemented.)")
    document.close()
    logger.info("Processing complete.")
    sys.exit(0)

if __name__ == "__main__":
    cli()