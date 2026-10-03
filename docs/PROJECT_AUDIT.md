# Project Audit — ecommerce-customer-analytics

Audit date: 2026-10-02 · Scope: GitHub repo + live Power BI model (`Ecommerce_Analytics.pbix`, 9 tables, 6 relationships, 100 measures) · Method: every KPI re-computed from the raw CSVs and compared against DAX query results from the open model.

## TL;DR

The dashboard looks polished, but **the headline numbers are wrong** and several "insights" are not supported by the data. A hiring manager who opens the PBIX and checks one number (ROI = 136,543%) will stop reading. The fix is mostly small DAX changes, plus two capability layers this project was missing: a **data-quality framework** and **experiment decision-making**. Both are now built (see bottom).

| Severity | # | Examples |
|---|---|---|
| Critical — wrong numbers on the dashboard | 6 | ROI, Spend, CPA, Impressions, Avg CTR, Net Profit, Performance Score |
| High — analytically invalid method | 5 | Churn label, RFM on 5 rows, CLV, no brand dimension, `TODAY()` recency |
| Medium — model and repo hygiene | 9 | Bi-directional joins, duplicate DAX exports, empty files, SQL for a schema that doesn't exist |

---

## 1. Critical: wrong KPIs (verified on the live model)

| KPI | Dashboard shows | Correct value | Root cause |
|---|---|---|---|
| **Total Spend** | Rs.62.7M | **Rs.29.13B** | `acquisition_cost` is a **per-conversion** cost (the source `ROI` column = (rev − cost×conv)/(cost×conv) to within rounding on all 166,665 rows). `SUM(acquisition_cost)` adds up unit prices. |
| **ROI** | **136,543%** | **194.0%** | follows from Spend |
| **ROAS** | 1,366x | **2.94x** | follows from Spend |
| **CPA** | Rs.0.37 | **Rs.169.83** | follows from Spend |
| **Total Impressions** | 16.67B | **9.18B** | `SUMX(VALUES(id), MAX(impressions))`: `MAX` inside an iterator with no `CALCULATE` returns the max of the whole filter context (100,000) for every id → 166,665 × 100,000. |
| **Avg CTR / CVR / CPC / CPL / CPA / RPC** | e.g. Avg CTR 14.9% | 8.5% | same missing context-transition bug |
| **Net Profit** (waterfall) | Rs.85.65B (> revenue!) | **Rs.56.52B** contribution after media | formula is `Revenue + CLV Uplift − Churn Loss`; spend never subtracted. "CLV Uplift" = `[M_Monetary]` = total conversions (a count) shown as money. |
| **Performance Score** | ~11,000 for every type, all "High" | 0–100 index | normalisers (0.015, 0.025, 0.8, 0.5) are arbitrary constants on the buggy averages above |

Fixed DAX for all of these (validated against the model): `powerbi/measures/_Fixes_and_DQ/Corrected_Measures.dax`.

## 2. High: analytically invalid methods

1. **Churn model is label leakage, not prediction.** `churn = engagement_score < 30 OR Conversion_Rate < 0.02 OR frequency <= 2`. Engagement maxes at 30.9, so **99.98% of rows are "churned"** (36 non-churn rows). The model is then trained on the same columns that define the label → 99.996% "accuracy" is a tautology. `frequency` is a constant per segment (row count). There is also no customer — the grain is a campaign. → Either drop churn, or reframe as a **campaign-underperformance classifier** (target = ROI below P25, features known *before* launch: type, channel, audience, language, duration; time-based train/test split).
2. **RFM on 5 rows.** RFM is computed per `customer_segment` (5 groups), `R_Score` hard-coded to 3, `qcut` into 5 bins on 5 values. The resulting "High/Low Value" labels are just the rank order of 5 near-identical totals. → Remove RFM, or rename to "Segment value ranking" and be honest that there is no customer grain.
3. **CLV is not CLV.** "Retention rate" = avg engagement ÷ max engagement, clipped to 0.95; `CLV_simple` = total segment revenue. → Remove, or present as an illustrative formula with stated assumptions.
4. **The brand dimension was dropped.** The README promises Nykaa vs Purplle vs Tira, but `platform` was added in the notebook and is **not in `campaign_data_cleaned.csv` or the model**. Only the `campaign_id` prefix (NY-/PU-/TI-) remains. → Re-export with `platform`, add a `dim_platform`.
5. **`Recency` uses `TODAY()`.** Every number changes daily; refreshes are not reproducible. → Anchor to `MAX(date)` in the data.

### Something to say in interviews: the data has almost no signal
Campaign-level ROI does not differ by campaign type (ANOVA p = 0.35), segment (p = 0.48) or language (p = 0.16). Every segment averages Rs.~514K revenue and 2.7 ROI, and `target_audience` disagrees with `customer_segment` on 80% of rows. Pooled-click CVR differences come out "significant" (p≈0) only because clicks are summed into the millions. The real gap is 0.2193 vs 0.2203. **Statistically significant, practically meaningless.** Lean into this on the dashboard: an analyst who says *"there is no winning channel here, and here's the proof"* comes across better than a dashboard that ranks noise.

## 3. Medium: model and repo hygiene

