# KPI Definitions

One definition per KPI, implemented identically in three places and reconciled automatically:

| Layer | Where | Reconciliation |
|---|---|---|
| Python (reference) | `src/data_quality/kpis.py::compute_kpis` | — |
| SQL | `sql/campaign/01_kpi_summary.sql` | SQL-DQ09: SQL vs Python vs Power BI within ±0.5% |
| DAX | `Measure's` table in the semantic model | DQ053–DQ065: Power BI snapshot (`powerbi/dq/kpi_snapshot.dax`) vs raw data within ±0.5% |

**Grain rules**
* The fact grain is one campaign. `acquisition_cost` is a cost **per conversion**, so **Spend = Σ(acquisition_cost × conversions)**.
* Rates are **ratios of sums** (Σclicks / Σimpressions), never averages of row-level ratios, so they stay correct under any filter.
* Values in "Current value" are for the full dataset (166,665 campaigns). Currency is not stated in the source.

## Core marketing KPIs

| KPI | Definition | Formula | Grain | Source | Current value |
|---|---|---|---|---|---|
| Campaigns | Number of campaign rows | `COUNT(campaign_id)` | campaign | DAX `Campaign Row Count`, SQL, Python | 166,665 |
| Revenue | Revenue attributed to campaigns | `Σ revenue` | campaign, additive | DAX `Total Revenue` | 85,650,246,071 |
| Spend | Media / acquisition spend | `Σ (acquisition_cost × conversions)` | campaign, additive | DAX `Total Spend` | 29,128,207,786 |
| Net Profit (contribution after media) | Revenue minus spend (no COGS in the data) | `Revenue − Spend` | any | DAX `Net Profit` | 56,522,038,285 |
| ROI | Return on media spend | `(Revenue − Spend) / Spend` | any | DAX `ROI` | 194.0% |
| ROAS | Revenue per unit of spend | `Revenue / Spend` | any | DAX `ROAS` (`Marketing ROI` is an alias) | 2.94x |
| Impressions | Ad impressions | `Σ impressions` | additive | DAX `Total Impressions` | 9,176,717,247 |
| Clicks | Clicks | `Σ clicks` | additive | DAX `Total Clicks` | 780,386,787 |
| Leads | Leads | `Σ leads` | additive | DAX `Total Leads` | 311,915,911 |
| Conversions | Conversions | `Σ conversions` | additive | DAX `Total Conversions` | 171,513,099 |
| CTR | Click-through rate | `Σ clicks / Σ impressions` | any | DAX `CTR` | 8.50% |
| Conversion Rate | Conversions per click | `Σ conversions / Σ clicks` | any | DAX `Conversion Rate` | 21.98% |
| Lead Rate | Leads per click | `Σ leads / Σ clicks` | any | DAX `Lead Rate` | 39.97% |
| CPA | Spend per conversion | `Spend / Σ conversions` | any | DAX `CPA` (`Cost per Conversion` alias) | 169.83 |
| CPL | Spend per lead | `Spend / Σ leads` | any | DAX `CPL` | 93.38 |
| AOV / Revenue per Conversion | Average revenue per conversion | `Revenue / Σ conversions` | any | DAX `Revenue per Conversion`, SQL `aov` | 499.38 |
| Revenue per Click (RPC) | Revenue per click | `Revenue / Σ clicks` | any | DAX `Revenue per Click`, `RPC` | 109.75 |
| Revenue per Lead | Revenue per lead | `Revenue / Σ leads` | any | DAX `Revenue per Lead` | 274.60 |
| Media Spend Share | Spend as share of revenue | `Spend / Revenue` | any | DAX `Media Spend Share` | 34.0% |
| Revenue % of Total | Share of revenue across segments | `Revenue / Revenue(ALL segments)` | segment | DAX `Revenue % of Total` | — |
| Attributed channel revenue | Revenue per channel, equal split across a campaign's channels | `Σ revenue / n_channels` | campaign × channel | SQL `06_channel_attribution.sql` | sums to total revenue |

## Time intelligence (DAX, `Date` table + `Time Intelligence` calculation group)

`Revenue MTD / QTD / YTD`, `Revenue MoM` and `MoM %`, `Rolling 30D / 90D / 12M Revenue`; calculation items
Current, MTD, QTD, YTD, Prior Month, MoM %, Rolling 3M. `Date` is a calculated `CALENDAR(MIN(date), MAX(date))` table.
**Limitation:** the data spans 2024-07-01 to 2025-06-24, so `Revenue YoY` / `YoY %` return blank, and June 2025 is partial.

## Model KPIs (campaign under-performance)

