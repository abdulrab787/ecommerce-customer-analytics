-- Headline KPIs. Rates are ratios of sums (additive-safe), never averages of row-level ratios.
SELECT
    COUNT(*)                                             AS campaign_rows,
    SUM(revenue)                                         AS total_revenue,
    SUM(spend)                                           AS total_spend,
    (SUM(revenue) - SUM(spend)) / SUM(spend)             AS roi,
    SUM(revenue) / SUM(spend)                            AS roas,
    SUM(impressions)                                     AS total_impressions,
    SUM(clicks)                                          AS total_clicks,
    SUM(leads)                                           AS total_leads,
    SUM(conversions)                                     AS total_conversions,
    SUM(clicks)      * 1.0 / SUM(impressions)            AS ctr,
    SUM(conversions) * 1.0 / SUM(clicks)                 AS conversion_rate,
    SUM(spend)   / SUM(conversions)                      AS cpa,
    SUM(spend)   / SUM(leads)                            AS cpl,
    SUM(revenue) / SUM(conversions)                      AS aov,
    SUM(revenue) - SUM(spend)                            AS net_profit
FROM campaigns;
