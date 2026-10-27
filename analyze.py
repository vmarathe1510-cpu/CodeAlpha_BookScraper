"""Quick analysis of the scraped dataset: proves the data is analysis-ready."""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
df = pd.read_csv(ROOT / "data" / "processed" / "books_clean.csv")
(ROOT / "outputs").mkdir(exist_ok=True)

top = df.groupby("category")["price_gbp"].mean().sort_values(ascending=False).head(10)
ax = top.sort_values().plot.barh(figsize=(8, 5), color="#2a6f97")
ax.set_title("Top 10 categories by average book price (GBP)")
ax.set_xlabel("Average price (GBP)")
plt.tight_layout()
plt.savefig(ROOT / "outputs" / "avg_price_by_category.png", dpi=150)

print(df.groupby("rating")["price_gbp"].agg(["count", "mean"]).round(2))
print("Price/rating correlation:", round(df["price_gbp"].corr(df["rating"]), 3))
