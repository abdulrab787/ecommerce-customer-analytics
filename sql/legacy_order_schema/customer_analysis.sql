-- 1) Create database
CREATE DATABASE ecommerce_analytics;
USE ecommerce_analytics;

-- 2) Customers table
CREATE TABLE customers (
    customer_id      INT PRIMARY KEY,
    customer_name    VARCHAR(255),
    email            VARCHAR(255),
    country          VARCHAR(100),
    signup_date      DATE
);

-- 3) Orders table
CREATE TABLE orders (
    order_id         INT PRIMARY KEY,
    customer_id      INT,
    order_date       DATE,
    order_status     VARCHAR(50),
    payment_method   VARCHAR(50),
    order_amount     DECIMAL(10,2),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- 4) Order items table
CREATE TABLE order_items (
    order_item_id    INT PRIMARY KEY,
    order_id         INT,
    product_id       INT,
    quantity         INT,
    unit_price       DECIMAL(10,2),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

-- 5) Products table 
CREATE TABLE products (
    product_id       INT PRIMARY KEY,
    product_name     VARCHAR(255),
    category         VARCHAR(100),
    unit_cost        DECIMAL(10,2)
);

-- 6) Total revenue, orders, customers:
-- Total revenue
SELECT SUM(order_amount) AS total_revenue
FROM orders;

-- Total number of orders
SELECT COUNT(*) AS total_orders
FROM orders;

-- Total number of unique customers
SELECT COUNT(DISTINCT customer_id) AS total_customers
FROM orders;

-- 7) Top customers by revenue:
SELECT 
    c.customer_id,
    c.customer_name,
    SUM(o.order_amount) AS customer_revenue
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name
ORDER BY customer_revenue DESC
LIMIT 20;
