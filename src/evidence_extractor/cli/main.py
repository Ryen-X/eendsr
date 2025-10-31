import json
import logging
import sys
from datetime import datetime

import click

from evidence_extractor.core.ingest import ingest_pdf
from evidence_extractor.core.preprocess import (
    clean_and_consolidate_text,
    extract_text_from_doc,
)
from evidence_extractor.core.provenance import find_claim_provenance
from evidence_extractor.evaluation.metrics import calculate_claim_metrics
from evidence_extractor.extraction.citations import (
    find_references_section,
    link_in_text_citations,
    parse_bibliography,
)
from evidence_extractor.extraction.figures import extract_figures_and_captions
from evidence_extractor.extraction.llm_orchestrator import orchestrate_llm_extraction
from evidence_extractor.extraction.summarization import generate_summary
from evidence_extractor.extraction.tables import extract_tables_with_llm
from evidence_extractor.extraction.uncertainty import annotate_claims_in_batch
from evidence_extractor.integration.gemini_client import GeminiClient
from evidence_extractor.models.schemas import (
    PICO,
    ArticleExtraction,
    Claim,
    Provenance,
    QualityScore,
    ValidationStatus,
)
from evidence_extractor.output.json_builder import save_to_json
from evidence_extractor.output.prisma import (
    generate_prisma_text_report,
    save_prisma_report,
)
from evidence_extractor.output.prisma_diagram import generate_prisma_diagram
from evidence_extractor.output.spreadsheet import export_to_excel
from evidence_extractor.utils.logging_config import setup_logging

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
    click.secho("--- Evidence Extractor ---", fg="cyan", bold=True)
    logger.info(f"Received request to process PDF: {pdf_path}")
    extraction_result = ArticleExtraction(source_filename=pdf_path)
    gemini_client = GeminiClient()
    if not gemini_client.is_configured():
        logger.warning("Gemini client not configured.")
    document = ingest_pdf(pdf_path)
    if not document:
        sys.exit(1)
    pages_text = extract_text_from_doc(document)
    text_with_newlines, cleaned_text = clean_and_consolidate_text(pages_text)
    if not cleaned_text:
        document.close()
        sys.exit(1)
    if gemini_client.is_configured():
        llm_payload = orchestrate_llm_extraction(gemini_client, cleaned_text[:16000])
        if llm_payload:
            if llm_payload.get("pico"):
                extraction_result.pico_elements = PICO(**llm_payload["pico"])
            if llm_payload.get("quality"):
                extraction_result.quality_scores.append(
                    QualityScore(**llm_payload["quality"])
                )
            claim_data = llm_payload.get("claims", [])
            if claim_data:
                temp_claims = []
                for item in claim_data:
                    text = item.get("claim_text")
                    if text:
                        page_num = find_claim_provenance(text, pages_text)
                        provenance = Provenance(
                            source_filename=pdf_path, page_number=page_num
                        )
                        claim = Claim(claim_text=text, provenance=provenance)
                        temp_claims.append(claim)
                annotate_claims_in_batch(gemini_client, temp_claims)
                extraction_result.claims = temp_claims
                summary = generate_summary(gemini_client, extraction_result.claims)
                if summary:
                    extraction_result.summary = summary
                    click.secho("\n--- Generated Summary ---", fg="green")
                    click.echo(summary)
                    click.secho("-----------------------", fg="green")
        figures = extract_figures_and_captions(document, gemini_client)
        if figures:
            extraction_result.figures = figures
    if gemini_client.is_configured():
        tables = extract_tables_with_llm(document, gemini_client)
        if tables:
            extraction_result.tables = tables
    else:
        logger.warning(
            "Skipping advanced table extraction as Gemini client is not configured."
        )
    refs_tuple = find_references_section(text_with_newlines)
    if refs_tuple:
        refs_text, start_idx = refs_tuple
        bib = parse_bibliography(refs_text)
        extraction_result.bibliography = bib
        body_text = text_with_newlines[:start_idx]
        link_in_text_citations(body_text, extraction_result.bibliography)
    save_to_json(extraction_result, output_path)
    document.close()
    click.secho("\nProcessing complete.", fg="green", bold=True)
    sys.exit(0)


