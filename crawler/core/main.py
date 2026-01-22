from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import requests
from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
import sys
import os
import time
import logging
import json


# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from logging_config import setup_logging

# Set up logging - change log_level to 'DEBUG' for more detailed output
logger = setup_logging(log_level='DEBUG', log_to_file=True, log_directory='logs')

# Cache robot parsers per domain
robot_parsers = {}

from utils import helper_functions as hf 


def can_fetch(url, user_agent='*'):
    """Check if we're allowed to crawl this URL according to robots.txt"""
    parsed = urlparse(url)
    domain = f"{parsed.scheme}://{parsed.netloc}"

    # Get or create parser for this domain
    if domain not in robot_parsers:
        rp = RobotFileParser()
        robots_url = urljoin(domain, '/robots.txt')
        rp.set_url(robots_url)
        try:
            logging.debug(f"Reading robots.txt for domain: {domain}")
            # Fetch robots.txt with timeout using requests
            response = requests.get(robots_url, timeout=2)
            if response.status_code == 200:
                rp.parse(response.text.splitlines())
                robot_parsers[domain] = rp
                logging.debug(f"Successfully loaded robots.txt for {domain}")
            else:
                logging.debug(f"robots.txt returned {response.status_code} for {domain}, assuming crawl allowed")
                robot_parsers[domain] = None
        except requests.exceptions.Timeout:
            logging.warning(f"Timeout reading robots.txt for {domain} (2s), assuming crawl allowed")
            robot_parsers[domain] = None
        except Exception as e:
            # If we can't read robots.txt, assume we can crawl
            logging.warning(f"Could not read robots.txt for {domain}: {e}")
            robot_parsers[domain] = None

    parser = robot_parsers[domain]
    if parser is None:
        return True

    can_crawl = parser.can_fetch(user_agent, url)
    if not can_crawl:
        logging.info(f"Robots.txt disallows crawling: {url}")
    return can_crawl




# Startup checks and initialization
logging.info("=== Web Crawler Starting ===")

# Check if required data files exist
data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'raw')
processed_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'processed')
to_crawl_file = os.path.join(data_dir, 'to_crawl.txt')
crawled_file = os.path.join(data_dir, 'crawled.txt')

if not os.path.exists(data_dir):
    logging.error(f"Data directory does not exist: {data_dir}")
    sys.exit(1)

if not os.path.exists(processed_dir):
    os.makedirs(processed_dir, exist_ok=True)

if not os.path.exists(to_crawl_file):
    logging.warning(f"To crawl file does not exist: {to_crawl_file}")
    logging.info("Creating empty to_crawl.txt file")
    with open(to_crawl_file, 'w') as f:
        pass

if not os.path.exists(crawled_file):
    logging.info("Creating empty crawled.txt file")
    with open(crawled_file, 'w') as f:
        pass

# Log initial queue status
try:
    with open(to_crawl_file, 'r', encoding='utf-8', errors='replace') as f:
        initial_queue_size = len([line for line in f if line.strip()])
    logging.info(f"Starting with {initial_queue_size} URLs in queue")
except Exception as e:
    logging.error(f"Could not read initial queue size: {e}")
    initial_queue_size = 0

if initial_queue_size == 0:
    logging.warning("No URLs in queue to start crawling!")

logging.info("Starting crawler main loop")

def save_page_json(url, soup, processed_dir):
    """Save page content as JSON"""
    page_data = {
        'url': url,
        'title': soup.title.string if soup.title and soup.title.string else '',
        'content': soup.get_text(separator=' ', strip=True)
    }

    # Simple filename from URL
    filename = f"page_{len(os.listdir(processed_dir)) + 1}.json"
    filepath = os.path.join(processed_dir, filename)

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(page_data, f, indent=2)
        logging.info(f"Saved page content to {filename}")
    except Exception as e:
        logging.error(f"Failed to save page data: {e}")

# TODO: Consider implementing proper priority queue instead of simple FIFO
# TODO: Add configurable crawl delays per domain
# TODO: Implement proper shutdown handling (e.g., SIGINT handling)

while True:
    try:
        url = hf.grab_next_url()

        if url is None:
            # Wait a bit before checking again if no URLs available
            logging.debug("No URLs available for crawling, waiting...")
            time.sleep(0.5)
            continue

        logging.info(f"Processing URL: {url}")

        # Skip invalid URLs
        parsed = urlparse(url)
        if parsed.scheme not in ['http', 'https']:
            logging.warning(f"Skipping invalid URL scheme: {url}")
            continue

        # Skip binary/non-HTML file extensions
        skip_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.zip', '.mp4', 
                          '.mp3', '.avi', '.exe', '.doc', '.docx', '.xls', '.xlsx', 
                          '.ppt', '.pptx', '.rar', '.tar', '.gz', '.ico', '.svg', '.webp']
        path_lower = parsed.path.lower()
        if any(path_lower.endswith(ext) for ext in skip_extensions):
            logging.debug(f"Skipping binary file: {url}")
            continue

        try:
            logging.debug(f"Making HTTP request to: {url}")
            # Use HEAD request first to check Content-Type
            try:
                head_response = requests.head(url, timeout=2, allow_redirects=True)
                content_type = head_response.headers.get('Content-Type', '').lower()
                
                # Skip if not HTML content
                if content_type and 'text/html' not in content_type:
                    logging.debug(f"Skipping non-HTML content ({content_type}): {url}")
                    continue
            except:
                # If HEAD fails, proceed with GET (some servers don't support HEAD)
                pass
            
            raw_html = requests.get(url, timeout=10)

            if raw_html.status_code != 200:
                logging.warning(f"HTTP {raw_html.status_code} for {url}")
                continue

            # Double-check content type after GET
            content_type = raw_html.headers.get('Content-Type', '').lower()
            if 'text/html' not in content_type:
                logging.debug(f"Skipping non-HTML response ({content_type}): {url}")
                continue

            logging.debug(f"Successfully fetched {url} ({len(raw_html.content)} bytes)")

            parsed_html = bs(raw_html.content, 'html.parser')

            # Save page content as JSON
            if hf.should_save(parsed_html.get_text(separator=' ', strip=True),processed_dir):
                save_page_json(url, parsed_html, processed_dir)

            # Extract links for further crawling
            links = []
            link_elements = parsed_html.find_all('a')
            logging.debug(f"Found {len(link_elements)} link elements")

            for link in link_elements:
                href = link.get('href')
                if href:
                    absolute_url = urljoin(url, href)
                    parsed = urlparse(absolute_url)
                    # Only add valid HTTP/HTTPS URLs that robots.txt allows
                    if parsed.scheme in ['http', 'https'] and can_fetch(absolute_url):
                        links.append(absolute_url)

            logging.info(f"Extracted {len(links)} valid links from {url}")
            hf.save_new_urls(links)

        except requests.exceptions.Timeout:
            logging.error(f"Timeout crawling {url}")
            continue
        except requests.exceptions.ConnectionError:
            logging.error(f"Connection error crawling {url}")
            continue
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error crawling {url}: {e}")
            continue
        except Exception as e:
            logging.error(f"Unexpected error crawling {url}: {e}")
            continue

    except KeyboardInterrupt:
        logging.info("Crawler stopped by user (Ctrl+C)")
        break
    except Exception as e:
        logging.error(f"Critical error in main loop: {e}")
        logging.info("Continuing crawler after error...")
        time.sleep(1)  # Brief pause before continuing
