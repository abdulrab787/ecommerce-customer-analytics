-- Brand comparison (Nykaa vs Purplle vs Tira) with share of total revenue (window over the grouped result).
SELECT
    platform,
    COUNT(*)                                       AS campaigns,
    SUM(revenue)                                   AS revenue,
    SUM(spend)                                     AS spend,
    (SUM(revenue) - SUM(spend)) / SUM(spend)       AS roi,
    SUM(conversions) * 1.0 / SUM(clicks)           AS conversion_rate,
    SUM(spend) / SUM(conversions)                  AS cpa,
    SUM(revenue) / SUM(SUM(revenue)) OVER ()       AS revenue_share
FROM campaigns
GROUP BY platform
ORDER BY revenue DESC;
