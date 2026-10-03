-- DuckDB setup: expose the CSVs as views. Run from the repo root (src.sql_runner does this).

-- Three raw brand files, unioned, with a platform column and the dd-mm-yyyy date parsed.
CREATE OR REPLACE VIEW raw_campaigns AS
SELECT *, 'Nykaa' AS platform   FROM read_csv('data/raw/nykaa_campaign_data.csv',   header = true, types = {'Date': 'VARCHAR'})
UNION ALL
SELECT *, 'Purplle' AS platform FROM read_csv('data/raw/purplle_campaign_data.csv', header = true, types = {'Date': 'VARCHAR'})
UNION ALL
SELECT *, 'Tira' AS platform    FROM read_csv('data/raw/tira_campaign_data.csv',    header = true, types = {'Date': 'VARCHAR'});

-- Cleaned campaign fact (the table loaded into Power BI). Grain: one row per campaign_id.
-- acquisition_cost is a cost PER CONVERSION, so spend = acquisition_cost * conversions.
CREATE OR REPLACE VIEW campaigns AS
SELECT *, acquisition_cost * conversions AS spend
FROM read_csv('data/processed/campaign_data_cleaned.csv', header = true);

CREATE OR REPLACE VIEW churn_predictions AS
SELECT * FROM read_csv('data/processed/churn_predictions.csv', header = true);

CREATE OR REPLACE VIEW rfm_segments AS
SELECT * FROM read_csv('data/processed/rfm_segments.csv', header = true);

CREATE OR REPLACE VIEW clv_segments AS
SELECT * FROM read_csv('data/processed/clv_segments.csv', header = true);
