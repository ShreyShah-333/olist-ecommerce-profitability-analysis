# Power BI — Interactive Dashboard (Week 3)

This folder will hold the `.pbix` file and any exported measures documentation for the interactive dashboard, built on top of the outputs from `../sql/` and `../python/`.

## Planned pages

| Page | Contents |
|---|---|
| Profitability Overview | Total revenue, profitability proxy, and margin % trends by month, category, and seller state; top/bottom 10 categories by proxy profit |
| Delivery Performance | On-time delivery rate, average delivery days (actual vs. estimated), delivery delay distribution by state, correlation view between delivery delay and review score |
| Customer Retention | Monthly cohort retention heatmap, overall repeat-purchase rate, repeat vs. one-time customer revenue split |
| Propensity Insights | Distribution of predicted repeat-purchase probability from the Python model, segmented by category and order value, to flag high-potential first-time customers |

## Planned core measures (DAX, draft)

```
Total Revenue = SUM(order_items[price])
Total Freight = SUM(order_items[freight_value])
Profitability Proxy = SUM(order_items[profitability_proxy])
Profit Margin % = DIVIDE([Profitability Proxy], [Total Revenue])
On-Time Delivery Rate =
    DIVIDE(
        CALCULATE(COUNTROWS(orders), orders[delivered_on_time] = TRUE),
        COUNTROWS(orders)
    )
Repeat Purchase Rate =
    DIVIDE(
        CALCULATE(DISTINCTCOUNT(customers[customer_unique_id]), customers[order_count] > 1),
        DISTINCTCOUNT(customers[customer_unique_id])
    )
```

## Data source

The dashboard will connect either directly to the Postgres database (via Power BI's built-in Postgres connector) or to the CSV exports produced by the scripts in `../python/outputs/`, whichever is more convenient once we get there.

## Status

Not started yet — this folder is a placeholder until Week 2 (Python) analysis is complete, since the dashboard measures build on the profitability proxy and propensity outputs.
