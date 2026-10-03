# Data Quality Checks

Two independent layers check the same data. Both run in CI (`.github/workflows/quality.yml`) and locally (`run_quality.ps1`).

| Layer | Run | Rules | Output | Current result |
|---|---|---|---|---|
| Python framework | `python -m src.data_quality.runner --config config/dq_rules.yml` | 65 checks in `config/dq_rules.yml`, logic in `src/data_quality/checks.py` | `reports/dq/dq_results.csv` (feeds the Power BI *Data Quality* page), `dq_summary.csv`, `dq_report.md` | **63 pass · 2 warn · 0 fail** |
| SQL (DuckDB) | `python -m src.sql_runner` | 10 queries in `sql/data_quality/` | `reports/sql/sql_dq_results.csv`, `kpi_reconciliation.csv` | **10 pass · 0 fail** |

Both exit with code 1 on a blocking failure, so they can gate a CI build or a scheduled refresh.
Severity in the Python layer: `critical` blocks publish, `high` fix before release, `warning` informational.

## 1. Python framework (65 checks)

| # | Layer | IDs | What is checked | Result |
|---|---|---|---|---|
| 1 | Duplicate records | DQ001–003 | `campaign_id` unique in raw union and processed fact; no full-row duplicates ignoring the ID | pass |
| 2 | Null checks | DQ004–015 | 12 required columns 0% null, including `platform` (brand) | pass |
| | Accepted values | DQ016 | `campaign_type` ∈ {Email, Influencer, Paid Ads, SEO, Social Media} | pass |
| 3 | Referential integrity | DQ017–019 | predictions → fact on `campaign_id`; fact → `rfm_segments` / `clv_segments` on segment | pass |
| 4 | Date validity | DQ020–023 | raw parses as `%d-%m-%Y`, processed as ISO; all dates in [2024-01-01, today] | pass |
| 5 | Negative / invalid values | DQ024–030 | 7 measures ≥ 0 | pass |
| | Funnel rules | DQ031–033 | clicks ≤ impressions, leads ≤ clicks, conversions ≤ leads | pass |
| | Range rules | DQ034–035 | revenue per conversion in [50, 5,000]; engagement in [0, 100] (warnings) | pass |
| 6 | Duplicate joins | DQ036–038 | "one"-side keys unique (segment tables, predictions) | pass |
| | Cardinality | DQ039 | `channel_used` ≤ 10 distinct values | **warn: 156** — multi-valued field; handled by the equal-split bridge in `sql/campaign/06_channel_attribution.sql` |
| 7 | Row multiplication | DQ040–043 | raw = processed = predictions row counts; left joins to segment/prediction tables keep row count | pass |
| 8 | KPI reconciliation | DQ044–049 | rows, revenue, spend, conversions, clicks, impressions: raw = processed (0% tolerance) | pass |
| | Formula check | DQ050 | stored ROI = (revenue − cost × conversions) / (cost × conversions) — proves cost is per conversion | pass |
| | Label sanity | DQ051 | model label minority class ≥ 5% (caught the old 99.98%-positive churn label) | pass |
| | Column consistency | DQ052 | `target_audience` = `customer_segment` on ≥ 95% of rows | **warn: 80.1% mismatch** — source data issue, documented as a limitation |
| 9 | Source-to-report | DQ053–065 | 13 Power BI KPIs (exported with `powerbi/dq/kpi_snapshot.dax`) vs the same KPIs recomputed from **raw** files, ±0.5% | pass |

The source-to-report layer is what caught the original dashboard errors (ROI shown as 136,543% instead of 194%, spend
understated about 460×, impressions overstated). See `docs/PROJECT_AUDIT.md`.

## 2. SQL checks (DuckDB, 10 checks)

| ID | Check | Mirrors |
|---|---|---|
| SQL-DQ01 | `campaign_id` unique in raw, processed and predictions | DQ001, DQ003, DQ038 |
| SQL-DQ02 | required fields not null | DQ004–015 |
| SQL-DQ03 | funnel order and non-negative measures | DQ024–033 |
| SQL-DQ04 | raw dates parse as dd-mm-yyyy and are in range | DQ020–021 |
| SQL-DQ05 | raw ROI matches the per-conversion cost formula (tolerance max(0.01, 0.1%)) | DQ050 |
| SQL-DQ06 | **revenue reconciliation** — rows, revenue, conversions, spend equal between raw and processed, per platform | DQ044–049 (adds the per-platform split) |
| SQL-DQ07 | referential integrity | DQ017–019 |
| SQL-DQ08 | joining the fact to segment tables does not multiply rows | DQ042 |
| SQL-DQ09 | **SQL ↔ Python ↔ Power BI KPI reconciliation** (12 KPIs, ±0.5%) | DQ053–065 (adds the SQL layer) |
| SQL-DQ10 | raw schema has exactly the 16 expected columns + platform (schema drift) | new |

## 3. Profiling (informational, not a gate)

`sql/campaign/09_outlier_profile.sql` → `reports/sql/09_outlier_profile.csv` (Tukey IQR fences):

| Metric | Outlier share | Note |
|---|---:|---|
| acquisition_cost | 8.7% | long right tail (max 15,473 vs median 209) |
| roi | 7.4% | max 79.3x; rows are kept because the ROI formula reconciles |
| revenue | 5.6% | |
| conversions | 4.3% | |
| spend per campaign | 0.0% | bounded between ~50,000 and ~300,000 — consistent with generated data |
| engagement_score | 0.0% | bounded 2.56–30.99 |

## 4. Coverage against common checks

| Check | Status |
|---|---|
| Null checks | ✅ DQ004–015, SQL-DQ02 |
| Duplicate checks | ✅ DQ001–003, SQL-DQ01 |
| Primary-key uniqueness | ✅ DQ001, DQ003, DQ036–038 |
| Referential integrity | ✅ DQ017–019, SQL-DQ07 |
| Invalid dates | ✅ DQ020–023, SQL-DQ04 |
| Negative / invalid numeric values | ✅ DQ024–035, SQL-DQ03 |
| Outlier checks | ✅ profiling only (section 3) — not a blocking rule |
| Revenue reconciliation | ✅ DQ044–049, SQL-DQ06 |
| Customer / order consistency | ➖ not applicable — no customer or order fields in the data |
| SQL-to-Power BI KPI reconciliation | ✅ DQ053–065, SQL-DQ09 |
| Schema drift | ✅ SQL-DQ10 |

## 5. Known gaps (future improvements)

* **The Power BI snapshot is a manual export.** `reports/dq/powerbi_kpi_snapshot.csv` is produced by running
  `powerbi/dq/kpi_snapshot.dax` in DAX query view / DAX Studio. If the model changes and the snapshot is not
  re-exported, DQ053–065 and SQL-DQ09 compare against stale numbers. Automating this needs the Power BI REST API
  (`executeQueries`) on a published dataset.
* **No freshness check.** The data is static; a production pipeline would alert when the latest `date` is older than expected.
* **Only headline KPIs are reconciled to Power BI.** Measures listed under "do not reconcile" in
  `docs/kpi_definitions.md` (e.g. `Avg CPA`, `CLV Uplift`) are not covered.
* **Outliers are profiled, not adjudicated.** No business rule says what ROI or cost is implausible, so nothing is excluded.
* **Category labels:** DQ016 (accepted values) is reported under "Null checks" and DQ052 under "Source-to-report" in
  `dq_results.csv`; the IDs and rules are correct, the category is cosmetic.
