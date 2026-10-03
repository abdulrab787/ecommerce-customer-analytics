-- Every prediction row maps to a campaign, and every campaign segment exists in both segment tables.
SELECT 'SQL-DQ07' AS check_id, 'referential integrity (predictions -> campaigns, campaigns -> segment tables)' AS check_name,
       (SELECT COUNT(*) FROM churn_predictions cp
         WHERE NOT EXISTS (SELECT 1 FROM campaigns c WHERE c.campaign_id = cp.campaign_id))
     + (SELECT COUNT(*) FROM campaigns c
         WHERE NOT EXISTS (SELECT 1 FROM rfm_segments r WHERE r.Customer_Segment = c.customer_segment))
     + (SELECT COUNT(*) FROM campaigns c
         WHERE NOT EXISTS (SELECT 1 FROM clv_segments s WHERE s.customer_segment = c.customer_segment))
       AS failing_rows;
