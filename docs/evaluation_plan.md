# Evaluation Plan for Research Utility

This document outlines the experimental design for evaluating the practical utility of the `evidence-extractor` tool beyond simple precision and recall metrics. These evaluations are designed to measure the tool's impact on the speed and consistency of the systematic review process.

## 1. Annotation Time Savings Evaluation

### Objective
To quantify the reduction in time required for a human researcher to perform structured data extraction using the tool versus a fully manual process.

### Experimental Design

1.  **Participants**: A group of researchers (e.g., graduate students) familiar with the review domain but not with the software.
2.  **Materials**:
    *   A set of 10 representative research papers from the target domain.
    *   A standardized spreadsheet template for manual data entry (columns for PICO, Claims, etc.).
    *   The `evidence-extractor` software.
3.  **Procedure**:
    *   The participant group is split into two: Group A (Manual First) and Group B (Tool First). This is a crossover design to control for learning effects.
    *   **Manual Round**: Participants are given 5 papers and the spreadsheet template. They are timed on how long it takes to read the papers and fill in the required data fields manually.
    *   **Tool-Assisted Round**: Participants are given the other 5 papers. They first run the `evidence-extractor` `extract` command on each paper. They then run the `review` command to correct the AI-generated output. They are timed on how long this entire process takes (running the tool + reviewing/correcting).
    *   Group A performs the Manual Round first, then the Tool-Assisted Round. Group B does the reverse.
4.  **Metrics**:
    *   `T_manual`: Average time per paper for the manual process.
    *   `T_tool`: Average time per paper for the tool-assisted process.
    *   **Time Savings (%)**: `(1 - (T_tool / T_manual)) * 100`.
5.  **Hypothesis**: The tool-assisted process (`T_tool`) will be significantly faster than the manual process (`T_manual`).

## 2. Inter-Annotator Agreement (IAA) Improvement Evaluation

### Objective
To measure whether using the tool as a starting point increases the consistency (agreement) between two independent researchers.

### Experimental Design

1.  **Participants**: At least two independent researchers (annotators).
2.  **Materials**:
    *   A set of 5 research papers.
    *   The `evidence-extractor` software.
3.  **Procedure**:
    *   **Round 1 (Manual IAA)**: Both annotators independently perform manual extraction on the 5 papers.
    *   **Round 2 (Tool-Assisted IAA)**: For the same 5 papers, both annotators are given the *same* initial AI-generated `results.json` file from the tool. They then independently run the `review` process to produce their own corrected versions of the file.
4.  **Metrics**:
    *   **Cohen's Kappa (κ)** or a similar IAA statistic will be calculated for both rounds. The agreement will be measured on a per-claim basis (i.e., did both annotators extract the same set of claims?).
    *   `κ_manual`: The IAA score from the manual round.
    *   `κ_tool`: The IAA score from the tool-assisted round.
5.  **Hypothesis**: The IAA score for the tool-assisted round (`κ_tool`) will be significantly higher than for the manual round (`κ_manual`), as both annotators started from the same AI-generated baseline.

## Conclusion

Executing these experiments would provide strong quantitative evidence for the utility of `evidence-extractor` as a research tool, supporting its value to the scientific community beyond its technical implementation.