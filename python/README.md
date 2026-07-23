# Python — EDA, Cohort Retention, Profitability Proxy & Propensity Model

This folder contains the Week 2 analysis scripts. Each script connects to the Postgres database populated by the SQL scripts in `../sql/` and reads/writes from an `outputs/` folder created automatically on first run (git-ignored).

## Setup

```bash
cd python
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in this folder (not committed) with your database connection string:

```
DATABASE_URL=postgresql://user:password@localhost:5432/olist
```

## Scripts

| Script | Purpose |
|---|---|
| `01_eda.py` | Order volume over time, category mix, delivery time distribution (actual vs. estimated), review score distribution |
| `02_cohort_retention.py` | Builds monthly acquisition cohorts and a retention heatmap; reports overall repeat-purchase rate |
| `03_profitability_proxy.py` | Builds a transparent, documented profitability proxy per order item (price minus freight, estimated commission, and estimated return cost), rolled up by category and seller state |
| `04_propensity_model.py` | Random Forest classifier estimating each new customer's likelihood of becoming a repeat customer, based on their first-order characteristics |

Run them in order:

```bash
python 01_eda.py
python 02_cohort_retention.py
python 03_profitability_proxy.py
python 04_propensity_model.py
```

## A note on the profitability proxy

Olist's public dataset doesn't include Olist's own commission rate or sellers' cost of goods, so an exact profit margin can't be computed. `03_profitability_proxy.py` makes its assumptions explicit as module-level constants (commission rate, return-cost rate) rather than hard-coding them invisibly, so they can be adjusted or challenged.

## A note on the propensity model

This is the one place AI/ML is used in the core analysis. It's additive, not load-bearing: it sits on top of the SQL/pandas profitability numbers and never replaces them. All financial figures come from transparent, auditable SQL and pandas logic.
