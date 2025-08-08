# Evidence-Extractor for Narrow-Domain Systematic Reviews

**A research software project for semi-automated evidence extraction from scholarly articles.**

## Overview

Manual screening and structured evidence extraction is a slow and inconsistent bottleneck for systematic reviews. This project, `evidence-extractor`, provides a domain-specific, reproducible tool to accelerate this process. It outputs structured claims, PICO fields, quality scores, and detailed provenance.

This is not a generic "PaperGPT"; it is designed to be tuned to a specific domain (e.g., ecology, clinical diagnostics) for higher accuracy and relevance.

### Core Features (Planned)

*   PDF ingestion and citation parsing.
*   Extraction of structured claims, PICO fields, and quality scores.
*   Table and figure extraction.
*   Detailed provenance linking claims to their source (page/line).
*   Human-in-the-loop correction workflow.
*   Export to structured formats (JSON, CSV) and machine-readable PRISMA artifacts.

## Installation

_Instructions to be added in a future phase._

```bash
pip install evidence-extractor
```

### Usage
A basic CLI usage example will be added here.
code
```bash
evidence-extractor extract --pdf path/to/paper.pdf --output results.json
```

### Contributing
Contributions are welcome! Please see our contributing guidelines for more details.
License
This project is licensed under the MIT License - see the LICENSE file for details.