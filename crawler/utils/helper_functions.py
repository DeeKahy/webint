import os
import time
import logging
from urllib.parse import urlparse

# Define data directory path
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'raw')
TO_CRAWL_FILE = os.path.join(DATA_DIR, 'to_crawl.txt')
CRAWLED_FILE = os.path.join(DATA_DIR, 'crawled.txt')
DOMAIN_TIMING_FILE = os.path.join(DATA_DIR, 'domain_timing.txt')

def grab_next_url():
    # Load domain timing data
    domain_times = {}
    if os.path.exists(DOMAIN_TIMING_FILE):
        logging.debug("Loading domain timing data")
        with open(DOMAIN_TIMING_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    domain, timestamp = line.split('\t')
                    domain_times[domain] = float(timestamp)
        logging.debug(f"Loaded timing data for {len(domain_times)} domains")
    else:
        logging.debug("No domain timing file found, starting fresh")

    # Read all URLs to crawl
    if not os.path.exists(TO_CRAWL_FILE):
        logging.warning(f"To crawl file not found: {TO_CRAWL_FILE}")
        return None

    with open(TO_CRAWL_FILE, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]

    logging.debug(f"Found {len(urls)} URLs in queue")

    # Find first URL whose domain can be crawled (>1 second since last crawl)
    # TODO: Make crawl delay configurable per domain
    current_time = time.time()
    selected_url = None
    rate_limited_count = 0

    for url in urls:
        domain = urlparse(url).netloc
        last_crawl_time = domain_times.get(domain, 0)
        time_since_last = current_time - last_crawl_time

        if time_since_last > 1:
            selected_url = url
            logging.debug(f"Selected URL from domain {domain} (last crawled {time_since_last:.1f}s ago)")
            break
        else:
            rate_limited_count += 1
            if rate_limited_count <= 3:  # Only log first few to avoid spam
                logging.debug(f"Rate limiting {domain}: only {time_since_last:.1f}s since last crawl")

    if selected_url:
        # Remove selected URL from to_crawl
        urls.remove(selected_url)
        with open(TO_CRAWL_FILE, 'w') as f:
            for url in urls:
                f.write(url + '\n')

        logging.debug(f"Removed URL from queue, {len(urls)} remaining")

        # Update domain timing
        domain = urlparse(selected_url).netloc
        domain_times[domain] = current_time
        with open(DOMAIN_TIMING_FILE, 'w') as f:
            for d, t in domain_times.items():
                f.write(f"{d}\t{t}\n")

        # Append to crawled file
        with open(CRAWLED_FILE, 'a') as f:
            f.write(selected_url + "\n")

        return selected_url
    else:
        if rate_limited_count > 0:
            logging.debug(f"All {rate_limited_count} URLs rate-limited, waiting...")
        else:
            logging.info("No URLs available to crawl")
        return None

def save_new_urls(links):
    logging.debug(f"Processing {len(links)} potential new URLs")

    # Read existing URLs from both files
    # TODO: Consider using database instead of files for better performance
    to_crawl = set()
    if os.path.exists(TO_CRAWL_FILE):
        with open(TO_CRAWL_FILE, 'r') as f:
            to_crawl = set(line.strip() for line in f)

    crawled = set()
    if os.path.exists(CRAWLED_FILE):
        with open(CRAWLED_FILE, 'r') as f:
            crawled = set(line.strip() for line in f)

    logging.debug(f"Found {len(to_crawl)} URLs to crawl, {len(crawled)} already crawled")

    # Filter out duplicates
    new_urls = []
    duplicate_count = 0

    for link in links:
        link = link.strip()
        if link and link not in to_crawl and link not in crawled:
            new_urls.append(link)
            to_crawl.add(link)  # Add to set to prevent duplicates within this batch
        elif link:
            duplicate_count += 1

    # Append only new URLs to file
    if new_urls:
        with open(TO_CRAWL_FILE, 'a') as f:
            for url in new_urls:
                f.write(url + '\n')
        logging.info(f"Added {len(new_urls)} new URLs to queue")
        if duplicate_count > 0:
            logging.debug(f"Skipped {duplicate_count} duplicate URLs")
    else:
        logging.debug(f"No new URLs to add ({duplicate_count} were duplicates)")
