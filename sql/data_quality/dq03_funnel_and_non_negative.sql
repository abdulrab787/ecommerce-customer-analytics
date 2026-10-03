-- Funnel order (conversions <= leads <= clicks <= impressions) and no negative measures.
SELECT 'SQL-DQ03' AS check_id, 'funnel order and non-negative measures' AS check_name,
       COUNT(*) AS failing_rows
FROM campaigns
WHERE clicks > impressions OR leads > clicks OR conversions > leads
   OR LEAST(impressions, clicks, leads, conversions, revenue, acquisition_cost, duration) < 0;
