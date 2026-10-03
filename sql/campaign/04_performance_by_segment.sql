-- Customer segment (as labelled on the campaign) vs target audience agreement.
-- target_audience and customer_segment disagree on ~80% of rows (DQ052), so segment
-- results describe the label, not a verified audience.
SELECT
    customer_segment,
    COUNT(*)                                                   AS campaigns,
    SUM(revenue)                                               AS revenue,
    (SUM(revenue) - SUM(spend)) / SUM(spend)                   AS roi,
    SUM(revenue) / SUM(conversions)                            AS aov,
    AVG(engagement_score)                                      AS avg_engagement,
    AVG(CASE WHEN target_audience = customer_segment THEN 1.0 ELSE 0.0 END) AS pct_audience_matches_segment
FROM campaigns
GROUP BY customer_segment
ORDER BY revenue DESC;
