-- Revenue reconciliation: row counts and totals must match between raw and processed, per platform.
-- failing_rows = number of (platform, metric) pairs that do not match.
WITH r AS (
    SELECT platform, COUNT(*) AS n, SUM(Revenue) AS rev, SUM(Conversions) AS conv,
           SUM(Acquisition_Cost * Conversions) AS spend
    FROM raw_campaigns GROUP BY platform
), p AS (
    SELECT platform, COUNT(*) AS n, SUM(revenue) AS rev, SUM(conversions) AS conv, SUM(spend) AS spend
    FROM campaigns GROUP BY platform
)
SELECT 'SQL-DQ06' AS check_id, 'raw vs processed totals per platform (rows, revenue, conversions, spend)' AS check_name,
       COALESCE(SUM((r.n <> p.n)::INT + (r.rev <> p.rev)::INT + (r.conv <> p.conv)::INT
                    + (ABS(r.spend - p.spend) > 0.01)::INT), 99) AS failing_rows
FROM r FULL OUTER JOIN p USING (platform);
