--a. Monthly revenue trend
SELECT
    DATE_FORMAT(order_date, '%Y-%m') AS month,
    SUM(order_amount) AS monthly_revenue
FROM orders
GROUP BY month
ORDER BY month;

--b. Revenue by country
SELECT
    c.country,
    SUM(o.order_amount) AS revenue
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.country
ORDER BY revenue DESC;

--c. Top product categories
SELECT
    p.category,
    SUM(oi.quantity * oi.unit_price) AS revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY revenue DESC;
