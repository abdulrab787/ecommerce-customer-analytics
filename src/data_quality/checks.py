"""
Reusable data-quality checks.

Every check is a pure function that takes DataFrames + parameters and returns a
CheckResult. The runner (runner.py) wires them to tables via config/dq_rules.yml,
so the same checks can be reused on any dataset without code changes.

Severity:
    critical -> blocks publishing (pipeline exits non-zero)
    high     -> must be investigated before the next release
    warning  -> logged and shown on the DQ dashboard page
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Callable, Iterable

import numpy as np
import pandas as pd


@dataclass
class CheckResult:
    check: str                 # e.g. "duplicate_records"
    category: str              # one of the 9 framework layers
    table: str
    rule: str                  # human-readable rule
    severity: str              # critical | high | warning
    passed: bool
    observed: float | int | str | None = None
    expected: float | int | str | None = None
    failing_rows: int = 0
    detail: str = ""
    sample: list = field(default_factory=list)

    @property
    def status(self) -> str:
        return "PASS" if self.passed else ("FAIL" if self.severity in ("critical", "high") else "WARN")

    def to_dict(self) -> dict:
        d = asdict(self)
        d["status"] = self.status
        d["sample"] = "; ".join(map(str, self.sample[:5]))
        return d


def _sample(df: pd.DataFrame, mask: pd.Series, cols: Iterable[str] | None = None, n: int = 5) -> list:
    sub = df.loc[mask, list(cols) if cols else df.columns]
    return sub.head(n).to_dict("records")


# --------------------------------------------------------------------------- #
# 1. Duplicate records
# --------------------------------------------------------------------------- #
def duplicate_records(df: pd.DataFrame, table: str, key: list[str] | None = None,
                      ignore_cols: list[str] | None = None, severity: str = "critical") -> CheckResult:
    """Primary-key uniqueness (if key given) or full-row duplicates (excluding ignore_cols)."""
    if key:
        mask = df.duplicated(subset=key, keep=False)
        rule = f"{key} is unique"
    else:
        cols = [c for c in df.columns if c not in (ignore_cols or [])]
        mask = df.duplicated(subset=cols, keep=False)
        rule = f"no full-row duplicates (ignoring {ignore_cols or []})"
    n = int(mask.sum())
    return CheckResult("duplicate_records", "Duplicate records", table, rule, severity,
                       n == 0, observed=n, expected=0, failing_rows=n,
                       sample=_sample(df, mask, key) if n else [])


# --------------------------------------------------------------------------- #
# 2. Null checks
# --------------------------------------------------------------------------- #
def null_check(df: pd.DataFrame, table: str, columns: list[str], max_null_pct: float = 0.0,
               severity: str = "critical") -> list[CheckResult]:
    out = []
    for c in columns:
        if c not in df.columns:
            out.append(CheckResult("null_check", "Null checks", table, f"column '{c}' exists",
                                   "critical", False, detail="column missing from table"))
            continue
        mask = df[c].isna() | (df[c].astype(str).str.strip() == "")
        pct = float(mask.mean())
        out.append(CheckResult("null_check", "Null checks", table,
                               f"{c} null% <= {max_null_pct:.2%}", severity, pct <= max_null_pct,
                               observed=round(pct, 6), expected=max_null_pct,
                               failing_rows=int(mask.sum())))
    return out


# --------------------------------------------------------------------------- #
# 3. Referential integrity
# --------------------------------------------------------------------------- #
def referential_integrity(child: pd.DataFrame, parent: pd.DataFrame, child_table: str,
                          parent_table: str, child_key: str, parent_key: str,
                          severity: str = "critical") -> CheckResult:
    """Every child key must exist in the parent (no orphans -> no '(Blank)' rows in Power BI)."""
    orphans = ~child[child_key].isin(parent[parent_key])
    n = int(orphans.sum())
    return CheckResult("referential_integrity", "Referential integrity", child_table,
                       f"{child_table}.{child_key} -> {parent_table}.{parent_key}", severity,
                       n == 0, observed=n, expected=0, failing_rows=n,
                       sample=child.loc[orphans, child_key].drop_duplicates().head(5).tolist())


# --------------------------------------------------------------------------- #
# 4. Date validity
# --------------------------------------------------------------------------- #
def date_validity(df: pd.DataFrame, table: str, column: str, fmt: str | None = None,
                  min_date: str | None = None, max_date: str | None = None,
                  allow_future: bool = False, severity: str = "critical") -> list[CheckResult]:
    parsed = pd.to_datetime(df[column], format=fmt, errors="coerce")
    unparsable = parsed.isna() & df[column].notna()
    res = [CheckResult("date_validity", "Date validity", table, f"{column} parses as {fmt or 'ISO'}",
                       severity, not unparsable.any(), observed=int(unparsable.sum()), expected=0,
                       failing_rows=int(unparsable.sum()),
                       sample=df.loc[unparsable, column].head(5).tolist())]
    lo = pd.Timestamp(min_date) if min_date else pd.Timestamp.min
    hi = pd.Timestamp(max_date) if max_date else pd.Timestamp.max
    if not allow_future:
        hi = min(hi, pd.Timestamp.today().normalize())
    out_of_range = parsed.notna() & ((parsed < lo) | (parsed > hi))
    res.append(CheckResult("date_validity", "Date validity", table,
                           f"{column} within [{min_date or '-inf'}, {max_date or 'today'}]", severity,
                           not out_of_range.any(), observed=int(out_of_range.sum()), expected=0,
                           failing_rows=int(out_of_range.sum()),
                           detail=f"observed range {parsed.min()} .. {parsed.max()}"))
    return res


# --------------------------------------------------------------------------- #
# 5. Negative values / numeric domain
# --------------------------------------------------------------------------- #
def non_negative(df: pd.DataFrame, table: str, columns: list[str], severity: str = "critical") -> list[CheckResult]:
    out = []
    for c in columns:
        mask = pd.to_numeric(df[c], errors="coerce") < 0
        out.append(CheckResult("negative_values", "Negative values", table, f"{c} >= 0", severity,
                               not mask.any(), observed=int(mask.sum()), expected=0,
                               failing_rows=int(mask.sum()), sample=df.loc[mask, c].head(5).tolist()))
    return out


def business_rule(df: pd.DataFrame, table: str, name: str, expression: str,
                  severity: str = "critical") -> CheckResult:
    """Row-level rule expressed as a pandas query that must be TRUE for every row,
    e.g. 'clicks <= impressions' (funnel monotonicity)."""
    ok = df.eval(expression)
    bad = ~ok.fillna(False)
    return CheckResult("business_rule", "Negative values", table, f"{name}: {expression}", severity,
                       not bad.any(), observed=int(bad.sum()), expected=0, failing_rows=int(bad.sum()),
                       sample=_sample(df, bad))


def accepted_values(df: pd.DataFrame, table: str, column: str, values: list,
                    severity: str = "high") -> CheckResult:
    bad = ~df[column].isin(values)
    return CheckResult("accepted_values", "Null checks", table, f"{column} in {values}", severity,
                       not bad.any(), observed=int(bad.sum()), expected=0, failing_rows=int(bad.sum()),
                       sample=df.loc[bad, column].drop_duplicates().head(5).tolist())


def column_consistency(df: pd.DataFrame, table: str, col_a: str, col_b: str,
                       max_mismatch_pct: float = 0.05, severity: str = "warning") -> CheckResult:
    """Two columns that should describe the same thing (e.g. target_audience vs customer_segment)."""
    mism = df[col_a] != df[col_b]
    pct = float(mism.mean())
    return CheckResult("column_consistency", "Source-to-report validation", table,
                       f"{col_a} == {col_b} (mismatch <= {max_mismatch_pct:.0%})", severity,
                       pct <= max_mismatch_pct, observed=round(pct, 4), expected=max_mismatch_pct,
                       failing_rows=int(mism.sum()))


# --------------------------------------------------------------------------- #
# 6. Duplicate joins  (dimension key not unique -> fan-out)
# --------------------------------------------------------------------------- #
def join_key_uniqueness(dim: pd.DataFrame, table: str, key: str, severity: str = "critical") -> CheckResult:
    dup = dim[key].duplicated(keep=False)
    return CheckResult("duplicate_joins", "Duplicate joins", table,
                       f"'one' side key {table}.{key} is unique", severity, not dup.any(),
                       observed=int(dup.sum()), expected=0, failing_rows=int(dup.sum()),
                       sample=dim.loc[dup, key].drop_duplicates().head(5).tolist())


# --------------------------------------------------------------------------- #
# 7. Unexpected row multiplication
# --------------------------------------------------------------------------- #
def row_multiplication(left: pd.DataFrame, right: pd.DataFrame, left_table: str, right_table: str,
                       on_left: str, on_right: str, how: str = "left",
                       max_ratio: float = 1.0, severity: str = "critical") -> CheckResult:
    merged = left.merge(right, left_on=on_left, right_on=on_right, how=how)
    ratio = len(merged) / max(len(left), 1)
    return CheckResult("row_multiplication", "Unexpected row multiplication", left_table,
                       f"{how} join {left_table}->{right_table} on {on_left} keeps rows (ratio <= {max_ratio})",
                       severity, ratio <= max_ratio + 1e-12, observed=round(ratio, 4), expected=max_ratio,
                       failing_rows=len(merged) - len(left),
                       detail=f"{len(left):,} rows before, {len(merged):,} after")


def row_count_match(a: pd.DataFrame, b: pd.DataFrame, a_name: str, b_name: str,
                    tolerance_pct: float = 0.0, severity: str = "critical") -> CheckResult:
    diff = abs(len(a) - len(b)) / max(len(a), 1)
    return CheckResult("row_multiplication", "Unexpected row multiplication", b_name,
                       f"row count {b_name} == {a_name} (±{tolerance_pct:.1%})", severity,
                       diff <= tolerance_pct, observed=len(b), expected=len(a),
                       failing_rows=abs(len(a) - len(b)))


# --------------------------------------------------------------------------- #
# 8. KPI reconciliation  (same KPI computed two independent ways)
# --------------------------------------------------------------------------- #
def kpi_reconciliation(name: str, value_a: float, value_b: float, label_a: str, label_b: str,
                       tolerance_pct: float = 0.001, severity: str = "critical") -> CheckResult:
    denom = abs(value_a) if value_a else 1.0
    diff = abs(value_a - value_b) / denom
    return CheckResult("kpi_reconciliation", "KPI reconciliation", name,
                       f"{label_a} == {label_b} (±{tolerance_pct:.2%})", severity,
                       diff <= tolerance_pct, observed=_fmt(value_b), expected=_fmt(value_a),
                       detail=f"relative diff {diff:.4%}")


def row_level_formula(df: pd.DataFrame, table: str, column: str, formula: Callable[[pd.DataFrame], pd.Series],
                      formula_text: str, abs_tol: float = 0.01, rel_tol: float = 0.001,
                      severity: str = "high") -> CheckResult:
    """Stored derived column must equal its definition (e.g. roi = (rev - cost*conv)/(cost*conv))."""
    recomputed = formula(df)
    # stored inputs are rounded to 2dp, so allow abs OR relative tolerance
    bad = (df[column] - recomputed).abs() > (recomputed.abs() * rel_tol).clip(lower=abs_tol)
    return CheckResult("kpi_reconciliation", "KPI reconciliation", table, f"{column} == {formula_text}",
                       severity, not bad.any(), observed=int(bad.sum()), expected=0,
                       failing_rows=int(bad.sum()))


# --------------------------------------------------------------------------- #
# 9. Source-to-report validation
# --------------------------------------------------------------------------- #
def source_to_report(expected: dict[str, float], reported: dict[str, float],
                     tolerance_pct: float = 0.005, severity: str = "critical") -> list[CheckResult]:
    """Compare KPIs exported from the Power BI model with KPIs recomputed from source."""
    out = []
    for kpi, exp in expected.items():
        if kpi not in reported:
            out.append(CheckResult("source_to_report", "Source-to-report validation", "powerbi",
                                   f"{kpi} present in report snapshot", "high", False,
                                   detail="KPI missing from snapshot"))
            continue
        rep = float(reported[kpi])
        diff = abs(rep - exp) / (abs(exp) if exp else 1.0)
        out.append(CheckResult("source_to_report", "Source-to-report validation", "powerbi",
                               f"Power BI [{kpi}] == source (±{tolerance_pct:.1%})", severity,
                               diff <= tolerance_pct, observed=_fmt(rep), expected=_fmt(exp),
                               detail=f"relative diff {diff:.2%}"))
    return out


# --------------------------------------------------------------------------- #
# Extra: target / label sanity for ML outputs
# --------------------------------------------------------------------------- #
def label_balance(df: pd.DataFrame, table: str, column: str, min_minority_pct: float = 0.05,
                  severity: str = "high") -> CheckResult:
    share = df[column].value_counts(normalize=True)
    minority = float(share.min()) if len(share) > 1 else 0.0
    return CheckResult("label_balance", "KPI reconciliation", table,
                       f"{column} minority class >= {min_minority_pct:.0%}", severity,
                       minority >= min_minority_pct, observed=round(minority, 6), expected=min_minority_pct,
                       detail=f"class shares {share.round(5).to_dict()}")


def cardinality(df: pd.DataFrame, table: str, column: str, max_distinct: int,
                severity: str = "warning") -> CheckResult:
    n = int(df[column].nunique())
    return CheckResult("cardinality", "Duplicate joins", table, f"{column} distinct <= {max_distinct}",
                       severity, n <= max_distinct, observed=n, expected=max_distinct,
                       detail="multi-valued attribute? split into a bridge table")


def _fmt(x):
    try:
        return float(np.round(float(x), 6))
    except Exception:  # noqa: BLE001
        return x
