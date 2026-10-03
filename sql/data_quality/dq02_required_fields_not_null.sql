-- Required fields on the processed fact must be populated.
SELECT 'SQL-DQ02' AS check_id, 'required fields not null' AS check_name,
       COUNT(*) AS failing_rows
FROM campaigns
WHERE campaign_id IS NULL OR platform IS NULL OR campaign_type IS NULL OR channel_used IS NULL
   OR customer_segment IS NULL OR date IS NULL
   OR impressions IS NULL OR clicks IS NULL OR leads IS NULL OR conversions IS NULL
   OR revenue IS NULL OR acquisition_cost IS NULL;
