# Universal Scraper

Universal Scraper is a powerful, adaptive, and stealthy web scraping system designed for the modern web. It handles everything from simple one-off requests to large-scale, deep-crawling operations.

## Key Features

- **Adaptive Parsing**: Automatically adjusts to website structure changes to maintain data extraction stability.
- **Advanced Stealth**: Built-in support for bypassing common anti-bot protections and Cloudflare interstitials.
- **Deep Extraction**: Intelligent content discovery and extraction using high-depth crawling strategies.
- **High Performance**: Optimized for speed with concurrent multi-session support and efficient data processing.

## System Components

- **`deep_scrape_africa_ai.py`**: Targeted extraction of reactions and sentiment from multiple platforms.
- **`exhaustive_scrape.py`**: Large-scale crawler for exhaustive domain-wide data collection.
- **`cleanup.py`**: Maintenance utility for cleaning up temporary files and build artifacts.
- **`benchmarks.py`**: Performance monitoring and evaluation tool.

## Getting Started

### 1. Environment Setup
It is recommended to use a dedicated virtual environment.

```bash
# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate
```

### 2. Installation
Install the system and its required dependencies in editable mode.

```bash
# Install with all features enabled
pip install -e ".[all]"
```

### 3. Initialize Browsers
Initialize the required browser binaries and configuration data.

```bash
# Download and install browsers
scrapling install
```

## Running the System

### Targeted Deep Scrape
Used for gathering specific, high-quality contextual data.
```bash
python deep_scrape_africa_ai.py
```

### Exhaustive Mega-Crawl
Used for discovering and aggregating data across multiple domains.
```bash
python exhaustive_scrape.py
```

### Clean Environment
Removes build artifacts and temporary files.
```bash
python cleanup.py
```

## Data Output Format

Results are aggregated into CSV files with the following structure:
- **url**: The source URL of the extracted page.
- **title**: The title of the page.
- **text**: The primary content or summary extracted.
- **contexts**: Key snippets and surrounding context found during extraction.

## Best Practices

- **Resource Management**: Use the cleanup utility regularly when performing large-scale crawls.
- **Rate Limiting**: Be aware of the scraping frequency to avoid triggering server-side protections.
- **Graceful Shutdown**: The system supports progress saving via the `Ctrl+C` interrupt.

## License

This system is provided for research and educational purposes.
