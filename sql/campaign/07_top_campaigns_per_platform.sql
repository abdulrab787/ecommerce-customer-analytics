-- Top 5 campaigns by revenue in each platform (ROW_NUMBER + QUALIFY), with overall ROI decile.
SELECT
    platform,
    campaign_id,
    campaign_type,
    customer_segment,
    revenue,
    (revenue - spend) / spend                                        AS roi,
    NTILE(10) OVER (ORDER BY (revenue - spend) / spend)              AS roi_decile_overall,
    ROW_NUMBER() OVER (PARTITION BY platform ORDER BY revenue DESC)  AS revenue_rank
FROM campaigns
QUALIFY revenue_rank <= 5
ORDER BY platform, revenue_rank;
