# Africa AI Village Expo Data Collection System

A comprehensive web scraping and data aggregation system designed to collect public reactions, sentiment, and detailed information regarding the **Africa AI Village Expo** held in India.

This system is built upon the [Scrapling](https://github.com/D4Vinci/Scrapling) framework, utilizing its advanced stealth, adaptive parsing, and deep-crawling capabilities.

## 🚀 Key Features

- **Multi-Platform Search**: Aggregates data from LinkedIn, Twitter/X, Reddit, and news portals.
- **Deep Extraction**: Uses `SearchFetcher` for high-depth crawling and content extraction.
- **Adaptive Resilience**: Leverages Scrapling's adaptive parsing to maintain data integrity even if website structures change.
- **Scalable Collection**: Includes both targeted scraping for quick results and exhaustive crawling for massive datasets.

## 📁 System Components

- **`deep_scrape_africa_ai.py`**: A targeted script for gathering specific reactions and reviews. Uses `search_and_extract` with deep extraction enabled.
- **`exhaustive_scrape.py`**: A large-scale crawler that discovers and navigates domains to build an extensive dataset. Uses `crawl_and_extract` with multi-page depth.
- **`cleanup.py`**: Utility for maintaining the project environment by cleaning up build artifacts and cache files.
- **`benchmarks.py`**: Performance monitoring tool to ensure scraping efficiency.

## 🛠️ Getting Started (Best Steps for Running)

Follow these steps to set up and run the system effectively from a clean environment.

### 1. Environment Setup
Create and activate a dedicated virtual environment to avoid dependency conflicts.

```bash
# Create a virtual environment
python3 -m venv venv

# Activate it (Linux/macOS)
source venv/bin/activate
```

### 2. Install Project & Dependencies
Install the package in **editable mode** with all optional features enabled. This ensures that the local `scrapling/` module is used and all AI/Shell features are available.

```bash
# Install everything (including AI and Shell extensions)
pip install -e ".[all]"
```

### 3. Initialize Browsers
The system uses stealthy and dynamic browsers that require specific binaries and fingerprinting data.

```bash
# Download and configure browsers
scrapling install
```

## 📈 Running the System

### 🔍 Targeted Deep Scrape
Best for gathering specific, high-quality reactions and comments.
```bash
python deep_scrape_africa_ai.py
```
*   **Input**: Pre-defined queries in the script.
*   **Output**: `africa_ai_deep_reactions.csv`
*   **When to use**: When you need deep contextual data from social media and news.

### 🕷️ Exhaustive Mega-Crawl
Best for building a massive dataset by navigating through multiple levels of different domains.
```bash
python exhaustive_scrape.py
```
*   **Input**: Broad and specific summit-related queries.
*   **Output**: `africa_ai_summit_2026_specific.csv`
*   **When to use**: For comprehensive event coverage and discovering hidden mentions.

### 🧹 Maintenance
Clean up build artifacts and temporary files.
```bash
python cleanup.py
```

## 💡 Best Practices for Best Results

1.  **Proxies**: If you are running large-scale crawls with `exhaustive_scrape.py`, it is highly recommended to configure a `ProxyRotator` within the scripts to avoid search engine rate limits.
2.  **Graceful Shutdown**: The Scrapling framework supports **Pause & Resume**. If a crawl is taking too long, press `Ctrl+C`. The progress is saved, and you can resume later.
3.  **Headless Mode**: For production runs, ensure `headless=True` is set in the fetcher calls (default in these scripts). If you want to debug, you can temporarily set it to `False`.
4.  **Network Stability**: Both scripts include retry logic, but ensure you have a stable connection as `SearchFetcher` handles complex network idle states.

## 📊 Data Output Format

All results are aggregated into CSV files with the following structure:
- `url`: Source link.
- `title`: Extracted page title.
- `text`: Main body content or summarized text.
- `contexts`: Key snippets and surrounding context identifying why the page was relevant.

## ⚖️ License & Disclaimer

This project is intended for research and educational purposes. Ensure compliance with terms of service and `robots.txt` of the target websites.

---
*Built with ❤️ using [Scrapling](https://github.com/D4Vinci/Scrapling).*
