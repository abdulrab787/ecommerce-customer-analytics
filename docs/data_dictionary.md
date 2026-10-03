# Data Dictionary

**Source:** Kaggle (public dataset): three CSV files of beauty e-commerce marketing campaigns.
The data shows signs of being synthetic: exactly 55,555 rows per brand, identical date ranges, and near-identical ROI
across every brand, campaign type and segment. Treat it as a practice dataset, not company records.

**Grain:** one row = one marketing campaign. **There is no customer, order or product identifier.**

**Currency:** not stated in the source. The project labels money as "Rs." on the dashboard, but the source does not confirm the currency.

Ranges below were measured on the current files (166,665 rows, 2024-07-01 to 2025-06-24).

---

## 1. Raw files — `data/raw/{nykaa,purplle,tira}_campaign_data.csv`

55,555 rows each, identical 16-column schema (PascalCase headers; lower-cased during cleaning).

| Field | Data Type | Description | Source | Validation |
|---|---|---|---|---|
| `Campaign_ID` | string | Campaign identifier, prefix = brand (`NY-`, `PU-`, `TI-`) + `CMP-` + number | raw | unique across all three files (DQ001, SQL-DQ01) |
| `Campaign_Type` | string | Email, Influencer, Paid Ads, SEO, Social Media | raw | accepted values (DQ016) |
| `Target_Audience` | string | Audience the campaign targeted (5 values) | raw | disagrees with `Customer_Segment` on 80.1% of rows (DQ052 warning) |
| `Duration` | integer | Campaign length in days | raw | 5 to 30; non-negative (DQ030) |
| `Channel_Used` | string | One or more channels, comma-separated (e.g. `"WhatsApp, YouTube"`); 156 combinations of 6 channels | raw | multi-valued — cardinality warning (DQ039); split with a bridge for channel analysis |
| `Impressions` | integer | Times the campaign was shown | raw | 10,001 to 100,000; ≥ clicks (DQ031) |
| `Clicks` | integer | Clicks | raw | 202 to 14,944; ≤ impressions, ≥ leads (DQ031–032) |
| `Leads` | integer | Leads captured | raw | 48 to 8,876; ≤ clicks, ≥ conversions |
| `Conversions` | integer | Conversions (purchases) | raw | 17 to 6,686; ≤ leads (DQ033) |
| `Revenue` | integer | Revenue attributed to the campaign | raw | 3,895 to 4,579,910; revenue/conversion between 50 and 5,000 (DQ034, warning) |
| `Acquisition_Cost` | decimal | **Cost per conversion** (not total campaign cost) | raw | 8.18 to 15,473.16. Proven by `ROI = (Revenue − Acquisition_Cost × Conversions) / (Acquisition_Cost × Conversions)` on every row within rounding (DQ050, SQL-DQ05) |
| `ROI` | decimal | Return on spend, as a ratio (1.94 = 194%) | raw | −0.99 to 79.3; must match the formula above |
| `Language` | string | Hindi, English, Tamil, Bengali | raw | — |
| `Engagement_Score` | decimal | Engagement index (scale undocumented) | raw | 2.56 to 30.99; checked within 0–100 (DQ035) |
| `Customer_Segment` | string | Segment label (College Students, Premium Shoppers, Tier 2 City Customers, Working Women, Youth) | raw | 5 values; not a customer identifier |
| `Date` | string `dd-mm-yyyy` | Campaign date | raw | parses with explicit `%d-%m-%Y`; ≥ 2024-01-01; not in the future (DQ020–021, SQL-DQ04) |

## 2. Processed fact — `data/processed/campaign_data_cleaned.csv`

Built by `python -m src.preprocessing`. Loaded into Power BI as table `campaign_data`. 166,665 rows.
All raw fields are kept (snake_case names) plus:

| Field | Data Type | Description | Source | Validation |
|---|---|---|---|---|
| `date` | date (ISO `yyyy-mm-dd`) | Parsed from raw `Date` | derived | 359 distinct dates |
| `platform` | string | Brand: Nykaa, Purplle, Tira (from the source file) | derived | not null (DQ015); 55,555 rows each |
| `CTR` | decimal | clicks / impressions (row level) | derived | 0.020 to 0.150 |
| `Conversion_Rate` | decimal | conversions / clicks (row level) | derived | 0.059 to 0.479 |
| `CPL` | decimal | spend per lead = acquisition_cost × conversions / leads | derived | 6.11 to 5,731.63 |
| `CPCV` | decimal | spend per conversion (= acquisition_cost) | derived | equals `acquisition_cost` |

