-- Customers inactive for more than 90 days
SELECT
    c.customer_id,
    c.customer_name,
    r.last_order_date,
    r.recency_days
FROM customers c
JOIN customer_rfm r ON c.customer_id = r.customer_id
WHERE r.recency_days > 90
ORDER BY r.recency_days DESC;

-- Create churn label (1 = churned, 0 = active)
CREATE OR REPLACE VIEW customer_churn_label AS
SELECT
    customer_id,
    recency_days,
    frequency,
    monetary,
    CASE 
        WHEN recency_days > 90 THEN 1
        ELSE 0
    END AS churn_flag
FROM customer_rfm;
