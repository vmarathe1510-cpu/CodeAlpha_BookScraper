"""
Reads data/processed/books_clean.csv, works out simple findings,
and writes them into README.md under '## Key findings'.

Usage:  python src/write_findings.py
"""
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
df = pd.read_csv(ROOT / "data" / "processed" / "books_clean.csv")
readme_path = ROOT / "README.md"

n_books, n_cats = len(df), df["category"].nunique()

# Only compare categories with at least 3 books so one odd book does not mislead
stats = df.groupby("category")["price_gbp"].agg(["mean", "count"])
stats = stats[stats["count"] >= 3].sort_values("mean")
priciest, cheapest = stats.index[-1], stats.index[0]

corr = df["price_gbp"].corr(df["rating"].astype(float))
if abs(corr) < 0.1:
    corr_text = "almost no relationship"
elif corr > 0:
    corr_text = "a weak positive relationship" if corr < 0.3 else "a clear positive relationship"
else:
    corr_text = "a weak negative relationship" if corr > -0.3 else "a clear negative relationship"

high_share = (df["rating"] >= 4).mean() * 100
rating_text = ("skews positive" if high_share >= 60 else
               "skews negative" if high_share <= 40 else "is fairly balanced")
biggest_cat = df["category"].value_counts()
low_stock = (df["stock_count"] <= 5).sum()

findings = f"""## Key findings
Based on {n_books} books across {n_cats} categories (see `outputs/avg_price_by_category.png`):

1. **Most expensive category:** {priciest} has the highest average price (£{stats.loc[priciest, 'mean']:.2f}), while {cheapest} is the cheapest (£{stats.loc[cheapest, 'mean']:.2f}).
2. **Price vs rating:** the correlation is {corr:.2f}, which shows {corr_text}. A higher price does not guarantee a better rating.
3. **Ratings:** {high_share:.0f}% of books have 4 or 5 stars, so the catalogue {rating_text}.
4. **Assortment:** {biggest_cat.index[0]} is the largest category ({biggest_cat.iloc[0]} books). {low_stock} books have 5 or fewer copies in stock, which may need restocking.
"""

text = readme_path.read_text(encoding="utf-8")
new_text, count = re.subn(r"## Key findings.*?(?=\n## Limitations)", findings, text, flags=re.S)
if count == 0:
    raise SystemExit("Could not find '## Key findings' and '## Limitations' in README.md")
readme_path.write_text(new_text, encoding="utf-8")
print(findings)
print("README.md updated.")
