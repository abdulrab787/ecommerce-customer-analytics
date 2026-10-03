-- Monthly trend with month-over-month growth (LAG) and running revenue (cumulative window).
-- Data covers 2024-07-01 to 2025-06-24, so year-over-year comparison is not possible;
-- June 2025 is a partial month.
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', CAST(date AS DATE))   AS month,
        COUNT(*)                                  AS campaigns,
        SUM(revenue)                              AS revenue,
        SUM(spend)                                AS spend
    FROM campaigns
    GROUP BY 1
)
SELECT
    month,
    campaigns,
    revenue,
    (revenue - spend) / spend                                     AS roi,
    revenue / LAG(revenue) OVER (ORDER BY month) - 1              AS revenue_mom_growth,
    SUM(revenue) OVER (ORDER BY month ROWS UNBOUNDED PRECEDING)   AS cumulative_revenue
FROM monthly
ORDER BY month;
