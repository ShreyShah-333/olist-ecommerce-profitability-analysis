-- ============================================================
-- Load raw Olist CSVs into the schema created in 01_schema.sql
--
-- Prerequisite: download the 9 CSVs from
-- https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
-- and place them in a local data/raw/ folder at the repo root
-- (data/ is gitignored, so these files stay local only).
--
-- Usage (run from the repo root, with psql):
--   psql -d your_database -f sql/02_load_data.sql
--
-- Note: \copy runs client-side via psql, so file paths are
-- resolved relative to the directory you run psql from.
-- ============================================================

-- Load order matters: parent tables before child tables (foreign keys)

\copy customers FROM 'data/raw/olist_customers_dataset.csv' WITH (FORMAT csv, HEADER true);

\copy sellers FROM 'data/raw/olist_sellers_dataset.csv' WITH (FORMAT csv, HEADER true);

\copy product_category_name_translation FROM 'data/raw/product_category_name_translation.csv' WITH (FORMAT csv, HEADER true);

\copy products FROM 'data/raw/olist_products_dataset.csv' WITH (FORMAT csv, HEADER true);

\copy orders FROM 'data/raw/olist_orders_dataset.csv' WITH (FORMAT csv, HEADER true);

\copy order_items FROM 'data/raw/olist_order_items_dataset.csv' WITH (FORMAT csv, HEADER true);

\copy order_payments FROM 'data/raw/olist_order_payments_dataset.csv' WITH (FORMAT csv, HEADER true);

\copy order_reviews FROM 'data/raw/olist_order_reviews_dataset.csv' WITH (FORMAT csv, HEADER true);

\copy geolocation FROM 'data/raw/olist_geolocation_dataset.csv' WITH (FORMAT csv, HEADER true);

-- ============================================================
-- Sanity check: row counts per table after load
-- ============================================================
SELECT 'customers' AS table_name, COUNT(*) FROM customers
UNION ALL SELECT 'sellers', COUNT(*) FROM sellers
UNION ALL SELECT 'product_category_name_translation', COUNT(*) FROM product_category_name_translation
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'orders', COUNT(*) FROM orders
UNION ALL SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL SELECT 'order_payments', COUNT(*) FROM order_payments
UNION ALL SELECT 'order_reviews', COUNT(*) FROM order_reviews
UNION ALL SELECT 'geolocation', COUNT(*) FROM geolocation;
