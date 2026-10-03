-- Base RFM table
CREATE OR REPLACE VIEW customer_rfm AS
SELECT
    o.customer_id,
    MAX(o.order_date)                           AS last_order_date,
    DATEDIFF(CURDATE(), MAX(o.order_date))      AS recency_days,
    COUNT(o.order_id)                           AS frequency,
    SUM(o.order_amount)                         AS monetary
FROM orders o
GROUP BY o.customer_id;
