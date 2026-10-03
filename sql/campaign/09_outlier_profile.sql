-- Outlier profile (informational, not a gate): Tukey IQR fences per numeric field.
-- Outliers here are flagged for review, not removed - extreme ROI campaigns are real rows in the source.
WITH long AS (
    SELECT 'revenue' AS metric, revenue::DOUBLE AS v FROM campaigns
    UNION ALL SELECT 'spend', spend FROM campaigns
    UNION ALL SELECT 'roi', (revenue - spend) / spend FROM campaigns
    UNION ALL SELECT 'acquisition_cost', acquisition_cost FROM campaigns
    UNION ALL SELECT 'conversions', conversions::DOUBLE FROM campaigns
    UNION ALL SELECT 'engagement_score', engagement_score FROM campaigns
), fences AS (
    SELECT metric,
           QUANTILE_CONT(v, 0.25) AS q1,
           QUANTILE_CONT(v, 0.75) AS q3
    FROM long GROUP BY metric
)
SELECT
    l.metric,
    MIN(l.v)                                                           AS min_value,
    ANY_VALUE(f.q1)                                                    AS q1,
    MEDIAN(l.v)                                                        AS median,
    ANY_VALUE(f.q3)                                                    AS q3,
    MAX(l.v)                                                           AS max_value,
    ANY_VALUE(f.q3 + 1.5 * (f.q3 - f.q1))                              AS upper_fence,
    SUM(CASE WHEN l.v > f.q3 + 1.5 * (f.q3 - f.q1)
              OR l.v < f.q1 - 1.5 * (f.q3 - f.q1) THEN 1 ELSE 0 END)   AS outlier_rows,
    AVG(CASE WHEN l.v > f.q3 + 1.5 * (f.q3 - f.q1)
              OR l.v < f.q1 - 1.5 * (f.q3 - f.q1) THEN 1.0 ELSE 0.0 END) AS outlier_share
FROM long l JOIN fences f USING (metric)
GROUP BY l.metric
ORDER BY outlier_share DESC;
