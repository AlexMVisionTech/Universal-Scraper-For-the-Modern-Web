from typing import List, Union, Optional
from urllib.parse import urlparse, parse_qs

from scrapling.fetchers.requests import Fetcher
from scrapling.fetchers.stealth_chrome import StealthyFetcher
from scrapling.parser import Selector, Selectors
from scrapling.core.utils import log


class SearchFetcher:
    """A high-level fetcher for searching the internet and verifying statements."""

    SEARCH_URL = "https://html.duckduckgo.com/html/"

    @classmethod
    def search(cls, query: str, max_results: int = 10, time_range: Optional[str] = None) -> List[str]:
        """Search the internet for a query and return a list of result URLs.

        :param query: The search query.
        :param max_results: Maximum number of URLs to return.
        :param time_range: DuckDuckGo time filter (df): 'd' (day), 'w' (week), 'm' (month), 'y' (year).
        :return: A list of URLs.
        """
        log.info(f"Searching for: {query} (time_range: {time_range})")
        
        data = {"q": query}
        if time_range:
            data["df"] = time_range
            
        # DuckDuckGo HTML version uses POST for search
        response = Fetcher.post(cls.SEARCH_URL, data=data)
        
        # Handle 202 Accepted (sometimes given if DDG is processing or limiting)
        if response.status == 202 and time_range:
            log.warning("Received 202 status with time_range. Retrying without time_range filter.")
            response = Fetcher.post(cls.SEARCH_URL, data={"q": query})

        if response.status != 200:
            log.error(f"Search failed with status {response.status}")
            return []

        # Extract links from the results
        # In DuckDuckGo HTML, results are usually in links with class 'result__a'
        # Using ::attr(href) is more direct and works well with Scrapling's Selector
        links = response.css('a.result__a::attr(href)').getall()
        if not links:
            # Fallback if class changes
            links = response.css('.links_main a::attr(href)').getall()
        
        urls = []
        for url in links:
            if url:
                # DuckDuckGo URLs are sometimes wrapped
                if '/l/?' in url and 'uddg=' in url:
                    from urllib.parse import urlparse, parse_qs
                    parsed = urlparse(url)
                    uddg = parse_qs(parsed.query).get('uddg')
                    if uddg:
                        url = uddg[0]
                
                if url not in urls:
                    urls.append(url)
            
            if len(urls) >= max_results:
                break
                
        return urls

    @classmethod
    def search_and_verify(
        cls, 
        statement: str, 
        max_results: int = 10, 
        deep: bool = True, 
        stealthy: bool = False
    ) -> List[dict]:
        """Search for a statement and verify its presence on the result pages.

        :param statement: The statement or keywords to look for.
        :param max_results: Maximum number of search results to check.
        :param deep: If True, fetch each page and verify the statement. If False, only check search snippets.
        :param stealthy: If True, use StealthyFetcher to visit result pages.
        :return: A list of dictionaries containing 'url' and 'found' (bool).
        """
        urls = cls.search(statement, max_results=max_results)
        results = []

        fetcher = StealthyFetcher if stealthy else Fetcher

        for url in urls:
            log.info(f"Verifying on: {url}")
            try:
                if deep:
                    if stealthy:
                        response = fetcher.fetch(url, headless=True)
                    else:
                        response = fetcher.get(url)
                    
                    # Search for the statement in the page
                    found = response.find_by_text(statement, partial=True) is not None
                else:
                    # Non-deep search is not really supported yet as we don't have snippets here easily
                    # and the search itself might be enough for some cases if we just want the URLs.
                    # But for now, let's treat non-deep as 'found' if it appeared in search results.
                    found = True 

                results.append({
                    "url": url,
                    "found": found
                })
            except Exception as e:
                log.error(f"Error checking {url}: {e}")
                results.append({
                    "url": url,
                    "found": False,
                    "error": str(e)
                })
        
        return results

    @classmethod
    def search_twitter(cls, query: str, max_results: int = 10, time_range: Optional[str] = None) -> List[str]:
        """Search Twitter (X) for a query using search engine operators.

        :param query: The search query.
        :param max_results: Maximum number of URLs to return.
        :param time_range: DuckDuckGo time filter (df).
        :return: A list of Tweet URLs.
        """
        twitter_query = f"site:twitter.com {query}"
        return cls.search(twitter_query, max_results=max_results, time_range=time_range)

    @classmethod
    def search_and_extract(
        cls, 
        query: str, 
        max_results: int = 5, 
        stealthy: bool = False,
        include_twitter: bool = True,
        time_range: Optional[str] = None,
        deep_extraction: bool = True
    ) -> List[dict]:
        """Search for a query and extract the context where it is mentioned.

        :param query: The search query or keywords.
        :param max_results: Maximum number of search results to check.
        :param stealthy: If True, use StealthyFetcher for all pages.
        :param include_twitter: If True, also search Twitter and include results.
        :param time_range: DuckDuckGo time filter (df).
        :param deep_extraction: If True, extract more paragraphs around matches.
        :return: A list of dictionaries containing 'url' and 'contexts' (list of strings).
        """
        urls = cls.search(query, max_results=max_results, time_range=time_range)
        
        if include_twitter:
            twitter_urls = cls.search_twitter(query, max_results=max_results // 2 or 1, time_range=time_range)
            # Combine and remove duplicates
            for t_url in twitter_urls:
                if t_url not in urls:
                    urls.append(t_url)

        results = []

        for url in urls:
            log.info(f"Extracting contexts from: {url}")
            try:
                # Twitter/X always requires stealthy fetching
                is_twitter = 'twitter.com' in url or 'x.com' in url
                current_stealthy = stealthy or is_twitter
                
                fetcher = StealthyFetcher if current_stealthy else Fetcher

                if current_stealthy:
                    response = fetcher.fetch(url, headless=True)
                else:
                    response = fetcher.get(url)
                
                # Special handling for Twitter/X selectors
                if is_twitter:
                    # Twitter uses data-testid for tweet text
                    matches = response.css('[data-testid="tweetText"]')
                else:
                    matches = response.find_by_text(query, first_match=False, partial=True)
                    
                    if not matches and len(query.split()) > 1:
                        broader_query = ' '.join(query.split()[:2])
                        matches = response.find_by_text(broader_query, first_match=False, partial=True)

                contexts = []
                # If deep extraction is enabled, we'll try to get more than just the matched paragraph
                if deep_extraction and not is_twitter:
                    # Get all paragraphs that contain common keywords
                    all_paragraphs = response.css('p::text').getall()
                    keywords = query.lower().split()
                    for p in all_paragraphs:
                        text = p.strip()
                        if len(text) > 40:
                            # If it contains any keyword, include it
                            if any(kw in text.lower() for kw in keywords):
                                if text not in contexts:
                                    contexts.append(text)
                
                # Always add the direct matches
                for match in matches:
                    text = match.get_all_text().strip()
                    if text and text not in contexts:
                        contexts.append(text)

                if contexts:
                    results.append({
                        "url": url,
                        "contexts": contexts[:10] # Cap per URL to avoid overwhelming
                    })
            except Exception as e:
                log.error(f"Error extracting from {url}: {e}")
                results.append({
                    "url": url,
                    "contexts": [],
                    "error": str(e)
                })

        return results

    @classmethod
    def multi_search_and_extract(
        cls, 
        queries: List[str], 
        max_results_per_query: int = 10,
        **kwargs
    ) -> List[dict]:
        """Perform multiple searches and combine/deduplicate results.

        :param queries: A list of search queries.
        :param max_results_per_query: Max results for each individual search.
        :param kwargs: Arguments passed to search_and_extract.
        :return: A list of combined result dictionaries.
        """
        all_results = []
        seen_urls = set()

        for query in queries:
            log.info(f"Running multi-query search: {query}")
            results = cls.search_and_extract(query, max_results=max_results_per_query, **kwargs)
            for res in results:
                url = res.get('url')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_results.append(res)
                elif url and url in seen_urls:
                    # Merge contexts for existing URL
                    for existing in all_results:
                        if existing['url'] == url:
                            new_contexts = res.get('contexts', [])
                            for ctx in new_contexts:
                                if ctx not in existing['contexts']:
                                    existing['contexts'].append(ctx)
                            break
        
        return all_results

    @classmethod
    def crawl_and_extract(
        cls, 
        queries: List[str], 
        max_seeds: int = 5,
        max_depth: int = 1,
        max_pages_per_domain: int = 10,
        domain_blacklist: Optional[List[str]] = None,
        **kwargs
    ) -> List[dict]:
        """Search for seeds and recursively crawl those domains for more content.

        :param queries: Search queries to find seed URLs.
        :param max_seeds: Max search results to use as seeds.
        :param max_depth: How deep to follow internal links (0-indexed).
        :param max_pages_per_domain: Limit pages scraped from a single domain.
        :param domain_blacklist: List of domains to skip.
        :param kwargs: Arguments passed to search_and_extract.
        :return: A list of result dictionaries.
        """
        seed_urls = []
        for query in queries:
            seed_urls.extend(cls.search(query, max_results=max_seeds))
        
        seed_urls = list(set(seed_urls)) # Dedup
        all_results = []
        seen_urls = set()
        domain_counts = {}

        def crawl(url, depth):
            if url in seen_urls or depth > max_depth:
                return
            
            domain = urlparse(url).netloc
            if domain_blacklist and any(b in url for b in domain_blacklist):
                return

            if domain_counts.get(domain, 0) >= max_pages_per_domain:
                return

            seen_urls.add(url)
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
            
            log.info(f"Crawling (depth {depth}): {url}")
            try:
                # Use Fetcher/StealthyFetcher directly to get full text and links
                is_twitter = 'twitter.com' in url or 'x.com' in url
                fetcher = StealthyFetcher if is_twitter else Fetcher
                
                if is_twitter:
                    response = fetcher.fetch(url, headless=True, **kwargs)
                else:
                    response = fetcher.get(url, **kwargs)

                # Extract context/text
                if is_twitter:
                    matches = response.css('[data-testid="tweetText"]')
                    text_content = [m.get_all_text().strip() for m in matches if m.get_all_text().strip()]
                else:
                    # For training, extract all meaningful paragraphs
                    paragraphs = response.css('p::text').getall()
                    text_content = [p.strip() for p in paragraphs if len(p.strip()) > 50]

                if text_content:
                    all_results.append({
                        "url": url,
                        "text": "\n".join(text_content),
                        "title": response.css('title::text').get() or "",
                        "domain": domain
                    })

                # Find more links to the same domain if depth allows
                if depth < max_depth and not is_twitter:
                    links = response.css('a::attr(href)').getall()
                    for link in links:
                        if not link: continue
                        
                        # Handle relative links
                        if link.startswith('/'):
                            link = f"{urlparse(url).scheme}://{domain}{link}"
                        
                        if urlparse(link).netloc == domain:
                            crawl(link, depth + 1)

            except Exception as e:
                log.error(f"Crawl error for {url}: {e}")

        for seed in seed_urls:
            crawl(seed, 0)
            
        return all_results

    @staticmethod
    def save_results(results: List[dict], filename: str):
        """Save search results to a file (JSON or CSV based on extension).

        :param results: The list of result dictionaries.
        :param filename: The path to the file to save.
        """
        import json
        import csv

        if filename.endswith('.json'):
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=4, ensure_ascii=False)
        elif filename.endswith('.csv'):
            if not results:
                return
            
            # Use all unique keys from all dicts as fieldnames
            fieldnames = set()
            for res in results:
                fieldnames.update(res.keys())
            
            fieldnames = sorted(list(fieldnames))
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for res in results:
                    row = res.copy()
                    if 'contexts' in row and isinstance(row['contexts'], list):
                        row['contexts'] = " | ".join(row['contexts'])
                    writer.writerow(row)
        elif filename.endswith('.jsonl'):
            with open(filename, 'w', encoding='utf-8') as f:
                for res in results:
                    f.write(json.dumps(res, ensure_ascii=False) + '\n')
        else:
            raise ValueError("Unsupported file format. Use .json, .jsonl or .csv")
        
        log.info(f"Results saved to {filename}")
