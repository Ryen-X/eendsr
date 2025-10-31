import logging

from graphviz import Digraph

from evidence_extractor.models.schemas import ArticleExtraction

logger = logging.getLogger(__name__)


def generate_prisma_diagram(extraction: ArticleExtraction, output_path: str):
    logger.info(f"Generating PRISMA flow diagram at '{output_path}.png'")
    dot = Digraph("PRISMA Flow Diagram")
    dot.attr("graph", rankdir="TB", splines="ortho", ranksep="0.6")
    dot.attr(
        "node",
        shape="box",
        style="rounded,filled",
        fillcolor="whitesmoke",
        fontname="helvetica",
    )
    dot.attr("edge", fontname="helvetica", fontsize="10")
    n_identified = 1
    n_screened = 1
    n_excluded = extraction.records_excluded_count
    n_included = n_screened - n_excluded
    dot.node("identification", f"Records identified (n = {n_identified})")
    dot.node("screening", f"Records screened (n = {n_screened})")
    dot.node("included", f"Studies included in synthesis (n = {n_included})")
    if n_excluded > 0:
        dot.node(
            "excluded", f"Records excluded (n = {n_excluded})", fillcolor="lightcoral"
        )
    dot.edge("identification", "screening", arrowhead="none")
    if n_excluded > 0:
        dot.edge(
            "screening",
            "excluded",
            label="  Exclusion reason: N/A for single-file tool",
        )
    dot.edge("screening", "included", arrowhead="none")

    try:
        dot.render(output_path, format="png", cleanup=True)
        logger.info("PRISMA diagram generated successfully.")
    except Exception as e:
        logger.error(
            "Failed to generate PRISMA diagram. Is Graphviz installed on your "
            f"system? Error: {e}"
        )
