"""
Single source of truth for KPI definitions.

These are the *expected* values every other layer (processed CSVs, Power BI
measures) must reconcile to. Definitions are written once here and documented
in docs/PROJECT_AUDIT.md.

Important grain note: `acquisition_cost` in the source is a cost PER CONVERSION
(proven by the source ROI column = (revenue - cost*conversions) / (cost*conversions)).
Spend therefore = acquisition_cost * conversions, NOT SUM(acquisition_cost).
"""
from __future__ import annotations

import pandas as pd


def spend(df: pd.DataFrame) -> pd.Series:
    return df["acquisition_cost"] * df["conversions"]


def compute_kpis(df: pd.DataFrame) -> dict[str, float]:
    s = float(spend(df).sum())
    rev = float(df["revenue"].sum())
    imp = float(df["impressions"].sum())
    clk = float(df["clicks"].sum())
    lead = float(df["leads"].sum())
    conv = float(df["conversions"].sum())
    return {
        "campaign_rows": float(len(df)),
        "total_revenue": rev,
        "total_spend": s,
        "roi": (rev - s) / s,
        "roas": rev / s,
        "total_impressions": imp,
        "total_clicks": clk,
        "total_leads": lead,
        "total_conversions": conv,
        "ctr": clk / imp,
        "avg_ctr": clk / imp,          # ratio of sums - the only additive-safe "average"
        "conversion_rate": conv / clk,
        "cpa": s / conv,
        "cpl": s / lead,
        "net_profit": rev - s,         # contribution after media spend (no COGS in source)
    }


def roi_row_formula(df: pd.DataFrame) -> pd.Series:
    sp = spend(df)
    return (df["revenue"] - sp) / sp
