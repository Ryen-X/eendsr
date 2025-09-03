# Evidence-Extractor for Narrow-Domain Systematic Reviews

**A research software project for semi-automated evidence extraction from scholarly articles.**

## Overview

Manual screening and structured evidence extraction is a slow and inconsistent bottleneck for systematic reviews. This project, `evidence-extractor`, provides a domain-specific, reproducible tool to accelerate this process. It outputs structured claims, PICO fields, quality scores, and detailed provenance.

This is not a generic "PaperGPT"; it is designed to be tuned to a specific domain (e.g., ecology, clinical diagnostics) for higher accuracy and relevance.

### Core Features (Planned)

*   PDF ingestion and citation parsing.
*   Extraction of structured claims, PICO fields, and quality scores using Google's Gemini models.
*   Table and figure extraction with caption analysis.
*   Detailed provenance linking claims to their source page.
*   Human-in-the-loop review and validation workflow.
*   Export to structured formats (JSON, XLSX) and machine-readable PRISMA artifacts (text reports and diagrams).

## Installation

### System Dependencies

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

### Python Package

_Instructions to be added in a future phase._

```bash
pip install evidence-extractor
```

## Usage
A basic CLI usage example will be added here.
code
Bash
evidence-extractor extract --pdf path/to/paper.pdf --output results.json

## Contributing

Contributions are welcome! Please see our contributing guidelines for more details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.