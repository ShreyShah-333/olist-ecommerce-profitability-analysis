# Olist E-Commerce Profitability & Retention Analysis

A SQL + Python + Power BI case study analyzing the [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) to identify which product categories, seller regions, and delivery-performance tiers drive profitable, repeat customers — and which are quietly costing the business money through late deliveries, poor reviews, and one-time-only buyers.

> **Note:** A separate future project will explore a RAG-based natural-language Q&A layer (Typesense + LangChain/LangGraph) on top of this analysis. This repo is scoped to SQL, Python, and Power BI only.

---

## 📌 Problem Statement

Olist is a marketplace connecting small Brazilian merchants to customers. This project answers: which product categories, seller regions, and delivery-performance tiers are most profitable and most likely to generate repeat business, and where should the business focus operational fixes or seller support to improve both profitability and retention?

## 🗂️ Dataset

[Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) — 100k real, anonymized orders from 2016–2018, across 9 linked CSV files:

| File | Description |
|---|---|
| `olist_orders_dataset.csv` | Order status, timestamps |
| `olist_order_items_dataset.csv` | Items per order, price, freight |
| `olist_order_payments_dataset.csv` | Payment type and installments |
| `olist_order_reviews_dataset.csv` | Customer review scores and text |
| `olist_customers_dataset.csv` | Customer location |
| `olist_products_dataset.csv` | Product category and attributes |
| `olist_sellers_dataset.csv` | Seller location |
| `olist_geolocation_dataset.csv` | Zip code to lat/lng mapping |
| `product_category_name_translation.csv` | Category names in English |

**License:** CC BY-NC-SA 4.0

## 🧰 Tech Stack

SQL (PostgreSQL) · Python (pandas, matplotlib/seaborn, scikit-learn) · Power BI

## 🗺️ Project Roadmap

- [x] **Week 1 — Data Modeling & Cleaning (SQL)** — Load the 9 CSVs into a relational schema, write joins connecting orders → items → payments → reviews → customers → sellers, handle one-order-multiple-items/sellers cases, and clean nulls/duplicates. *(Schema, load, and cleaning scripts complete in `sql/`.)*
- [x] **Week 2 — Exploratory Analysis & Modeling (Python)** — Order volume trends, delivery time distributions, review score patterns by category/region, a cohort retention analysis using `customer_unique_id`, a profitability proxy (price minus freight minus an assumed cost ratio, clearly documented as an assumption), and a repeat-purchase propensity model (Random Forest). *(Scripts complete in `python/`; awaiting a run against the loaded dataset.)*
- [ ] **Week 3 — Dashboard (Power BI)** — Build the executive-facing dashboard surfacing contribution margin by category/region, cohort retention curves, and delivery-delay vs. review-score relationships.
- [ ] **Week 4 — Recommendation & Polish** — Write a one-page business recommendation, tighten the analysis, and finalize documentation.

## ✅ How We'll Measure Success

- **Profitability:** Contribution margin proxy per category and seller region, ranking them from most to least profitable rather than by revenue alone.
- **Process improvement:** Quantified relationship between delivery delay and review score (e.g. average review score for on-time vs. late orders), giving a data-backed case for logistics investment.
- **Retention:** Cohort curves showing the percentage of customers still purchasing in month 2, 3, and 6 after their first order, segmented by category/region.
- **Predictive lift:** Precision/recall/AUC for the repeat-purchase propensity model, plus a lift metric — what percentage of actual repeat buyers would be captured by targeting the top-decile predicted customers versus random targeting.

## 📁 Repository Structure

```
olist-ecommerce-profitability-analysis/
├── sql/
│   ├── 01_schema.sql            # Table definitions and indexes
│   ├── 02_load_data.sql         # \copy commands to load the 9 CSVs
│   └── 03_data_cleaning.sql     # Read-only validation/cleaning checks
├── python/
│   ├── requirements.txt
│   ├── 01_eda.py                 # Exploratory data analysis
│   ├── 02_cohort_retention.py    # Cohort retention analysis
│   ├── 03_profitability_proxy.py # Profitability proxy calculation
│   └── 04_propensity_model.py    # Repeat-purchase propensity model
├── powerbi/                      # Power BI dashboard file(s) (Week 3)
└── README.md
```
