import logging
from typing import Dict, List

from thefuzz import fuzz

logger = logging.getLogger(__name__)


def calculate_claim_metrics(
    extracted_claims: List[str], gold_standard_claims: List[str]
) -> Dict[str, float]:
    true_positives = 0
    false_positives = 0

    if not gold_standard_claims:
        return {
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0,
            "true_positives": 0,
            "false_positives": len(extracted_claims),
            "false_negatives": 0,
        }
    matched_gold_indices = set()

    for extracted in extracted_claims:
        is_match_found = False
        for i, gold in enumerate(gold_standard_claims):
            if fuzz.partial_ratio(extracted.lower(), gold.lower()) > 95:
                if i not in matched_gold_indices:
                    true_positives += 1
                    matched_gold_indices.add(i)
                    is_match_found = True
                    break

        if not is_match_found:
            false_positives += 1

    false_negatives = len(gold_standard_claims) - len(matched_gold_indices)

    precision = (
        true_positives / (true_positives + false_positives)
        if (true_positives + false_positives) > 0
        else 0.0
    )
    recall = (
        true_positives / (true_positives + false_negatives)
        if (true_positives + false_negatives) > 0
        else 0.0
    )
    f1_score = (
        2 * (precision * recall) / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )

    logger.info(
        f"Evaluation complete: TP={true_positives}, FP={false_positives}, "
        f"FN={false_negatives}"
    )

    return {
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
    }
