"""
01_eda.py
Exploratory Data Analysis for the Olist e-commerce dataset.

Connects to the Postgres database (populated via sql/01_schema.sql and
sql/02_load_data.sql) and produces summary statistics and charts covering:
  - Order volume over time
  - Product category mix
  - Delivery time distribution (estimated vs. actual)
  - Review score distribution

Usage:
    python python/01_eda.py

Requires a .env file (not committed) with:
    DATABASE_URL=postgresql://user:password@localhost:5432/olist
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost:5432/olist")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")


def get_engine():
    return create_engine(DATABASE_URL)


def load_core_tables(engine):
    orders = pd.read_sql("SELECT * FROM orders", engine, parse_dates=[
        "order_purchase_timestamp", "order_approved_at",
        "order_delivered_carrier_date", "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ])
    order_items = pd.read_sql("SELECT * FROM order_items", engine)
    products = pd.read_sql("SELECT * FROM products", engine)
    category_translation = pd.read_sql("SELECT * FROM product_category_name_translation", engine)
    reviews = pd.read_sql("SELECT * FROM order_reviews", engine)
    return orders, order_items, products, category_translation, reviews


def plot_order_volume_over_time(orders):
    monthly = (
        orders.set_index("order_purchase_timestamp")
        .resample("MS")
        .size()
    )
    plt.figure(figsize=(10, 5))
    monthly.plot(kind="line", marker="o")
    plt.title("Monthly Order Volume")
    plt.xlabel("Month")
    plt.ylabel("Number of Orders")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "order_volume_over_time.png"))
    plt.close()


def plot_category_mix(order_items, products, category_translation):
    merged = (
        order_items.merge(products, on="product_id", how="left")
        .merge(category_translation, on="product_category_name", how="left")
    )
    top_categories = (
        merged["product_category_name_english"]
        .value_counts()
        .head(15)
    )
    plt.figure(figsize=(10, 6))
    sns.barplot(x=top_categories.values, y=top_categories.index)
    plt.title("Top 15 Product Categories by Order Item Volume")
    plt.xlabel("Number of Order Items")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "top_categories.png"))
    plt.close()


def plot_delivery_time_distribution(orders):
    delivered = orders.dropna(subset=["order_delivered_customer_date"]).copy()
    delivered["actual_delivery_days"] = (
        delivered["order_delivered_customer_date"] - delivered["order_purchase_timestamp"]
    ).dt.days
    delivered["estimated_delivery_days"] = (
        delivered["order_estimated_delivery_date"] - delivered["order_purchase_timestamp"]
    ).dt.days

    plt.figure(figsize=(10, 5))
    sns.histplot(delivered["actual_delivery_days"], bins=40, label="Actual", kde=True)
    sns.histplot(delivered["estimated_delivery_days"], bins=40, label="Estimated", kde=True, color="orange")
    plt.legend()
    plt.title("Actual vs. Estimated Delivery Time (days)")
    plt.xlabel("Days from Purchase to Delivery")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "delivery_time_distribution.png"))
    plt.close()

    on_time_rate = (delivered["order_delivered_customer_date"] <= delivered["order_estimated_delivery_date"]).mean()
    print(f"On-time delivery rate: {on_time_rate:.2%}")


def plot_review_score_distribution(reviews):
    plt.figure(figsize=(8, 5))
    sns.countplot(x="review_score", data=reviews, order=[1, 2, 3, 4, 5])
    plt.title("Review Score Distribution")
    plt.xlabel("Review Score")
    plt.ylabel("Number of Reviews")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "review_score_distribution.png"))
    plt.close()


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    engine = get_engine()
    orders, order_items, products, category_translation, reviews = load_core_tables(engine)

    print(f"Loaded {len(orders):,} orders, {len(order_items):,} order items, "
          f"{len(products):,} products, {len(reviews):,} reviews.")

    plot_order_volume_over_time(orders)
    plot_category_mix(order_items, products, category_translation)
    plot_delivery_time_distribution(orders)
    plot_review_score_distribution(reviews)

    print(f"Charts saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
