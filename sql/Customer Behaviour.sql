-- a. Repeat vs New Customers
SELECT
    CASE 
        WHEN order_count = 1 THEN 'New Customer'
        ELSE 'Repeat Customer'
    END AS customer_type,
    COUNT(*) AS total_customers
FROM (
    SELECT customer_id, COUNT(order_id) AS order_count
    FROM orders
    GROUP BY customer_id
) t
GROUP BY customer_type;

--b. Average time between purchases
SELECT 
    customer_id,
    AVG(DATEDIFF(next_order_date, order_date)) AS avg_days_between_orders
FROM (
    SELECT 
        customer_id,
        order_date,
        LEAD(order_date) OVER (PARTITION BY customer_id ORDER BY order_date) AS next_order_date
    FROM orders
) t
WHERE next_order_date IS NOT NULL
GROUP BY customer_id;

--c. Customer lifetime revenue
SELECT 
    customer_id,
    SUM(order_amount) AS lifetime_value
FROM orders
GROUP BY customer_id
ORDER BY lifetime_value DESC;
