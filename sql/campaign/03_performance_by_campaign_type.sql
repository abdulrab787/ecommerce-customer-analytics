-- Campaign type x platform, ranked by ROI inside each platform.
SELECT
    platform,
    campaign_type,
    COUNT(*)                                       AS campaigns,
    SUM(revenue)                                   AS revenue,
    (SUM(revenue) - SUM(spend)) / SUM(spend)       AS roi,
    SUM(clicks) * 1.0 / SUM(impressions)           AS ctr,
    SUM(conversions) * 1.0 / SUM(clicks)           AS conversion_rate,
    RANK() OVER (PARTITION BY platform
                 ORDER BY (SUM(revenue) - SUM(spend)) / SUM(spend) DESC) AS roi_rank_in_platform
FROM campaigns
GROUP BY platform, campaign_type
ORDER BY platform, roi_rank_in_platform;
