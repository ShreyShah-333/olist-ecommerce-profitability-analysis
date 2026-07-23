"""
03_profitability_proxy.py
Builds an order-level profitability proxy.

Olist's public dataset does not include Olist's own commission rate or
sellers' cost of goods, so true profit margin can't be computed exactly.
Instead, this script builds a transparent PROXY metric so we can still
compare relative profitability across categories/sellers/states:

    profitability_proxy = item_revenue
                           - freight_value
                           - estimated_commission
                           - estimated_return_processing_cost (for low review scores)

estimated_commission defaults to 15% of item price (a commonly cited Olist
marketplace commission rate) and is exposed as a module-level constant so
the assumption is explicit, not hidden.

Usage:
    python python/03_profitability_proxy.py
"""

import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost:5432/olist")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")

# Explicit, documented assumptions (adjust as needed):
ESTIMATED_COMMISSION_RATE = 0.15   # Olist's typical marketplace commission
LOW_REVIEW_THRESHOLD = 2           # review_score <= this is treated as a costly outcome
ESTIMATED_RETURN_COST_RATE = 0.10  # extra cost assumed for low-review orders


def get_engine():
    return create_engine(DATABASE_URL)


def load_data(engine):
    query = """
        SELECT
            oi.order_id, oi.product_id, oi.seller_id,
            oi.price, oi.freight_value,
            p.product_category_name,
            t.product_category_name_english,
            s.seller_state,
            c.customer_state,
            r.review_score
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        LEFT JOIN product_category_name_translation t
            ON p.product_category_name = t.product_category_name
        JOIN sellers s ON oi.seller_id = s.seller_id
        JOIN orders o ON oi.order_id = o.order_id
        JOIN customers c ON o.customer_id = c.customer_id
        LEFT JOIN order_reviews r ON oi.order_id = r.order_id
    """
    return pd.read_sql(query, engine)


def compute_profitability_proxy(df):
    df["estimated_commission"] = df["price"] * ESTIMATED_COMMISSION_RATE
    df["estimated_return_cost"] = 0.0
    low_review_mask = df["review_score"] <= LOW_REVIEW_THRESHOLD
    df.loc[low_review_mask, "estimated_return_cost"] = (
        df.loc[low_review_mask, "price"] * ESTIMATED_RETURN_COST_RATE
    )
    df["profitability_proxy"] = (
        df["price"]
        - df["freight_value"]
        - df["estimated_commission"]
        - df["estimated_return_cost"]
    )
    return df


def summarize(df):
    by_category = (
        df.groupby("product_category_name_english")["profitability_proxy"]
        .agg(["sum", "mean", "count"])
        .sort_values("sum", ascending=False)
    )
    by_seller_state = (
        df.groupby("seller_state")["profitability_proxy"]
        .agg(["sum", "mean", "count"])
        .sort_values("sum", ascending=False)
    )
    return by_category, by_seller_state


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    engine = get_engine()
    df = load_data(engine)
    df = compute_profitability_proxy(df)

    by_category, by_seller_state = summarize(df)

    df.to_csv(os.path.join(OUTPUT_DIR, "order_item_profitability.csv"), index=False)
    by_category.to_csv(os.path.join(OUTPUT_DIR, "profitability_by_category.csv"))
    by_seller_state.to_csv(os.path.join(OUTPUT_DIR, "profitability_by_seller_state.csv"))

    print("Top 5 most profitable categories (by total proxy profit):")
    print(by_category.head(5))
    print(f"\nOutputs saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
