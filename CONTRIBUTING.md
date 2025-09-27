# Contributing to Evidence-Extractor

First off, thank you for considering contributing! This project is an open-source tool for the research community, and we welcome any help to make it better.

## How Can I Contribute?

### Reporting Bugs
If you find a bug, please open an issue on our GitHub repository. Be sure to include:
- Your operating system and Python version.
- The version of `evidence-extractor` you are using.
- A clear description of the bug.
- Steps to reproduce the bug, including a sample PDF if possible (please ensure it is publicly accessible and not under copyright restrictions).
- The full traceback if the application crashed.

### Suggesting Enhancements
If you have an idea for a new feature or an improvement to an existing one, please open an issue. We would love to hear your thoughts on how to make the tool more useful.

### Code Contributions
If you would like to contribute code, please follow these steps:
1.  **Fork the repository** on GitHub.
2.  **Create a new branch** for your feature or bug fix (e.g., `git checkout -b feature/new-claim-parser`).
3.  **Set up your development environment**:
    ```bash
    # Create and activate a virtual environment
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

    # Install the project in editable mode with all dev dependencies
    pip install -e ".[test,notebook]"
    ```
4.  **Make your changes.** Please ensure your code follows the existing style.
5.  **Add tests** for your new feature or bug fix. We use `pytest` for our test suite. Run the tests to make sure everything is still working:
    ```bash
    # Run fast unit tests
    pytest -m "not integration"

    # Run slow integration tests (requires a configured .env file)
    pytest -m "integration"
    ```
6.  **Update the documentation** if you have changed the user-facing API or added a new feature.
7.  **Commit your changes** with a clear and descriptive commit message.
8.  **Push your branch** to your fork on GitHub.
9.  **Open a Pull Request** to the `main` branch of the original repository.

We will review your pull request as soon as possible. Thank you for your contribution!