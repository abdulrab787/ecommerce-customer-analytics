-- channel_used is multi-valued ("WhatsApp, YouTube"). Exploding it naively multiplies revenue
-- (one campaign counted once per channel). This query builds a channel bridge and uses an
-- EQUAL-SPLIT attribution rule so attributed revenue still sums to the campaign total.
WITH bridge AS (
    SELECT
        campaign_id,
        TRIM(ch)                                           AS channel,
        revenue,
        spend,
        LEN(STRING_SPLIT(channel_used, ','))               AS n_channels
    FROM campaigns,
         UNNEST(STRING_SPLIT(channel_used, ',')) AS t(ch)
)
SELECT
    channel,
    COUNT(DISTINCT campaign_id)                            AS campaigns_using_channel,
    SUM(revenue)                                           AS naive_revenue_double_counted,
    SUM(revenue / n_channels)                              AS attributed_revenue_equal_split,
    SUM(spend / n_channels)                                AS attributed_spend_equal_split,
    (SUM(revenue / n_channels) - SUM(spend / n_channels))
        / SUM(spend / n_channels)                          AS attributed_roi
FROM bridge
GROUP BY channel
ORDER BY attributed_revenue_equal_split DESC;