`spend` (= acquisition_cost × conversions) is not stored; it is computed in SQL (`campaigns` view), DAX (`Total Spend`)
and Python (`src/data_quality/kpis.py::spend`).

## 3. Model output — `data/processed/churn_predictions.csv`

Built by `python -m src.train_model`. Same 166,665 rows and columns as the fact, plus:

| Field | Data Type | Description | Source | Validation |
|---|---|---|---|---|
| `frequency` | integer | Number of campaigns in the row's `customer_segment` (constant per segment) | derived | — |
| `churn` | 0/1 | **Name kept for Power BI compatibility.** 1 = campaign ROI below the 25th percentile of the training period (< 0.04), i.e. an under-performing campaign. Not customer churn. | model label | positive rate 24.8%; minority ≥ 5% (DQ051) |
| `Churn_Prediction` | 0/1 | 1 = among the riskiest 25% by model score | model output | 25.0% flagged |

## 4. Segment tables — `data/processed/rfm_segments.csv`, `clv_segments.csv`

Built by `python -m src.segment_value`. **5 rows each (one per `customer_segment`), not per customer.**
Illustrative only — see `docs/kpi_definitions.md` § Segment value metrics.

`rfm_segments`: `Customer_Segment` (key), `Recency` (days, all 0), `Frequency` (campaign count), `Monetary` (revenue),
`R_Score` (constant 3), `F_Score`, `M_Score` (1–5 quintiles), `RFM_Score` (sum), `Segment` (High/Medium/Low Value).

`clv_segments`: `customer_segment` (key), `total_revenue`, `total_conversions`, `total_leads`, `total_clicks`,
`total_impressions`, `avg_engagement`, `frequency`, `CLV_simple`, `AOV`, `CLV_aov`, `RRetention_Rate` (unclipped
engagement proxy), `Retention_Rate` (clipped to 0.10–0.95), `CLV_discounted`.

Validation: join keys unique (DQ036–037), every fact segment present (DQ018–019), joining
to the fact does not multiply rows (DQ042, SQL-DQ08).

## 5. Quality and experiment outputs (also loaded into Power BI)

| File | Grain | Key fields |
|---|---|---|
| `reports/dq/dq_results.csv` | one row per DQ check (65) | `check_id`, `category`, `table`, `rule`, `severity`, `status` (PASS/WARN/FAIL), `observed`, `expected`, `failing_rows`, `run_ts` |
| `reports/experiments/experiment_decisions.csv` | one row per **simulated** experiment (4) | `experiment_id`, `primary_metric`, `planned_n_per_arm`, `srm_p_value`, `primary_lift`, `primary_ci_low/high`, `decision`, `reason`, `is_simulated` |
| `reports/experiments/experiment_metrics.csv` | experiment × metric | `experiment_id`, `metric`, `role` (primary/secondary/guardrail), `rel_lift`, `ci_low/high`, `p_value`, `status` |
| `reports/experiments/experiment_segments.csv` | experiment × segment | `rel_lift`, `p_value`, `p_holm`, `significant_after_holm` |
| `reports/sql/sql_dq_results.csv` | one row per SQL check (9) | `check_id`, `check_name`, `failing_rows`, `status` |

## 6. Keys, dimensions and measures

| Type | Fields |
|---|---|
| Primary key | `campaign_id` (raw union, fact, predictions) |
| Foreign keys | `churn_predictions.campaign_id → campaign_data.campaign_id`; `campaign_data.customer_segment → rfm_segments.Customer_Segment`, `→ clv_segments.customer_segment`; `campaign_data.date → Date.Date`; `experiment_metrics.experiment_id → experiment_decisions.experiment_id` |
| Dimensions (attributes on the fact) | `platform`, `campaign_type`, `channel_used`, `target_audience`, `customer_segment`, `language`, `date` |
| Additive measures | `impressions`, `clicks`, `leads`, `conversions`, `revenue`, spend (`acquisition_cost × conversions`) |
| Non-additive (never SUM) | `acquisition_cost`, `roi`, `engagement_score`, `CTR`, `Conversion_Rate`, `CPL`, `CPCV` — recompute from additive measures |
