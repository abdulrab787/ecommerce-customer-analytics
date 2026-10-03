"""
Build data/processed/campaign_data_cleaned.csv from the three raw brand files.

    python -m src.preprocessing

Fixes vs. the original notebook export:
  * keeps the `platform` (brand) column  -> DQ015
  * cost metrics use the correct grain: acquisition_cost is a cost PER CONVERSION
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.feature_engineering import add_campaign_metrics

RAW = {"Nykaa": "nykaa", "Purplle": "purplle", "Tira": "tira"}
COLS = ["campaign_id", "campaign_type", "target_audience", "duration", "channel_used", "impressions",
        "clicks", "leads", "conversions", "revenue", "acquisition_cost", "roi", "language",
        "engagement_score", "customer_segment", "date", "CTR", "Conversion_Rate", "CPL", "CPCV", "platform"]


def build(root: Path = Path(".")) -> pd.DataFrame:
    parts = []
    for platform, stem in RAW.items():
        d = pd.read_csv(root / f"data/raw/{stem}_campaign_data.csv")
        d.columns = d.columns.str.lower().str.replace(" ", "_")
        d["platform"] = platform
        parts.append(d)
    df = pd.concat(parts, ignore_index=True)
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y").dt.date
    df = add_campaign_metrics(df)
    return df[COLS]


if __name__ == "__main__":
    out = build()
    out.to_csv("data/processed/campaign_data_cleaned.csv", index=False)
    print(out.shape, out["platform"].value_counts().to_dict())
