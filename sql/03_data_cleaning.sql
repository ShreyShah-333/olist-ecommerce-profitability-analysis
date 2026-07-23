-- ============================================================
-- Data validation & cleaning checks
-- Run these after 02_load_data.sql to sanity-check the loaded
-- data. These are all read-only SELECT checks (no rows are
-- modified) so you can review results before deciding whether
-- and how to clean/exclude anything downstream in Python.
-- ============================================================

-- 1. Customers with multiple customer_id's for the same person
--    (customer_unique_id repeats across orders by design in this
--    dataset; useful to know for retention/repeat-purchase analysis)
SELECT customer_unique_id, COUNT(*) AS num_customer_ids
FROM customers
GROUP BY customer_unique_id
HAVING COUNT(*) > 1
ORDER BY num_customer_ids DESC;

-- 2. Orders marked 'delivered' but missing a delivery date
SELECT order_id, order_status, order_delivered_customer_date
FROM orders
WHERE order_status = 'delivered' AND order_delivered_customer_date IS NULL;

-- 3. Orders with a delivery date earlier than the purchase date
--    (should return zero rows if the data is clean)
SELECT order_id, order_purchase_timestamp, order_delivered_customer_date
FROM orders
WHERE order_delivered_customer_date < order_purchase_timestamp;

-- 4. Order items with non-positive prices or negative freight values
SELECT *
FROM order_items
WHERE price <= 0 OR freight_value < 0;

-- 5. Review scores outside the expected 1-5 range
SELECT *
FROM order_reviews
WHERE review_score NOT BETWEEN 1 AND 5;

-- 6. Products referencing a category with no English translation
SELECT p.product_id, p.product_category_name
FROM products p
LEFT JOIN product_category_name_translation t
  ON p.product_category_name = t.product_category_name
WHERE p.product_category_name IS NOT NULL AND t.product_category_name IS NULL;

-- 7. Orders with no matching order_items rows
SELECT o.order_id
FROM orders o
LEFT JOIN order_items oi ON o.order_id = oi.order_id
WHERE oi.order_id IS NULL;

-- 8. Orders where total payments don't reconcile with item + freight totals
--    (small rounding differences are expected; large gaps are worth a look)
SELECT
  oi.order_id,
  SUM(oi.price + oi.freight_value) AS items_total,
  SUM(op.payment_value) AS payments_total
FROM order_items oi
JOIN order_payments op ON oi.order_id = op.order_id
GROUP BY oi.order_id
HAVING ABS(SUM(oi.price + oi.freight_value) - SUM(op.payment_value)) > 0.01
LIMIT 100;
