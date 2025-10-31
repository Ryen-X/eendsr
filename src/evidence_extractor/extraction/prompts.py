# Central repository for all LLM prompt templates

ORCHESTRATION_PROMPT = """
You are an expert research assistant. Analyze the following text from a scientific
paper and extract the requested information.

Return a single, valid JSON object with three top-level keys: "pico", "quality",
and "claims".

1.  **pico**: An object with keys "population", "intervention", "comparison", and
    "outcome". If an element is not found, its value should be null.
2.  **quality**: An object based on the study design. It must have keys
    "score_name" (always "Methodological Quality"), "score_value" ("High",
    "Medium", or "Low"), and "justification".
    - "High": Randomized Controlled Trial (RCT), Systematic Review.
    - "Medium": Cohort Study, Case-Control Study.
    - "Low": Case Report, Cross-Sectional Study, unclear methodology.
3.  **claims**: A JSON array of objects. Each object represents a key factual
    finding and must have a single key: "claim_text". Do not extract general
    statements or background info.

Do not include any explanatory text or markdown formatting around the final JSON
object.

--- TEXT ---
{text_snippet}
--- END TEXT ---

JSON Response:
"""

UNCERTAINTY_PROMPT = """
Analyze the linguistic certainty for each scientific claim in the numbered list
below. For each claim, classify its confidence level as "High", "Medium", or "Low"
based on its wording.

- "High": Definitive language (e.g., "we demonstrate", "proves", "shows a
  significant increase").
- "Medium": Cautious language (e.g., "suggests", "is associated with", "may
  indicate").
- "Low": Speculative language (e.g., "could potentially", "further research is
  needed").

Return a single, valid JSON array where each object corresponds to a claim in the
original list. Each object must have two keys:
1. "claim_index": The original number of the claim (e.g., 1, 2, 3...).
2. "annotation": A string that includes the confidence level and a brief
   justification.

--- CLAIM LIST ---
{formatted_claims}
--- END CLAIM LIST ---

JSON Response:
"""

SUMMARY_PROMPT = """
Based on the following list of key findings extracted from a research paper, write
a single, concise paragraph that summarizes the main conclusions of the study.
Synthesize the points into a coherent narrative. Do not simply list them.
The tone should be objective and academic.
Start the paragraph directly, without any introductory phrases like "This paper
concludes that...".

--- KEY FINDINGS ---
{formatted_claims}
--- END KEY FINDINGS ---

Summary Paragraph:
"""

FIGURE_CAPTION_PROMPT = """
Analyze this image from a research paper. Your task is to identify its caption.
The caption is typically the text block directly below the figure, often starting
with "Figure X:".
Respond with ONLY the full caption text. Do not add any other explanation.
If you cannot find a caption, respond with "No caption found.".
"""

TABLE_PARSING_PROMPT = """
Analyze the following image of a table from a research paper.

Your task is to:
1.  Identify the column headers.
2.  Extract the data for each row.
3.  Provide a one-sentence summary of the table's main finding.

Return a single, valid JSON object with two keys: "summary" and
"structured_data".
- The value for "summary" should be the summary string.
- The value for "structured_data" should be a JSON array of objects, where each
  object represents a row and the keys are the column headers.

If a cell spans multiple rows, repeat its value for each row it covers.
If the table is unreadable, return an empty "structured_data" array.
Do not include any explanatory text or markdown formatting around the JSON object.
"""
