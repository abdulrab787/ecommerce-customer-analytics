-- Share of campaigns in the bottom ROI quartile, by campaign type and language.
-- If these attributes drove performance, the rates would move well away from 25%.
WITH q AS (
    SELECT QUANTILE_CONT((revenue - spend) / spend, 0.25) AS p25
    FROM campaigns
)
SELECT
    c.campaign_type,
    c.language,
    COUNT(*)                                                                      AS campaigns,
    AVG(CASE WHEN (c.revenue - c.spend) / c.spend < q.p25 THEN 1.0 ELSE 0.0 END)  AS pct_bottom_quartile_roi
FROM campaigns AS c
CROSS JOIN q
GROUP BY c.campaign_type, c.language
ORDER BY pct_bottom_quartile_roi DESC;
