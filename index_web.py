import time
from urllib.parse import urldefrag, urljoin, urlparse
from bs4 import BeautifulSoup
import requests
import trafilatura
import urllib

from marqo_helper import index_content_to_marqo
from util import print_error

visited_urls = set()  # To avoid duplicate visits


def get_robots_parser(base_url):
    """Fetch and parse the site's robots.txt"""
    robots_url = urljoin(base_url, "/robots.txt")
    rp = urllib.robotparser.RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
        return rp
    except Exception as e:
        print(f"Error fetching robots.txt from {robots_url}: {e}")
        return None


def is_allowed_by_robots(url, rp):
    """Check if the URL is allowed to be crawled."""
    return rp.can_fetch("*", url) if rp else True  # Assume allowed if robots.txt fails


def process_page(base_url, url):
    """Extracts all internal links from a given URL."""
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Googlebot"})
        if response.status_code >= 300:  # Check for redirects or errors
            raise Exception(f"Received status code {response.status_code} for {url}")

        soup = BeautifulSoup(response.text, "html.parser")
        links = set()

        for a_tag in soup.find_all("a", href=True):
            clean_link = normalize_url(
                base_url, a_tag["href"]
            )  # Normalize & remove fragments
            if (
                urlparse(clean_link).netloc == urlparse(base_url).netloc
            ):  # Ensure it's an internal link
                links.add(clean_link)

        main_content: str = trafilatura.extract(response.text)
        title_tag = soup.find("title")
        title: str = title_tag.string if title_tag else main_content.splitlines()[0]
        title = title.strip().splitlines()[0].strip()

        return title, main_content, links
    except Exception as e:
        print_error(f"Error fetching {url}: {e}")
        return "", "", set()


def normalize_url(base_url, href):
    # Convert relative URL to absolute
    absolute_url = urljoin(base_url, href)

    # Remove fragments
    clean_url, _ = urldefrag(absolute_url)

    # Parse the URL to remove query parameters and normalize
    # parsed_url = urlparse(clean_url)
    # clean_url = parsed_url._replace(query="", params="").geturl()

    # Remove trailing slash if present
    if clean_url.endswith("/"):
        clean_url = clean_url[:-1]

    return clean_url


def crawl_website(start_url, max_pages=50):
    """Recursively crawls a website while respecting robots.txt."""
    rp = get_robots_parser(start_url)  # Get robots.txt rules
    to_visit = {start_url}

    while to_visit and len(visited_urls) < max_pages:
        url = to_visit.pop()
        if url in visited_urls or not is_allowed_by_robots(url, rp):
            continue

        print(f"\n===> Crawling: {url}")
        visited_urls.add(url)

        title, page_content, new_links = process_page(start_url, url)
        to_visit.update(new_links - visited_urls)  # Avoid revisiting links

        if title and page_content:
            index_content_to_marqo(title, page_content, "web", url)

        time.sleep(2)  # Be polite, don't overload the server

    print(f"\nCrawled {len(visited_urls)} pages.")


crawl_website("https://doodoodaily.com", 1000)
