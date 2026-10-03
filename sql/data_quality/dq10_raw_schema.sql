-- Schema drift: the raw union must expose exactly the 16 expected source columns plus platform.
WITH expected(col) AS (
    VALUES ('Campaign_ID'), ('Campaign_Type'), ('Target_Audience'), ('Duration'), ('Channel_Used'),
           ('Impressions'), ('Clicks'), ('Leads'), ('Conversions'), ('Revenue'), ('Acquisition_Cost'),
           ('ROI'), ('Language'), ('Engagement_Score'), ('Customer_Segment'), ('Date'), ('platform')
), actual AS (
    SELECT column_name AS col FROM (DESCRIBE raw_campaigns)
)
SELECT 'SQL-DQ10' AS check_id, 'raw schema has exactly the expected columns' AS check_name,
       (SELECT COUNT(*) FROM expected WHERE col NOT IN (SELECT col FROM actual))
     + (SELECT COUNT(*) FROM actual WHERE col NOT IN (SELECT col FROM expected)) AS failing_rows;
