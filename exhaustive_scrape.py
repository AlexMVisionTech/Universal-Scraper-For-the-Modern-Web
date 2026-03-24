import os
import sys
import csv
import time

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from scrapling.fetchers.search import SearchFetcher
from scrapling.fetchers.stealth_chrome import StealthyFetcher
from scrapling.fetchers.requests import Fetcher
from scrapling.core.utils import log

# Change log level if needed
import logging
logging.getLogger("scrapling").setLevel(logging.INFO)

def save_partial_results(results, filename):
    if not results:
        return
    file_exists = os.path.isfile(filename)
    fieldnames = set()
    for res in results:
        fieldnames.update(res.keys())
    fieldnames = sorted(list(fieldnames))
    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        for res in results:
            row = res.copy()
            if 'contexts' in row and isinstance(row['contexts'], list):
                row['contexts'] = " | ".join(row['contexts'])
            writer.writerow(row)

def main():
    print("Starting EXHAUSTIVE deep scrape for 'Africa AI Village'...", flush=True)
    
    queries = [
        '"Africa AI Village" "India AI Impact Summit 2026"',
        '"Africa AI Village" India summit 2026',
        '"Africa AI Village" India Impact AI',
        '"Africa AI Village" New Delhi summit 2026',
        '"Africa AI Village" Global Pavilion India 2026',
        'site:linkedin.com "Africa AI Village" "India AI Impact Summit"',
        'site:twitter.com "Africa AI Village" "India AI Impact Summit"',
        '#AfricaAIVillage "India AI Impact Summit"',
        '"Africa AI Village" showcasing at India AI Impact Summit',
        'African startups at India AI Impact Summit 2026 "Africa AI Village"'
    ]
    
    print(f"Total mega-queries to execute: {len(queries)}", flush=True)
    output_filename = os.path.join(os.path.dirname(__file__), "africa_ai_summit_2026_specific.csv")
    
    for idx, query in enumerate(queries, 1):
        print(f"\n[{idx}/{len(queries)}] Processing query: {query}", flush=True)
        try:
            # We use crawl_and_extract for extreme scraping
            # This follows intra-site links (max_depth=1)
            # which could yield WAY more data than search_and_extract.
            # max_seeds=10 means it finds up to 10 top results from search engine,
            # then crawls each of those domains up to max_pages_per_domain.
            results = SearchFetcher.crawl_and_extract(
                queries=[query],
                max_seeds=5,
                max_depth=1, 
                max_pages_per_domain=5,
                domain_blacklist=['luma.com', 'eventbrite.com', 'linkedin.com/legal', 'linkedin.com/uas'],
                timeout=10,
                retries=1
            )
            
            if results:
                save_partial_results(results, output_filename)
                
        except Exception as e:
            print(f"[{idx}/{len(queries)}] Error processing {query}: {e}", flush=True)
            
        # polite delay between queries to avoid DuckDuckGo bans
        time.sleep(3)
            
    print(f"\nExhaustive scraping completed! Massive dataset appended to {output_filename}", flush=True)

if __name__ == "__main__":
    main()
