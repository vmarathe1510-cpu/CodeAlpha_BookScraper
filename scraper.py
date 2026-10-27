"""
CodeAlpha Task 1 - Web Scraping
Scrapes book data (title, price, rating, stock, category, UPC, description)
from https://books.toscrape.com, a sandbox site built for scraping practice.

Usage:
    python src/scraper.py                 # scrape all 50 pages (~1000 books)
    python src/scraper.py --max-pages 3   # quick test run
"""
import argparse
import logging
import time
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://books.toscrape.com/catalogue/"
START_URL = urljoin(BASE_URL, "page-1.html")
RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = ROOT / "data" / "raw" / "books_raw.csv"
CLEAN_PATH = ROOT / "data" / "processed" / "books_clean.csv"

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("scraper")


def build_session() -> requests.Session:
    """HTTP session with a descriptive User-Agent and automatic retries."""
    session = requests.Session()
    session.headers.update({"User-Agent": "CodeAlpha-Internship-Scraper/1.0 (educational use)"})
    retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def get_soup(session: requests.Session, url: str) -> BeautifulSoup:
    resp = session.get(url, timeout=15)
    resp.raise_for_status()
    resp.encoding = "utf-8"  # avoids the 'Â£' encoding glitch on prices
    return BeautifulSoup(resp.text, "lxml")


def parse_listing(soup: BeautifulSoup) -> list[dict]:
    """Extract basic fields for every book card on a listing page."""
    books = []
    for card in soup.select("article.product_pod"):
        link = card.h3.a
        books.append({
            "title": link["title"],
            "url": urljoin(BASE_URL, link["href"]),
            "price_raw": card.select_one("p.price_color").get_text(strip=True),
            "rating_raw": card.select_one("p.star-rating")["class"][1],
        })
    return books


def parse_detail(soup: BeautifulSoup) -> dict:
    """Extract category, UPC, stock count and description from a book page."""
    crumbs = soup.select("ul.breadcrumb li")
    category = crumbs[2].get_text(strip=True) if len(crumbs) >= 3 else None
    table = {row.th.get_text(strip=True): row.td.get_text(strip=True)
             for row in soup.select("table.table-striped tr")}
    desc_tag = soup.select_one("#product_description ~ p")
    return {
        "category": category,
        "upc": table.get("UPC"),
        "num_reviews": table.get("Number of reviews"),
        "description": desc_tag.get_text(strip=True) if desc_tag else None,
        "stock_text": table.get("Availability"),
    }


def next_page_url(soup: BeautifulSoup, current_url: str):
    nxt = soup.select_one("li.next a")
    return urljoin(current_url, nxt["href"]) if nxt else None


def scrape(max_pages: int, delay: float) -> pd.DataFrame:
    session = build_session()
    url, page, records = START_URL, 1, []
    while url and page <= max_pages:
        log.info("Listing page %d: %s", page, url)
        soup = get_soup(session, url)
        for book in parse_listing(soup):
            try:
                detail = parse_detail(get_soup(session, book["url"]))
                records.append({**book, **detail})
            except requests.RequestException as exc:
                log.warning("Skipped %s (%s)", book["url"], exc)
            time.sleep(delay)  # be polite to the server
        url = next_page_url(soup, url)
        page += 1
    return pd.DataFrame(records)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Convert raw strings to analysis-ready types and drop duplicates."""
    out = df.copy()
    out["price_gbp"] = out["price_raw"].str.extract(r"(\d+\.?\d*)")[0].astype(float)
    out["rating"] = out["rating_raw"].map(RATING_MAP).astype("Int64")
    out["stock_count"] = out["stock_text"].str.extract(r"(\d+)")[0].astype("Int64")
    out["num_reviews"] = pd.to_numeric(out["num_reviews"], errors="coerce").astype("Int64")
    out["description_length"] = out["description"].fillna("").str.len()
    out = out.drop_duplicates(subset="upc").drop(
        columns=["price_raw", "rating_raw", "stock_text"])
    return out


def quality_report(df: pd.DataFrame) -> None:
    log.info("Rows: %d | Columns: %d", *df.shape)
    log.info("Missing values per column:\n%s", df.isna().sum().to_string())
    log.info("Price range: %.2f - %.2f GBP", df["price_gbp"].min(), df["price_gbp"].max())
    log.info("Categories: %d", df["category"].nunique())


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape books.toscrape.com")
    parser.add_argument("--max-pages", type=int, default=50)
    parser.add_argument("--delay", type=float, default=0.3, help="seconds between requests")
    args = parser.parse_args()

    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)

    raw = scrape(args.max_pages, args.delay)
    raw.to_csv(RAW_PATH, index=False)
    cleaned = clean(raw)
    cleaned.to_csv(CLEAN_PATH, index=False)
    quality_report(cleaned)
    log.info("Saved %s and %s", RAW_PATH, CLEAN_PATH)


if __name__ == "__main__":
    main()
