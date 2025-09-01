import click
import sys
import logging
import json
from datetime import datetime
from evidence_extractor.utils.logging_config import setup_logging
from evidence_extractor.core.ingest import ingest_pdf
from evidence_extractor.core.preprocess import extract_text_from_doc, clean_and_consolidate_text
from evidence_extractor.core.provenance import find_claim_provenance
from evidence_extractor.extraction.citations import find_references_section, parse_bibliography, link_in_text_citations
from evidence_extractor.extraction.structure import detect_sections
from evidence_extractor.extraction.tables import extract_tables_from_pdf
from evidence_extractor.extraction.pico import extract_pico_elements
from evidence_extractor.extraction.methods import extract_methods_and_quality
from evidence_extractor.extraction.figures import extract_figures_and_captions
from evidence_extractor.extraction.claims import extract_claim_texts
from evidence_extractor.extraction.uncertainty import annotate_claims_in_batch
from evidence_extractor.extraction.summarization import generate_summary
from evidence_extractor.models.schemas import ArticleExtraction, Claim, Provenance, ValidationStatus
from evidence_extractor.integration.gemini_client import GeminiClient
from evidence_extractor.output.json_builder import save_to_json
from evidence_extractor.output.spreadsheet import export_to_excel

logger = logging.getLogger(__name__)

@click.group()
@click.version_option(package_name="evidence_extractor")
def cli():
    setup_logging()

@cli.command()
@click.option(
    "--pdf", "pdf_path", type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    required=True, help="The path to the PDF file to be processed.",
)
@click.option(
    "--output", "output_path", type=click.Path(dir_okay=False, writable=True, resolve_path=True),
    required=True, help="The path to save the structured JSON output.",
)
def extract(pdf_path: str, output_path: str):
    logger.info("--- Evidence Extractor ---")
    logger.info(f"Received request to process PDF: {pdf_path}")
    
    extraction_result = ArticleExtraction(source_filename=pdf_path)
    gemini_client = GeminiClient()
    if not gemini_client.is_configured(): logger.warning("Gemini client not configured.")
    document = ingest_pdf(pdf_path)
    if not document: sys.exit(1)
    pages_text = extract_text_from_doc(document)
    text_with_newlines, cleaned_text = clean_and_consolidate_text(pages_text)
    if not cleaned_text: document.close(); sys.exit(1)

    if gemini_client.is_configured():
        text_snippet_metadata = cleaned_text[:8000]
        text_snippet_claims = cleaned_text[:16000]
        
        title = gemini_client.query(f"Extract the title of this paper: {text_snippet_metadata[:4000]}")
        if title: extraction_result.title = title.strip()
        
        pico = extract_pico_elements(gemini_client, text_snippet_metadata)
        if pico: extraction_result.pico_elements = pico
        
        quality = extract_methods_and_quality(gemini_client, text_snippet_metadata)
        if quality: extraction_result.quality_scores.append(quality)
        
        figures = extract_figures_and_captions(document, gemini_client)
        if figures: extraction_result.figures = figures
            
        claim_texts = extract_claim_texts(gemini_client, text_snippet_claims)
        if claim_texts:
            temp_claims = []
            for text in claim_texts:
                page_num = find_claim_provenance(text, pages_text)
                provenance = Provenance(source_filename=pdf_path, page_number=page_num)
                claim = Claim(claim_text=text, provenance=provenance)
                temp_claims.append(claim)
            
            annotate_claims_in_batch(gemini_client, temp_claims)
            extraction_result.claims = temp_claims
            summary = generate_summary(gemini_client, extraction_result.claims)
            if summary:
                extraction_result.summary = summary
                logger.info(f"--- Generated Summary ---\n{summary}\n-----------------------")
    sections = detect_sections(text_with_newlines)
    tables = extract_tables_from_pdf(pdf_path)
    if tables: extraction_result.tables = tables
    refs_tuple = find_references_section(text_with_newlines)
    if refs_tuple:
        refs_text, start_idx = refs_tuple
        bib = parse_bibliography(refs_text)
        extraction_result.bibliography = bib
        body_text = text_with_newlines[:start_idx]
        link_in_text_citations(body_text, extraction_result.bibliography)
    save_to_json(extraction_result, output_path)
    document.close()
    logger.info("Processing complete.")
    sys.exit(0)