| KPI | Definition | Formula | Grain | Source | Current value |
|---|---|---|---|---|---|
| Under-performance rate (`Churn Rate` in DAX) | Share of campaigns with ROI below the train-period P25 | `Σ churn / COUNT` | campaign | DAX `Churn Rate`, `churn_predictions.churn` | 24.8% |
| Predicted risk rate | Share flagged as riskiest 25% | `Σ Churn_Prediction / COUNT` | campaign | DAX `Predicted Churn Rate` | 25.0% |
| Test ROC-AUC | Ranking quality on the time-based hold-out | sklearn `roc_auc_score` | test set | `reports/model/evaluation.json` | 0.4996 |
| Test precision / recall / F1 | At the 25% flag cut-off | sklearn | test set | `reports/model/evaluation.json` | 0.2442 / 0.2389 / 0.2415 |

The DAX names still say "churn" because the report visuals reference them; the meaning is campaign under-performance.

## Data-quality and experiment KPIs (DAX)

| KPI | Formula | Source table |
|---|---|---|
| DQ Checks / Passed / Failed / Warnings | row counts of `dq_results` by `status` | `dq_results` |
| DQ Critical Failed | `status = "FAIL"` and `severity = "critical"` | `dq_results` |
| DQ Pass Rate | `DQ Passed / DQ Checks` (currently 63/65 = 96.9%, 2 warnings, 0 failures) | `dq_results` |
| DQ Banner | "DATA CERTIFIED" when `DQ Critical Failed = 0` | `dq_results` |
| Experiments Run / Shipped / Ship Rate / Invalid Tests | counts of `experiment_decisions` by `decision` | `experiment_decisions` (**simulated**) |
| Primary Lift, CI Low/High | average of the per-experiment values | `experiment_decisions` (**simulated**) |

## Segment value metrics (illustrative — no customer grain)

Computed per `customer_segment` (5 rows) in `src/segment_value.py`. **These are not customer RFM or customer lifetime value.**

| Metric | Formula | Caveat |
|---|---|---|
| Recency | days between the segment's last campaign and the last date in the data | 0 for every segment |
| Frequency | campaigns per segment | 33,071–33,557 (1.5% spread) |
| Monetary | revenue per segment | 16.89B–17.24B (2.1% spread) |
| F_Score / M_Score | quintile (1–5) of the 5 segment values | ranks near-identical values |
| RFM_Score / Segment | R(=3) + F + M; ≥11 High, ≥8 Medium, else Low | label = rank order, not value |
| AOV | segment revenue / conversions | the only sound figure; ≈ 499 for all segments |
| CLV_simple | segment revenue | identical to revenue |
| CLV_aov | AOV × campaign count | mixed grain |
| Retention_Rate | avg engagement / max avg engagement, clipped 0.10–0.95 | engagement proxy, not retention; 0.95 for every segment after clipping |
| CLV_discounted | AOV × count × r / (1 + 0.10 − r) | driven by the assumed r (see notebook 04 sensitivity table) |

## Measures in the model that do not reconcile (known issues, not yet changed)

These legacy KPI definitions were identified during validation and are not used as headline project findings (the
README results come from `src/data_quality/kpis.py` and `sql/campaign/01_kpi_summary.sql`). They are still in the
semantic model and are documented here rather than edited, because the report has
uncommitted visual changes and DAX edits cannot be validated outside Power BI Desktop.

| Measure | Current DAX | Problem | Correct alternative |
|---|---|---|---|
| `Avg CPA` | `AVERAGE(acquisition_cost)` | unweighted mean of per-conversion cost = **376.09**, vs true CPA 169.83 | use `CPA` |
| `Avg CTR`, `Avg CVR`, `Avg RPC`, `Avg CPC`, `Avg CPL`, `Avg ROI` | `AVERAGEX` of row-level ratios | unweighted; `Avg ROI` = 2.69 vs true ROI 1.94 | use the ratio-of-sums measures |
| `CLV Uplift` | `[M_Monetary]` = `SUM(conversions)` | a count presented as money | remove |
| `Churn Loss`, `Lifetime Loss`, `Churn‑Adjusted Profit` | built on `CLV Uplift` / `CLV_discounted` | inherit the problems above | remove or relabel as illustrative |
| `M_Monetary` (DAX RFM) | `SUM(conversions)` | Python RFM uses revenue for Monetary | align to `[Total Revenue]` |
| `Revenue YoY`, `Revenue YoY %` | `SAMEPERIODLASTYEAR` | < 12 months of data, always blank | hide |
| `Churned Customer` | `SUM(Churn_Prediction)` | counts campaigns, not customers | rename |
| `Measure 3` (Date table) | empty | unused | delete |
