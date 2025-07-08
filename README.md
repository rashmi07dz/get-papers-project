# {get_papers_with_pharma_authors]

## PubMed Paper Filter CLI Tool

![Python](https://img.shields.io/badge/Python-3.12%2B-blue?style=for-the-badge&logo=python)
![Poetry](https://img.shields.io/badge/Poetry-Enabled-green?style=for-the-badge&logo=poetry)
![GitHub](https://img.shields.io/github/stars/rashmi07dz/get-papers-project?style=for-the-badge&logo=github)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

---

## 📝 Description

This is a command-line interface (CLI) tool designed to fetch academic paper information from PubMed, specifically filtering for articles that may have non-academic authors based on their affiliation details. It helps researchers and analysts identify publications potentially influenced by industry or private entities.

## ✨ Features

* **PubMed Integration**: Fetches paper IDs and detailed XML data directly from the PubMed E-utilities API.
* **Affiliation Parsing**: Extracts article titles, authors, PMIDs, and their affiliations from complex PubMed XML responses.
* **Non-Academic Filtering**: Identifies authors from non-academic institutions (e.g., companies, pharmaceutical industries, private entities) based on a configurable keyword list.
* **CSV Output**: Saves filtered paper details (PMID, Title, Authors, Affiliations) into a structured CSV file for easy analysis.
* **Python Poetry Setup**: Manages project dependencies and virtual environments using Poetry for a clean development workflow.

## 🚀 Installation

To set up this project locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/rashmi07dz/get-papers-project.git](https://github.com/rashmi07dz/get-papers-project.git)
    cd get-papers-project
    ```

2.  **Install Poetry (if you don't have it):**
    ```bash
    pip install poetry
    ```
    (Or follow the official Poetry installation guide for your OS.)

3.  **Install project dependencies using Poetry:**
    ```bash
    poetry install
    ```

## 💡 Usage

Run the CLI tool using `poetry run` followed by the command and your PubMed query.

```bash
poetry run get-papers-list "your search query"