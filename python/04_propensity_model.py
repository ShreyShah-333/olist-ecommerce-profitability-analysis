"""
04_propensity_model.py
Repeat-purchase propensity model.

Trains a classifier to estimate the likelihood that a customer will place
a second order, using features available at (or shortly after) the time of
their first order: first-order value, freight cost, product category,
delivery speed, and review score. This is the "AI" layer discussed in the
project plan -- it sits on top of the SQL/pandas profitability analysis and
does not replace it; all financial figures in 03_profitability_proxy.py are
computed independently in transparent SQL/pandas.

Usage:
    python python/04_propensity_model.py
"""

import os
import pandas as pd
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, roc_auc_score
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost:5432/olist")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")


def get_engine():
    return create_engine(DATABASE_URL)


def build_feature_table(engine):
    query = """
        SELECT
            c.customer_unique_id,
            o.order_id,
            o.order_purchase_timestamp,
            o.order_delivered_customer_date,
            o.order_estimated_delivery_date,
            oi.price,
            oi.freight_value,
            t.product_category_name_english,
            r.review_score
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        LEFT JOIN product_category_name_translation t
            ON p.product_category_name = t.product_category_name
        LEFT JOIN order_reviews r ON o.order_id = r.order_id
        WHERE o.order_status NOT IN ('canceled', 'unavailable')
    """
    df = pd.read_sql(query, engine, parse_dates=[
        "order_purchase_timestamp", "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ])

    # Collapse to one row per customer's FIRST order only
    first_orders = (
        df.sort_values("order_purchase_timestamp")
        .groupby("customer_unique_id")
        .first()
        .reset_index()
    )

    # Label: did this customer place more than one order overall?
    order_counts = df.groupby("customer_unique_id")["order_id"].nunique()
    first_orders["repeat_customer"] = (
        first_orders["customer_unique_id"].map(order_counts) > 1
    ).astype(int)

    first_orders["delivery_delay_days"] = (
        first_orders["order_delivered_customer_date"]
        - first_orders["order_estimated_delivery_date"]
    ).dt.days

    return first_orders


def train_model(df):
    feature_cols = [
        "price", "freight_value", "product_category_name_english",
        "review_score", "delivery_delay_days"
    ]
    df = df.dropna(subset=feature_cols)

    X = df[feature_cols]
    y = df["repeat_customer"]

    numeric_features = ["price", "freight_value", "review_score", "delivery_delay_days"]
    categorical_features = ["product_category_name_english"]

    preprocessor = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
    ], remainder="passthrough")

    model = Pipeline([
        ("preprocess", preprocessor),
        ("classifier", RandomForestClassifier(
            n_estimators=200, max_depth=8, class_weight="balanced", random_state=42
        )),
    ])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    print(classification_report(y_test, y_pred))
    print(f"ROC AUC: {roc_auc_score(y_test, y_proba):.3f}")

    return model, X_test, y_test, y_proba


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    engine = get_engine()
    df = build_feature_table(engine)

    print(f"Built feature table for {len(df):,} first-time customers.")
    print(f"Baseline repeat-purchase rate: {df['repeat_customer'].mean():.2%}")

    model, X_test, y_test, y_proba = train_model(df)

    results = X_test.copy()
    results["actual_repeat_customer"] = y_test.values
    results["predicted_repeat_probability"] = y_proba
    results.to_csv(os.path.join(OUTPUT_DIR, "propensity_predictions.csv"), index=False)

    print(f"Predictions saved to {OUTPUT_DIR}/propensity_predictions.csv")


if __name__ == "__main__":
    main()
