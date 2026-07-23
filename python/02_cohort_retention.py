"""
02_cohort_retention.py
Monthly acquisition cohort analysis for repeat-purchase / retention.

Groups customers (by customer_unique_id, since customer_id is generated
per-order in this dataset) into cohorts based on the month of their first
order, then tracks what share of each cohort placed another order in
subsequent months.

Usage:
    python python/02_cohort_retention.py
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


def load_customer_orders(engine):
    query = """
        SELECT c.customer_unique_id, o.order_id, o.order_purchase_timestamp
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.order_status NOT IN ('canceled', 'unavailable')
    """
    df = pd.read_sql(query, engine, parse_dates=["order_purchase_timestamp"])
    return df


def build_cohorts(df):
    df["order_month"] = df["order_purchase_timestamp"].dt.to_period("M")
    first_purchase = df.groupby("customer_unique_id")["order_month"].min().rename("cohort_month")
    df = df.join(first_purchase, on="customer_unique_id")
    df["cohort_index"] = (
        (df["order_month"] - df["cohort_month"]).apply(lambda x: x.n)
    )
    return df


def retention_table(df):
    cohort_data = (
        df.groupby(["cohort_month", "cohort_index"])["customer_unique_id"]
        .nunique()
        .reset_index()
    )
    cohort_pivot = cohort_data.pivot(index="cohort_month", columns="cohort_index", values="customer_unique_id")
    cohort_size = cohort_pivot.iloc[:, 0]
    retention = cohort_pivot.divide(cohort_size, axis=0)
    return retention


def plot_retention_heatmap(retention):
    plt.figure(figsize=(12, 8))
    sns.heatmap(retention, annot=True, fmt=".0%", cmap="Blues")
    plt.title("Monthly Cohort Retention Rate")
    plt.xlabel("Months Since First Purchase")
    plt.ylabel("Acquisition Cohort")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "cohort_retention_heatmap.png"))
    plt.close()


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    engine = get_engine()
    df = load_customer_orders(engine)
    df = build_cohorts(df)
    retention = retention_table(df)

    overall_repeat_rate = (
        df.groupby("customer_unique_id")["order_id"].nunique().gt(1).mean()
    )
    print(f"Overall repeat-purchase rate: {overall_repeat_rate:.2%}")

    plot_retention_heatmap(retention)
    retention.to_csv(os.path.join(OUTPUT_DIR, "cohort_retention_table.csv"))
    print(f"Retention table and heatmap saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
