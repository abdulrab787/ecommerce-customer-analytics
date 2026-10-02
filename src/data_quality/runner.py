"""
Config-driven data-quality runner.

    python -m src.data_quality.runner --config config/dq_rules.yml

Outputs (in run.output_dir):
    dq_results.csv      one row per check   -> load into Power BI "Data Quality" page
    dq_summary.csv      pass/warn/fail per framework category
    dq_report.md        human-readable report for the README / PR
Exit code 1 if any check with a severity listed in run.fail_on fails
(so it can gate a CI job or a scheduled refresh).
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import yaml

from . import checks as C
from .kpis import compute_kpis, roi_row_formula

CATEGORIES = [
    "Duplicate records", "Null checks", "Referential integrity", "Date validity",
    "Negative values", "Duplicate joins", "Unexpected row multiplication",
    "KPI reconciliation", "Source-to-report validation",
]


def load_tables(cfg: dict, root: Path) -> dict[str, pd.DataFrame]:
    tables = {}
    for name, spec in cfg["tables"].items():
        if "union" in spec:
            parts = []
            for p in spec["union"]:
                d = pd.read_csv(root / p["path"])
                if "platform" in p:
                    d["platform"] = p["platform"]
                parts.append(d)
            df = pd.concat(parts, ignore_index=True)
        else:
            df = pd.read_csv(root / spec["path"])
        if spec.get("lowercase_columns"):
            df.columns = df.columns.str.lower().str.replace(" ", "_")
        tables[name] = df
    return tables


def _parse_dates(df: pd.DataFrame, col: str, fmt: str | None) -> pd.DataFrame:
    df = df.copy()
    df[col] = pd.to_datetime(df[col], format=fmt, errors="coerce")
    return df


def run_checks(cfg: dict, tables: dict[str, pd.DataFrame], root: Path) -> list[C.CheckResult]:
    R: list[C.CheckResult] = []
    T = tables
    for chk in cfg["checks"]:
        t = chk["type"]
        sev = chk.get("severity")
        kw = {"severity": sev} if sev else {}
        try:
            if t == "duplicate_records":
                R.append(C.duplicate_records(T[chk["table"]], chk["table"], chk.get("key"),
                                             chk.get("ignore_cols"), **kw))
            elif t == "null_check":
                R += C.null_check(T[chk["table"]], chk["table"], chk["columns"],
                                  chk.get("max_null_pct", 0.0), **kw)
            elif t == "accepted_values":
                R.append(C.accepted_values(T[chk["table"]], chk["table"], chk["column"], chk["values"], **kw))
            elif t == "referential_integrity":
                R.append(C.referential_integrity(T[chk["child"]], T[chk["parent"]], chk["child"],
                                                 chk["parent"], chk["child_key"], chk["parent_key"], **kw))
            elif t == "date_validity":
                R += C.date_validity(T[chk["table"]], chk["table"], chk["column"], chk.get("format"),
                                     chk.get("min_date"), chk.get("max_date"),
                                     chk.get("allow_future", False), **kw)
            elif t == "non_negative":
                R += C.non_negative(T[chk["table"]], chk["table"], chk["columns"], **kw)
            elif t == "business_rule":
                R.append(C.business_rule(T[chk["table"]], chk["table"], chk["name"], chk["expression"], **kw))
            elif t == "join_key_uniqueness":
                R.append(C.join_key_uniqueness(T[chk["table"]], chk["table"], chk["key"], **kw))
            elif t == "cardinality":
                R.append(C.cardinality(T[chk["table"]], chk["table"], chk["column"], chk["max_distinct"], **kw))
            elif t == "row_count_match":
                R.append(C.row_count_match(T[chk["a"]], T[chk["b"]], chk["a"], chk["b"],
                                           chk.get("tolerance_pct", 0.0), **kw))
            elif t == "row_multiplication":
                R.append(C.row_multiplication(T[chk["left"]], T[chk["right"]], chk["left"], chk["right"],
                                              chk["on_left"], chk["on_right"], chk.get("how", "left"),
                                              chk.get("max_ratio", 1.0), **kw))
            elif t == "kpi_reconciliation":
                ka, kb = compute_kpis(T[chk["a"]]), compute_kpis(T[chk["b"]])
                for k in ("campaign_rows", "total_revenue", "total_spend", "total_conversions",
                          "total_clicks", "total_impressions"):
                    R.append(C.kpi_reconciliation(f"{k}: {chk['a']} vs {chk['b']}", ka[k], kb[k],
                                                  chk["a"], chk["b"], chk.get("tolerance_pct", 0.0), **kw))
            elif t == "roi_formula":
                R.append(C.row_level_formula(T[chk["table"]], chk["table"], "roi", roi_row_formula,
                                             "(revenue - cost*conversions)/(cost*conversions)", abs_tol=0.01, **kw))
            elif t == "label_balance":
                R.append(C.label_balance(T[chk["table"]], chk["table"], chk["column"],
                                         chk.get("min_minority_pct", 0.05), **kw))
            elif t == "column_consistency":
                R.append(C.column_consistency(T[chk["table"]], chk["table"], chk["col_a"], chk["col_b"],
                                              chk.get("max_mismatch_pct", 0.05), **kw))
            elif t == "source_to_report":
                snap_path = root / chk["snapshot"]
                if not snap_path.exists():
                    R.append(C.CheckResult("source_to_report", "Source-to-report validation", "powerbi",
                                           "snapshot exists", "high", False, detail=f"missing {snap_path}"))
                    continue
                snap = pd.read_csv(snap_path).set_index("kpi")["value"].to_dict()
                exp = compute_kpis(T[chk["source"]])
                exp = {k: exp[k] for k in chk["kpis"]}
                R += C.source_to_report(exp, snap, chk.get("tolerance_pct", 0.005), **kw)
            else:
                raise ValueError(f"unknown check type {t}")
        except KeyError as e:   # missing table/column is itself a DQ failure
            R.append(C.CheckResult(t, "Null checks", str(chk.get("table", "")), f"{t} could run",
                                   "critical", False, detail=f"missing field/column: {e}"))
    return R


def write_outputs(results: list[C.CheckResult], out_dir: Path) -> pd.DataFrame:
    out_dir.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame([r.to_dict() for r in results])
    df.insert(0, "run_ts", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    df.insert(1, "check_id", [f"DQ{i:03d}" for i in range(1, len(df) + 1)])
    df.to_csv(out_dir / "dq_results.csv", index=False)

    summ = (df.assign(category=pd.Categorical(df["category"], CATEGORIES, ordered=True))
              .pivot_table(index="category", columns="status", values="check_id", aggfunc="count",
                           fill_value=0, observed=False)
              .reindex(columns=["PASS", "WARN", "FAIL"], fill_value=0))
    summ.to_csv(out_dir / "dq_summary.csv")

    lines = [f"# Data Quality Report\n", f"Run: {df['run_ts'].iloc[0]}  \n",
             f"**{(df.status == 'PASS').sum()} pass · {(df.status == 'WARN').sum()} warn · "
             f"{(df.status == 'FAIL').sum()} fail** out of {len(df)} checks\n",
             "\n## Summary by layer\n", "| Layer | Pass | Warn | Fail |", "|---|---|---|---|"]
    for cat, row in summ.iterrows():
        lines.append(f"| {cat} | {row['PASS']} | {row['WARN']} | {row['FAIL']} |")
    lines += ["\n## Failures and warnings\n", "| ID | Severity | Table | Rule | Observed | Expected | Detail |",
              "|---|---|---|---|---|---|---|"]
    for _, r in df[df.status != "PASS"].sort_values(["severity", "check_id"]).iterrows():
        lines.append(f"| {r.check_id} | {r.severity} | {r.table} | {r.rule} | {r.observed} | "
                     f"{r.expected} | {r.detail} |")
    (out_dir / "dq_report.md").write_text("\n".join(lines), encoding="utf-8")
    return df


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config/dq_rules.yml")
    ap.add_argument("--root", default=".")
    a = ap.parse_args(argv)
    root = Path(a.root)
    cfg = yaml.safe_load((root / a.config).read_text())
    results = run_checks(cfg, load_tables(cfg, root), root)
    df = write_outputs(results, root / cfg["run"]["output_dir"])
    blocking = df[(df.status == "FAIL") & df.severity.isin(cfg["run"].get("fail_on", ["critical"]))]
    print(df.groupby(["category", "status"]).size().unstack(fill_value=0))
    print(f"\n{len(blocking)} blocking failure(s). Report: {cfg['run']['output_dir']}/dq_report.md")
    return 1 if len(blocking) else 0


if __name__ == "__main__":
    sys.exit(main())
