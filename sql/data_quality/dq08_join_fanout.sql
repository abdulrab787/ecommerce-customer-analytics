-- Joining the fact to a dimension-like table must not multiply rows (duplicate join keys inflate KPIs).
SELECT 'SQL-DQ08' AS check_id, 'no row multiplication when joining fact to segment tables' AS check_name,
       ((SELECT COUNT(*) FROM campaigns c JOIN rfm_segments r ON r.Customer_Segment = c.customer_segment)
         - (SELECT COUNT(*) FROM campaigns))
     + ((SELECT COUNT(*) FROM campaigns c JOIN clv_segments s ON s.customer_segment = c.customer_segment)
         - (SELECT COUNT(*) FROM campaigns))
       AS failing_rows;
