import os
import sys

# Ensure Scrapling is in the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from scrapling.fetchers.search import SearchFetcher
from scrapling.core.utils import log
import csv

def save_partial_results(results, filename):
    if not results:
        return
    
    file_exists = os.path.isfile(filename)
    
    # Use all unique keys from all dicts as fieldnames
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
    print("Starting deep scrape for Africa AI Village reactions...", flush=True)
    
    all_queries = [
        # Reduced queries to prevent locking up for hours
        "Africa AI Village India reactions",
        "Africa AI Village India review",
        "Africa AI Village India impact",
        "#AfricaAIVillage India",
        "site:linkedin.com \"Africa AI Village\" India",
        "site:reddit.com \"Africa AI Village\"",
    ]
    
    print(f"Total queries to execute: {len(all_queries)}", flush=True)
    output_filename = os.path.join(os.path.dirname(__file__), "africa_ai_deep_reactions.csv")
    
    for idx, query in enumerate(all_queries, 1):
        print(f"[{idx}/{len(all_queries)}] Processing query: {query}", flush=True)
        try:
            # We use search_and_extract directly for better control
            results = SearchFetcher.search_and_extract(
                query=query,
                max_results=5,          # Less results per query to speed up and avoid hanging
                stealthy=True,          
                include_twitter=True,   
                deep_extraction=True    
            )
            
            print(f"[{idx}/{len(all_queries)}] Found {len(results)} URLs. Saving partial results...", flush=True)
            save_partial_results(results, output_filename)
            
        except Exception as e:
            print(f"Error processing {query}: {e}", flush=True)
            
    print(f"Finished scraping. Data appended to {output_filename}", flush=True)

if __name__ == "__main__":
    main()
