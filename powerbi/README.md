# Power BI — Ecommerce Analytics

Semantic model and report for the campaign data in this repository. Project-level context, results and limitations are
in the [main README](../README.md).

## Open the report

1. Open `dashboards/Ecommerce_Analytics.pbip` in Power BI Desktop. This PBIP project (report definition in
   `Ecommerce_Analytics.Report/`, semantic model in `Ecommerce_Analytics.SemanticModel/`) is the report.
2. Set the `ProjectRoot` parameter (Transform data → Manage parameters) to your clone folder, ending with `\`.
3. Refresh. All tables load from CSVs under `data/processed/` and `reports/`.

## Contents

| Path | What it is |
|---|---|
| `dashboards/Ecommerce_Analytics.SemanticModel/` | Model in TMDL (tables, 156 measures, relationships, RLS roles, calculation group) |
| `dashboards/Ecommerce_Analytics.SemanticModel/documentation/model-documentation.md` | Generated documentation of every table, measure and role |
| `dashboards/Ecommerce_Analytics.Report/` | Report definition (PBIR) |
| `measures/` | Earlier DAX exports by display folder; `_Fixes_and_DQ/Corrected_Measures.dax` holds the corrected KPI definitions |
| `dq/kpi_snapshot.dax` | DAX query that exports headline KPIs for the source-to-report checks (DQ053–065, SQL-DQ09) |
| `EcommerceTheme.json` | Report theme |
| `assets/` | Screenshots (`v2/` is current) and the dashboard tour video |

## Pages

Executive Overview · Channel & Audience Insights · RFM Segmentation · Campaign Risk · Profitability · What-If Simulator ·
Data Quality · Experiment Decisions, plus a Campaign Detail drill-through and a KPI tooltip page.

## Notes

* RFM, "churn" and CLV visuals are built on **segment-level, illustrative** tables (the data has no customer grain), and
  "churn" means campaign under-performance. See [docs/kpi_definitions.md](../docs/kpi_definitions.md).
* Experiment pages show **simulated** data.
* Measures that do not reconcile to the KPI definitions (e.g. `Avg CPA`, `CLV Uplift`) are listed in
  [docs/kpi_definitions.md](../docs/kpi_definitions.md#measures-in-the-model-that-do-not-reconcile-known-issues-not-yet-changed).
* The model is not a full star schema yet; see [docs/architecture.md](../docs/architecture.md).
