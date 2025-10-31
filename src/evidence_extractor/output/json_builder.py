import logging

from evidence_extractor.models.schemas import ArticleExtraction

logger = logging.getLogger(__name__)


def save_to_json(extraction_result: ArticleExtraction, output_path: str):
    logger.info(f"Attempting to save extraction results to '{output_path}'...")
    try:
        json_output = extraction_result.model_dump_json(indent=2)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(json_output)
        logger.info(f"Successfully saved structured JSON output to '{output_path}'.")
    except TypeError as e:
        logger.error(f"A TypeError occurred during JSON serialization: {e}")
    except IOError as e:
        logger.error(f"An IOError occurred while writing to file '{output_path}': {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during JSON output generation: {e}")
