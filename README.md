# CodeAlpha_BookScraper

**CodeAlpha Data Analytics Internship - Task 1: Web Scraping**

## Problem statement
An online retailer wants a structured dataset of competitor book listings to support pricing and assortment analysis. This project builds a reproducible scraper that turns public HTML pages into a clean, analysis-ready CSV.

## What it collects
Title, category, price (GBP), star rating, stock count, UPC, number of reviews, description and product URL, for ~1,000 books across 50 listing pages.

## Tech stack
Python, Requests (with retry logic), BeautifulSoup + lxml, pandas, Matplotlib.

## Project structure
```
data/raw/        books_raw.csv        # exactly as scraped
data/processed/  books_clean.csv      # typed, de-duplicated
src/scraper.py                        # scrape + clean + data-quality report
src/analyze.py                        # sample insight chart
outputs/                              # figures
```

## How to run
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python src/scraper.py --max-pages 3     # quick test
python src/scraper.py                   # full run
python src/analyze.py
```

## Design decisions
- **Ethical scraping:** sandbox site built for practice, descriptive User-Agent, delay between requests, retries with backoff.
- **Two data layers:** raw CSV is never modified; cleaning happens in code, so results are reproducible.
- **Cleaning:** price strings to floats, rating words to integers, stock text to counts, duplicates removed by UPC.
- **Data-quality report** printed after every run (rows, missing values, price range, category count).

## Key findings
Based on 1000 books across 50 categories (see `outputs/avg_price_by_category.png`):

1. **Most expensive category:** Politics has the highest average price (£53.61), while Food and Drink is the cheapest (£31.41).
2. **Price vs rating:** the correlation is 0.03, which shows almost no relationship. A higher price does not guarantee a better rating.
3. **Ratings:** 38% of books have 4 or 5 stars, so the catalogue skews negative.
4. **Assortment:** Default is the largest category (152 books). 420 books have 5 or fewer copies in stock, which may need restocking.

## Limitations and next steps
- The site is static; JavaScript-heavy sites would need Selenium or Playwright.
- Next step: feed this dataset into the EDA project (Task 2).

## Author
Your Name | LinkedIn | GitHub