| Area | Finding | Fix |
|---|---|---|
| Relationships | `rfm_segments ↔ clv_segments` 1:1 **bi-directional**; `churn_predictions → Date` bi-directional; inactive 1:1 `churn_predictions ↔ campaign_data` | Single-direction star; fold churn columns into the fact (it's the same 166,665 rows duplicated) |
| Star schema | README claims a star schema; model is 4 wide flat tables | Build `dim_campaign_type`, `dim_channel`, `dim_segment`, `dim_platform`, `dim_language`, `Date` |
| Multi-valued channel | `channel_used` has 156 values like "WhatsApp, YouTube" | Bridge table `campaign_channel` (split) + documented attribution rule |
| Measures | 100 measures, many duplicates (CPA / Avg CPA / Cost per Conversion; ROAS / Marketing ROI), `Measure 3` empty, unformatted, no descriptions | Consolidate to ~40, add format strings + descriptions |
| Display folders | `_Channel` folder contains churn & accuracy measures | Re-folder |
| DAX exports | `Executive_Overview.dax`, `RFM_Analysis.dax`, `Churn_Retention.dax`, `Profitability.dax` are **byte-identical** | Keep one export or switch to PBIP/TMDL |
| Version control | 39 MB PBIX + 37 MB CSVs + 1.3 MB pickle in git | Save as **PBIP** (TMDL diffs), `.gitignore` large data, Git LFS if needed |
| Empty files | `src/*.py`, `requirements.txt`, `LICENSE`, `.gitignore`, `reports/business_report.pdf` are 0 bytes | Filled or removed in this branch |
| SQL | Scripts query `orders`, `customers`, `order_items` tables that don't exist in this dataset | Rewrite against the campaign data (or DuckDB / dbt — you already have a `profiles.yml`) |
| README | Missing `models/star_schema.png`; `git clone yourusername`; location says Abu Dhabi | Update |

---

## 4. Added: data-quality framework (`src/data_quality/`)

Config-driven (`config/dq_rules.yml`). 65 checks across 9 layers. Writes `reports/dq/dq_results.csv`, which feeds a Power BI **Data Quality** page. Exits non-zero on critical failures so it can gate CI or a refresh.

```
Data Quality Checks                       current result
├── Duplicate records                     3 pass
├── Null checks (+ accepted values)       12 pass · 1 FAIL  (platform column missing)
├── Referential integrity                 3 pass
├── Date validity                         4 pass
├── Negative values (+ funnel rules)      12 pass
├── Duplicate joins (+ cardinality)       3 pass · 1 warn  (channel_used 156 values)
├── Unexpected row multiplication         4 pass
├── KPI reconciliation (+ label sanity)   7 pass · 1 FAIL  (churn 99.98%)
└── Source-to-report validation           6 pass · 1 warn · 7 FAIL  (Spend, ROI, ROAS, Impressions, Avg CTR, CPA, Net Profit)
```

Source-to-report works like this: `powerbi/dq/kpi_snapshot.dax` exports the dashboard's KPIs → the runner recomputes each KPI from **raw** CSVs using one definition file (`src/data_quality/kpis.py`) → compares within ±0.5%. It caught every bug in section 1 automatically.

## 5. Added: experiment decision-making (`src/experimentation/`)

The campaign files contain **no randomised experiment**, so comparing campaign types is observational, not an A/B test. To show the skill properly, the project now has:

- **Pre-registration** (`experiments/registry.yml`): hypothesis, primary metric, MDE, power, guardrails, decision rule, all fixed before data is seen
- **Design**: sample size (70,229/arm for 3.5% → +8% MDE), duration rounded to full weeks (28 days)
- **Validity**: sample-ratio-mismatch test
- **Readout**: z-test + CI on relative lift, Welch t-test, CUPED, Bayesian P(better) + expected loss
- **Guardrails**: margin, refunds, unsubscribes (BREACH / AT RISK / OK)
- **Segments**: exploratory only, Holm-adjusted
- **Deterministic decision rule** → memo per test + CSVs for a Power BI page

Four **simulated** tests (clearly labelled) show four different correct decisions:

| Test | Result | Decision | Lesson |
|---|---|---|---|
| EXP-001 Free-shipping bar | CVR +14.5% (CI +8.7%…+20.5%) | **SHIP WITH MONITORING** | refund-rate CI too wide → monitor |
| EXP-002 20% vs 10% influencer discount | CVR +10.6% significant, margin/user −28% | **DO NOT SHIP** | a conversion win can lose money (≈Rs.4.2M/yr margin avoided) |
| EXP-003 WhatsApp 2h reminder | looks like +15%… | **INVALID** | 53/47 split, SRM p=3e-126 → assignment bug, no number is trusted |
| EXP-004 First-name subject line | CI −7.4%…+2.9% | **DO NOT SHIP** | CI rules out the MDE → stop and try a bolder idea |

## 6. Prioritised roadmap

| # | Do | Effort | Why |
|---|---|---|---|
| 1 | Paste corrected DAX (Spend, ROI, Impressions, averages, profit, score) | 1 h | Removes the credibility killers |
| 2 | Re-export processed CSV with `platform`; add brand slicer | 1 h | README promise |
| 3 | Add **Data Quality** page (banner + layer matrix + failing checks) | 2 h | Shows trust engineering |
| 4 | Add **Experiment Decisions** page (decision cards, CI forest plot, guardrails) | 3 h | Shows decision-making |
| 5 | Replace churn/RFM/CLV pages with campaign-underperformance model + honest "no signal" analysis | 4–6 h | Removes leakage |
| 6 | Star schema + channel bridge, single-direction relationships, consolidate measures | 3 h | Model quality |
| 7 | Save as PBIP, GitHub Action running `pytest` + DQ runner on every push | 1 h | Engineering maturity |
| 8 | Rewrite SQL against this data in DuckDB (optionally dbt tests mirroring the DQ rules) | 3 h | SQL that actually runs |
