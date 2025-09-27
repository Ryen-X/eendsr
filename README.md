# Evidence-Extractor for Narrow-Domain Systematic Reviews

**A research software project for semi-automated evidence extraction from scholarly articles using Large Language Models.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

Manual screening and structured evidence extraction is a slow and inconsistent bottleneck for systematic reviews. This project, `evidence-extractor`, provides a domain-specific, reproducible tool to accelerate this process by leveraging Google's Gemini models. It ingests PDF articles and outputs structured claims, PICO fields, quality scores, and detailed provenance.

This is not a generic "PaperGPT"; it is designed to be tuned to a specific domain (e.g., ecology, clinical diagnostics) for higher accuracy and relevance.

### Core Features

*   **PDF Ingestion**: Processes text-based PDF scholarly articles.
*   **AI-Powered Extraction**: Uses Google Gemini to extract:
    *   PICO Elements (Population, Intervention, Comparison, Outcome).
    *   Key scientific claims and findings.
    *   Methodological quality scores based on study design.
    *   Figure captions using multimodal vision capabilities.
*   **Advanced Table Structuring**: Locates tables, captures them as images, and uses Gemini Vision to parse them into structured data (JSON objects).
*   **Provenance**: Traces extracted claims back to the page number where they were found.
*   **Human-in-the-Loop (HITL)**: Includes an interactive CLI command to review, validate, and correct extracted data.
*   **Multiple Export Formats**: Generates structured JSON, user-friendly XLSX spreadsheets, and PRISMA-style text reports and flow diagrams.

## Installation

### 1. System Dependencies

This tool requires the **Graphviz** visualization software to generate PRISMA flow diagrams. Please install it before installing the Python package.

*   **macOS (using Homebrew):**
    ```bash
    brew install graphviz
    ```
*   **Linux (Debian/Ubuntu):**
    ```bash
    sudo apt-get update && sudo apt-get install -y graphviz
    ```
*   **Windows:**
    Download and run the installer from the [official Graphviz website](https://graphviz.org/download/). Ensure the `bin` directory is added to your system's PATH.

### 2. Python Package and Setup

This project is not yet on PyPI. To install it, clone the repository and install it in editable mode.

```bash
# Clone the repository
git clone https://github.com/your-username/evidence-extractor.git
cd evidence-extractor

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .
```

## 3. API Key Setup
The tool requires a Google Gemini API key.

Obtain a key from [Google AI Studio](https://aistudio.google.com).

Create a file named `.env` in the root of the project directory.

Add your key to the file like this:
```
GEMINI_API_KEY="YOUR_API_KEY_HERE"
```

### Usage

The tool provides three main commands: extract, review, and export:

### 1. Extract
This is the main command. It takes a PDF as input and generates a structured JSON file as output.
```
evidence-extractor extract --pdf path/to/paper.pdf --output results.json
```

### 2. Review
This command starts an interactive session to let you validate the findings in a generated JSON file.
```
evidence-extractor review results.json
```

You will be prompted to (v)erify, (r)eject, or (s)kip each extracted item. Your changes are saved back to the JSON file.


### 3. Export
This command converts a reviewed JSON file into more user-friendly formats:
### Export to an Excel spreadsheet
```
evidence-extractor export results.json --output summary.xlsx
```

### Generate PRISMA text report and flow diagram
```
evidence-extractor export results.json --output summary.xlsx --prisma report.txt --prisma-diagram flow
```

## Examples

For a hands-on guide, please see our example Jupyter Notebooks in the `/examples` directory:
1.  `01_basic_extraction_workflow.ipynb`: Covers the full `extract` -> `review` -> `export` workflow.
2.  `02_advanced_pico_extraction.ipynb`: Shows how to use the tool as a Python library in your own scripts.

## Contributing

Contributions are welcome! We encourage you to report bugs, suggest features, or submit pull requests. Please see our [**Contributing Guidelines**](CONTRIBUTING.md) for more details on how to get started.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.