@cli.command()
@click.argument(
    "json_path", type=click.Path(exists=True, dir_okay=False, resolve_path=True)
)
def review(json_path: str):
    click.echo("--- Interactive Review Session ---")
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        extraction = ArticleExtraction(**data)
        click.secho(f"Successfully loaded '{json_path}' for review.", fg="green")
    except Exception as e:
        click.secho(f"Error loading or parsing JSON file: {e}", fg="red")
        sys.exit(1)
    if extraction.pico_elements:
        pico = extraction.pico_elements
        click.echo("\n--- Reviewing PICO Elements ---")
        click.echo(f"  Population: {pico.population}")
        click.echo(f"  Intervention: {pico.intervention}")
        click.echo(f"  Comparison: {pico.comparison}")
        click.echo(f"  Outcome: {pico.outcome}")
        click.echo(f"  Current Status: {pico.correction_metadata.status.value}")
        action = click.prompt(
            "(v)erify, (r)eject, or (s)kip?", type=str, default="s"
        ).lower()
        if action == "v":
            pico.correction_metadata.status = ValidationStatus.VERIFIED
            pico.correction_metadata.last_reviewed = datetime.utcnow()
        elif action == "r":
            pico.correction_metadata.status = ValidationStatus.REJECTED
            pico.correction_metadata.last_reviewed = datetime.utcnow()
            pico.correction_metadata.reviewer_comment = click.prompt(
                "Rejection reason (optional)", type=str, default=""
            )
    for i, score in enumerate(extraction.quality_scores):
        click.echo(f"\n--- Reviewing Quality Score {i + 1} ---")
        click.echo(f"  Score Name: {score.score_name}")
        click.echo(f"  Score Value: {score.score_value}")
        click.echo(f"  Justification: {score.justification}")
        click.echo(f"  Current Status: {score.correction_metadata.status.value}")
        action = click.prompt(
            "(v)erify, (r)eject, or (s)kip?", type=str, default="s"
        ).lower()
        if action == "v":
            score.correction_metadata.status = ValidationStatus.VERIFIED
            score.correction_metadata.last_reviewed = datetime.utcnow()
        elif action == "r":
            score.correction_metadata.status = ValidationStatus.REJECTED
            score.correction_metadata.last_reviewed = datetime.utcnow()
            score.correction_metadata.reviewer_comment = click.prompt(
                "Rejection reason (optional)", type=str, default=""
            )
    for i, claim in enumerate(extraction.claims):
        click.echo(f"\n--- Reviewing Claim {i + 1} ---")
        click.echo(f"  Claim Text: {claim.claim_text}")
        click.echo(f"  Provenance: Page {claim.provenance.page_number}")
        click.echo(f"  Current Status: {claim.correction_metadata.status.value}")
        action = click.prompt(
            "(v)erify, (r)eject, or (s)kip?", type=str, default="s"
        ).lower()
        if action == "v":
            claim.correction_metadata.status = ValidationStatus.VERIFIED
            claim.correction_metadata.last_reviewed = datetime.utcnow()
        elif action == "r":
            claim.correction_metadata.status = ValidationStatus.REJECTED
            claim.correction_metadata.last_reviewed = datetime.utcnow()
            claim.correction_metadata.reviewer_comment = click.prompt(
                "Rejection reason (optional)", type=str, default=""
            )
    click.echo("\n--- Review Complete ---")
    if click.confirm("Do you want to save your changes to the file?"):
        save_to_json(extraction, json_path)
    else:
        click.echo("Changes were not saved.")


@cli.command()
@click.argument(
    "json_path", type=click.Path(exists=True, dir_okay=False, resolve_path=True)
)
@click.option(
    "--output",
    "output_path",
    type=click.Path(dir_okay=False, writable=True, resolve_path=True),
    required=True,
)
@click.option(
    "--prisma",
    "prisma_path",
    type=click.Path(dir_okay=False, writable=True, resolve_path=True),
)
@click.option(
    "--prisma-diagram",
    "prisma_diagram_path",
    type=click.Path(dir_okay=False, writable=True, resolve_path=True),
)
def export(
    json_path: str, output_path: str, prisma_path: str, prisma_diagram_path: str
):
    logger.info(f"Loading '{json_path}' for export.")
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        extraction = ArticleExtraction(**data)
    except Exception as e:
        logger.error(f"Failed to load or parse JSON file: {e}")
        sys.exit(1)
    export_to_excel(extraction, output_path)
    if prisma_path:
        report_content = generate_prisma_text_report(extraction)
        save_prisma_report(report_content, prisma_path)
    if prisma_diagram_path:
        generate_prisma_diagram(extraction, prisma_diagram_path)


@cli.command()
@click.option(
    "--pdf",
    "pdf_path",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    required=True,
)
@click.option(
    "--gold-standard",
    "gold_standard_path",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    required=True,
)
def evaluate(pdf_path: str, gold_standard_path: str):
    logger.info("--- Performance Evaluation Mode ---")
    try:
        with open(gold_standard_path, "r") as f:
            gold_data = json.load(f)
        gold_claims = [item["claim_text"] for item in gold_data.get("claims", [])]
        logger.info(f"Loaded {len(gold_claims)} claims from gold standard file.")
    except Exception as e:
        logger.error(f"Failed to load or parse gold standard file: {e}")
        sys.exit(1)
    gemini_client = GeminiClient()
    if not gemini_client.is_configured():
        logger.error("Cannot run evaluation; Gemini client not configured.")
        sys.exit(1)
    document = ingest_pdf(pdf_path)
    if not document:
        sys.exit(1)
    pages_text = extract_text_from_doc(document)
    _, cleaned_text = clean_and_consolidate_text(pages_text)
    llm_payload = orchestrate_llm_extraction(gemini_client, cleaned_text[:16000])
    extracted_claims_text = []
    if llm_payload and llm_payload.get("claims"):
        extracted_claims_text = [
            item.get("claim_text", "")
            for item in llm_payload["claims"]
            if item.get("claim_text")
        ]
    logger.info(f"Extraction pipeline generated {len(extracted_claims_text)} claims.")
    metrics = calculate_claim_metrics(extracted_claims_text, gold_claims)
    click.echo("\n--- Claim Extraction Performance ---")
    click.secho(f"  Precision: {metrics['precision']:.2f}", fg="yellow")
    click.secho(f"  Recall:    {metrics['recall']:.2f}", fg="yellow")
    click.secho(f"  F1-Score:  {metrics['f1_score']:.2f}", fg="yellow")
    click.echo("  ----------------------------------")
    click.echo(f"  True Positives:  {metrics['true_positives']}")
    click.echo(f"  False Positives: {metrics['false_positives']}")
    click.echo(f"  False Negatives: {metrics['false_negatives']}")
    click.echo("------------------------------------")


if __name__ == "__main__":
    cli()
