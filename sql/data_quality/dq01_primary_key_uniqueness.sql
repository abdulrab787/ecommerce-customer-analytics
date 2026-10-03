-- campaign_id must be unique in the raw union, the processed fact and the predictions table.
SELECT 'SQL-DQ01' AS check_id, 'campaign_id unique (raw, processed, predictions)' AS check_name,
       (SELECT COUNT(*) - COUNT(DISTINCT campaign_id) FROM raw_campaigns)
     + (SELECT COUNT(*) - COUNT(DISTINCT campaign_id) FROM campaigns)
     + (SELECT COUNT(*) - COUNT(DISTINCT campaign_id) FROM churn_predictions) AS failing_rows;
