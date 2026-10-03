"""
Segment value ranking (RFM-style) and illustrative segment "CLV".

    python -m src.segment_value

IMPORTANT - read before quoting these numbers:
  * The source data has NO customer or order grain. Each row is a marketing campaign.
  * Both tables are therefore computed per `customer_segment` (5 rows), not per customer.
  * They are kept because the Power BI model reads them; they are an illustrative
    ranking of 5 near-identical segments, NOT customer RFM and NOT customer lifetime value.
    See docs/kpi_definitions.md ("Segment value metrics") for the caveats.

Outputs (column names/order unchanged because Power BI depends on them):
    data/processed/rfm_segments.csv
    data/processed/clv_segments.csv
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

DISCOUNT_RATE = 0.10          # assumption carried over from notebook 04
RETENTION_CLIP = (0.1, 0.95)  # assumption carried over from notebook 04


def _segment_label(score: int) -> str:
    if score >= 11:
        return "High Value"
    if score >= 8:
        return "Medium Value"
    return "Low Value"


def rfm_by_segment(df: pd.DataFrame) -> pd.DataFrame:
    """Recency (days before the last date in the data), Frequency (campaign count),
    Monetary (revenue) per segment. R_Score is a constant 3: with every segment
    active on the last day, recency carries no information."""
    df = df.assign(date=pd.to_datetime(df["date"]))
    last = df["date"].max()
    rfm = df.groupby("customer_segment").agg(
        Recency=("date", lambda x: (last - x.max()).days),
        Frequency=("campaign_id", "count"),
        Monetary=("revenue", "sum"),
    ).reset_index().rename(columns={"customer_segment": "Customer_Segment"})
    rfm["R_Score"] = 3
    rfm["F_Score"] = pd.qcut(rfm["Frequency"], 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["M_Score"] = pd.qcut(rfm["Monetary"], 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["RFM_Score"] = rfm["R_Score"] + rfm["F_Score"] + rfm["M_Score"]
    rfm["Segment"] = rfm["RFM_Score"].apply(_segment_label)
    return rfm[["Customer_Segment", "Recency", "Frequency", "Monetary",
                "R_Score", "F_Score", "M_Score", "RFM_Score", "Segment"]]


def clv_by_segment(df: pd.DataFrame) -> pd.DataFrame:
    """Three illustrative formulas per segment:
        CLV_simple     = total segment revenue
        CLV_aov        = AOV * campaign count
        CLV_discounted = AOV * count * r / (1 + d - r)
    where r ("retention") is a PROXY = avg engagement / max avg engagement, clipped.
    No repeat-purchase data exists, so r is not a real retention rate."""
    seg = df.groupby("customer_segment").agg(
        total_revenue=("revenue", "sum"),
        total_conversions=("conversions", "sum"),
        total_leads=("leads", "sum"),
        total_clicks=("clicks", "sum"),
        total_impressions=("impressions", "sum"),
        avg_engagement=("engagement_score", "mean"),
        frequency=("campaign_id", "count"),
    ).reset_index()
    seg["CLV_simple"] = seg["total_revenue"]
    seg["AOV"] = seg["total_revenue"] / seg["total_conversions"].replace(0, np.nan)
    seg["CLV_aov"] = seg["AOV"] * seg["frequency"]
    seg["RRetention_Rate"] = seg["avg_engagement"] / seg["avg_engagement"].max()   # unclipped proxy
    seg["Retention_Rate"] = seg["RRetention_Rate"].clip(*RETENTION_CLIP)
    seg["CLV_discounted"] = (seg["AOV"] * seg["frequency"] * seg["Retention_Rate"]) / (
        1 + DISCOUNT_RATE - seg["Retention_Rate"])
    return seg


def main(root: Path = Path(".")):
    df = pd.read_csv(root / "data/processed/campaign_data_cleaned.csv")
    rfm, clv = rfm_by_segment(df), clv_by_segment(df)
    rfm.to_csv(root / "data/processed/rfm_segments.csv", index=False)
    clv.to_csv(root / "data/processed/clv_segments.csv", index=False)
    print(rfm.to_string(index=False))
    print(clv[["customer_segment", "AOV", "Retention_Rate", "CLV_discounted"]].to_string(index=False))


if __name__ == "__main__":
    main()