@cli.command()
@click.argument("json_path", type=click.Path(exists=True, dir_okay=False, resolve_path=True))
def review(json_path: str):
    click.echo("--- Interactive Review Session ---")
    try:
        with open(json_path, 'r', encoding='utf-8') as f: data = json.load(f)
        extraction = ArticleExtraction(**data)
        click.secho(f"Successfully loaded '{json_path}' for review.", fg="green")
    except Exception as e:
        click.secho(f"Error loading or parsing JSON file: {e}", fg="red"); sys.exit(1)
    if extraction.pico_elements:
        pico = extraction.pico_elements
        click.echo("\n--- Reviewing PICO Elements ---")
        click.echo(f"  Population: {pico.population}")
        click.echo(f"  Intervention: {pico.intervention}")
        click.echo(f"  Comparison: {pico.comparison}")
        click.echo(f"  Outcome: {pico.outcome}")
        click.echo(f"  Current Status: {pico.correction_metadata.status.value}")
        action = click.prompt("(v)erify, (r)eject, or (s)kip?", type=str, default='s').lower()
        if action == 'v': pico.correction_metadata.status = ValidationStatus.VERIFIED; pico.correction_metadata.last_reviewed = datetime.utcnow()
        elif action == 'r': pico.correction_metadata.status = ValidationStatus.REJECTED; pico.correction_metadata.last_reviewed = datetime.utcnow(); pico.correction_metadata.reviewer_comment = click.prompt("Rejection reason (optional)", type=str, default="")
    for i, score in enumerate(extraction.quality_scores):
        click.echo(f"\n--- Reviewing Quality Score {i+1} ---")
        click.echo(f"  Score Name: {score.score_name}")
        click.echo(f"  Score Value: {score.score_value}")
        click.echo(f"  Justification: {score.justification}")
        click.echo(f"  Current Status: {score.correction_metadata.status.value}")
        action = click.prompt("(v)erify, (r)eject, or (s)kip?", type=str, default='s').lower()
        if action == 'v': score.correction_metadata.status = ValidationStatus.VERIFIED; score.correction_metadata.last_reviewed = datetime.utcnow()
        elif action == 'r': score.correction_metadata.status = ValidationStatus.REJECTED; score.correction_metadata.last_reviewed = datetime.utcnow(); score.correction_metadata.reviewer_comment = click.prompt("Rejection reason (optional)", type=str, default="")
    for i, claim in enumerate(extraction.claims):
        click.echo(f"\n--- Reviewing Claim {i+1} ---")
        click.echo(f"  Claim Text: {claim.claim_text}")
        click.echo(f"  Provenance: Page {claim.provenance.page_number}")
        click.echo(f"  Current Status: {claim.correction_metadata.status.value}")
        action = click.prompt("(v)erify, (r)eject, or (s)kip?", type=str, default='s').lower()
        if action == 'v': claim.correction_metadata.status = ValidationStatus.VERIFIED; claim.correction_metadata.last_reviewed = datetime.utcnow()
        elif action == 'r': claim.correction_metadata.status = ValidationStatus.REJECTED; claim.correction_metadata.last_reviewed = datetime.utcnow(); claim.correction_metadata.reviewer_comment = click.prompt("Rejection reason (optional)", type=str, default="")
    click.echo("\n--- Review Complete ---")
    if click.confirm("Do you want to save your changes to the file?"): save_to_json(extraction, json_path)
    else: click.echo("Changes were not saved.")

@cli.command()
@click.argument("json_path", type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.option(
    "--output", "output_path", type=click.Path(dir_okay=False, writable=True, resolve_path=True),
    required=True, help="The path to save the output .xlsx spreadsheet.",
)
def export(json_path: str, output_path: str):
    logger.info(f"Loading '{json_path}' for export.")
    try:
        with open(json_path, 'r', encoding='utf-8') as f: data = json.load(f)
        extraction = ArticleExtraction(**data)
    except Exception as e:
        logger.error(f"Failed to load or parse JSON file: {e}"); sys.exit(1)
    export_to_excel(extraction, output_path)

if __name__ == "__main__":
    cli()