"""
Run the project's SQL in DuckDB (in-memory; reads the CSVs directly).

    python -m src.sql_runner

1. sql/00_create_views.sql            -> views over data/raw and data/processed
2. sql/campaign/*.sql                 -> one CSV per query in reports/sql/
3. sql/data_quality/*.sql             -> reports/sql/sql_dq_results.csv (exit 1 if any check fails)
4. KPI reconciliation                 -> SQL KPIs vs Python definitions (src/data_quality/kpis.py)
                                         vs the Power BI KPI snapshot (reports/dq/powerbi_kpi_snapshot.csv)
"""
from __future__ import annotations

import sys
from pathlib import Path

import duckdb
import pandas as pd

from src.data_quality.kpis import compute_kpis

RECONCILE = ["campaign_rows", "total_revenue", "total_spend", "roi", "roas", "total_impressions",
             "total_clicks", "total_conversions", "ctr", "conversion_rate", "cpa", "net_profit"]
TOLERANCE = 0.005   # same +-0.5% tolerance as the Python source-to-report layer


def run(root: Path = Path(".")) -> int:
    out = root / "reports/sql"
    out.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute(f"SET file_search_path = '{root.resolve().as_posix()}'")
    con.execute((root / "sql/00_create_views.sql").read_text())

    for f in sorted((root / "sql/campaign").glob("*.sql")):
        df = con.execute(f.read_text()).df()
        df.to_csv(out / f"{f.stem}.csv", index=False)
        print(f"[ok] {f.name:<40} {len(df):>4} rows")

    dq = pd.concat([con.execute(f.read_text()).df() for f in sorted((root / "sql/data_quality").glob("*.sql"))],
                   ignore_index=True)

    # KPI reconciliation: SQL vs Python vs Power BI snapshot
    sql_kpis = pd.read_csv(out / "01_kpi_summary.csv").iloc[0].to_dict()
    py_kpis = compute_kpis(pd.read_csv(root / "data/processed/campaign_data_cleaned.csv"))
    snap_path = root / "reports/dq/powerbi_kpi_snapshot.csv"
    pbi = pd.read_csv(snap_path).set_index("kpi")["value"].to_dict() if snap_path.exists() else {}
    rows = []
    for k in RECONCILE:
        s, p, b = float(sql_kpis[k]), float(py_kpis[k]), pbi.get(k)
        ok_py = abs(s - p) <= TOLERANCE * max(abs(p), 1e-12)
        ok_pbi = b is None or abs(s - float(b)) <= TOLERANCE * max(abs(float(b)), 1e-12)
        rows.append({"kpi": k, "sql": s, "python": p, "powerbi_snapshot": b,
                     "sql_vs_python_ok": ok_py, "sql_vs_powerbi_ok": ok_pbi})
    rec = pd.DataFrame(rows)
    rec.to_csv(out / "kpi_reconciliation.csv", index=False)
    dq = pd.concat([dq, pd.DataFrame([{
        "check_id": "SQL-DQ09", "check_name": "SQL KPIs reconcile to Python definitions and Power BI snapshot (+-0.5%)",
        "failing_rows": int((~rec.sql_vs_python_ok).sum() + (~rec.sql_vs_powerbi_ok).sum())}])], ignore_index=True)

    dq["failing_rows"] = dq["failing_rows"].astype(int)
    dq["status"] = dq["failing_rows"].map(lambda n: "PASS" if n == 0 else "FAIL")
    dq.to_csv(out / "sql_dq_results.csv", index=False)
    print()
    print(dq.to_string(index=False))
    if not pbi:
        print("note: Power BI snapshot not found; SQL vs Power BI comparison skipped")
    return int((dq["status"] == "FAIL").any())


if __name__ == "__main__":
    sys.exit(run())
