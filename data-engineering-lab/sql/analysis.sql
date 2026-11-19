-- Run against the local retail.db using Python as described in lesson 01.
-- One row per order in silver; dimensions describe customers and products.
SELECT s.order_id, c.customer_name, p.product_name,
       s.quantity * s.unit_price_cents / 100.0 AS revenue
FROM silver s
JOIN dim_customer c ON c.customer_id = s.customer_id
JOIN dim_product p ON p.product_id = s.product_id
ORDER BY s.order_id;

SELECT c.region, SUM(s.quantity * s.unit_price_cents) / 100.0 AS revenue
FROM silver s JOIN dim_customer c ON c.customer_id = s.customer_id
GROUP BY c.region ORDER BY revenue DESC;

-- Rank orders within each region, retaining every individual order.
SELECT c.region, s.order_id, s.quantity * s.unit_price_cents / 100.0 AS revenue,
       ROW_NUMBER() OVER (
         PARTITION BY c.region
         ORDER BY s.quantity * s.unit_price_cents DESC, s.order_id
       ) AS revenue_rank
FROM silver s JOIN dim_customer c ON c.customer_id = s.customer_id
ORDER BY c.region, revenue_rank;
