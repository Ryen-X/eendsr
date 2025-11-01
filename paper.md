---
title: 'Evidence-Extractor: A Python Framework for Semi-Automated, Human-in-the-Loop Data Extraction in Systematic Reviews'
tags:
  - Python
  - systematic reviews
  - natural language processing
  - large language models
  - evidence synthesis
  - research automation
  - scholarly communication
authors:
  - name: Aaryan Singh
    orcid: 0009-0004-0832-0161
    affiliation: 1
affiliations:
 - name: Independent Researcher
   index: 1
date: 01 November 2025
bibliography: paper.bib
---

# Summary

`Evidence-Extractor` is an open-source Python library and command-line tool designed to accelerate the evidence synthesis process in systematic reviews. The manual extraction of structured data from large volumes of scholarly articles is a primary bottleneck in research, characterized by its time-intensive nature and susceptibility to inter-annotator variability. Our software addresses this challenge by employing a semi-automated, human-in-the-loop (HITL) workflow. It leverages the capabilities of large language models (LLMs), specifically Google's Gemini, to perform initial, structured data extraction from PDF articles. The software identifies and parses key research components, including PICO elements (Population, Intervention, Comparison, Outcome), methodological details, primary claims, and data from tables and figures. Crucially, all AI-generated data is then subjected to a built-in interactive review process, empowering the researcher to validate, correct, or reject extractions. The final, verified data can be exported into multiple formats, including machine-readable JSON, user-friendly XLSX spreadsheets, and publication-ready PRISMA-style artifacts.

# Statement of Need

The exponential growth of scientific literature presents a significant challenge to the practice of evidence-based research. Systematic reviews, which form the foundation of meta-analyses and clinical guidelines, depend on the meticulous and consistent extraction of data from a corpus of studies. The manual nature of this task is not only a major resource constraint but also a source of potential bias and error. While recent advances in natural language processing have introduced tools for general document summarization, these often lack the specificity and structured output required for rigorous, quantitative evidence synthesis. Researchers do not just need summaries; they need discrete, comparable data points (e.g., sample sizes, outcome measures, specific factual claims) formatted consistently across diverse sources.

`Evidence-Extractor` is designed to fill this methodological gap. It is not a fully autonomous "black box" but a transparent co-pilot for the researcher. By providing a strong, AI-generated first pass of data extraction, it significantly reduces the cognitive load and manual effort required. Its integrated HITL validation workflow is fundamental to its design, ensuring that the final dataset is a product of expert human oversight, thereby maintaining the high standards of scholarly rigor. The software's ability to link extracted claims to their page-level provenance further enhances the transparency and verifiability of the entire process. By streamlining the most laborious phase of a systematic review, `Evidence-Extractor` enables researchers to focus their efforts on higher-level analysis and interpretation, ultimately accelerating the pace of scientific discovery.

# Key Features and Functionality

*   **Multi-Modal PDF Ingestion**: The software ingests text-based PDF documents and can process textual content, identify graphical elements, and locate tables using a hybrid approach of heuristic parsing (PyMuPDF [@fitz], Camelot [@camelot]) and multimodal LLM analysis (Gemini Vision API).

*   **Structured, AI-Powered Extraction**: A core orchestration module makes a single, efficient call to the Gemini API to extract multiple structured fields simultaneously, including PICO elements, a methodological quality assessment, and a list of primary scientific claims.

*   **Human-in-the-Loop (HITL) Validation**: A built-in interactive command-line interface (`review`) allows researchers to systematically approve, reject, or edit every piece of AI-generated data. This process enriches the data with a verifiable audit trail (validation status, timestamps).

*   **Comprehensive Output Generation**: The `export` command generates a suite of research artifacts from the validated data, including:
    *   A detailed XLSX spreadsheet with separate tabs for claims, tables, and a study summary.
    *   A PRISMA-style text report summarizing the extraction process.
    *   A PRISMA 2020 flow diagram (PNG) generated via Graphviz, suitable for inclusion in publications.

*   **Robust and Extensible**: The codebase is fully typed, modular, and accompanied by a comprehensive test suite using `pytest`, including unit and integration tests. A continuous integration workflow enforces code quality and correctness, and the project is structured to be extensible for future research and domain-specific adaptations.

`Evidence-Extractor` represents a significant step towards integrating modern AI capabilities into the systematic review workflow in a practical, responsible, and research-centric manner.

# Acknowledgements

We acknowledge the contributions of the open-source community and the developers of the core libraries that make this project possible.

# References
