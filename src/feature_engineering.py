"""
Derived campaign metrics, shared by src.preprocessing and the notebooks.

Grain note: `acquisition_cost` is a cost PER CONVERSION, so campaign spend is
acquisition_cost * conversions (see src/data_quality/kpis.py).
"""
from __future__ import annotations

import pandas as pd


def add_campaign_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Add CTR, Conversion_Rate, CPL (spend per lead) and CPCV (spend per conversion)."""
    df = df.copy()
    spend = df["acquisition_cost"] * df["conversions"]
    df["CTR"] = df["clicks"] / df["impressions"]
    df["Conversion_Rate"] = df["conversions"] / df["clicks"]
    df["CPL"] = spend / df["leads"]
    df["CPCV"] = df["acquisition_cost"]
    return df


def add_time_features(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    """Calendar month as a string category (used by the campaign-risk model)."""
    df = df.copy()
    df["month"] = pd.to_datetime(df[date_col]).dt.month.astype(str)
    return df
