import duckdb
import pandas as pd

from src.feature_engineering import add_campaign_metrics
from src.segment_value import clv_by_segment, rfm_by_segment


def _campaigns():
    return pd.DataFrame({
        "campaign_id": [f"C{i}" for i in range(5)],
        "customer_segment": ["A", "B", "C", "D", "E"],
        "date": ["2025-01-01", "2025-01-02", "2025-01-03", "2025-01-04", "2025-01-05"],
        "impressions": [1000] * 5, "clicks": [100] * 5, "leads": [50] * 5,
        "conversions": [10, 20, 30, 40, 50], "revenue": [1000.0, 2000, 3000, 4000, 5000],
        "acquisition_cost": [10.0] * 5, "engagement_score": [10.0, 12, 14, 16, 18],
    })


def test_cost_metrics_use_per_conversion_grain():
    df = add_campaign_metrics(_campaigns())
    # spend = 10 * 10 = 100 for the first row -> CPL = 100 / 50 leads = 2
    assert df.loc[0, "CPL"] == 2.0 and df.loc[0, "CPCV"] == 10.0
    assert df.loc[0, "CTR"] == 0.1 and df.loc[0, "Conversion_Rate"] == 0.1


def test_rfm_by_segment_scores_and_labels():
    # qcut needs 5 distinct frequencies (true in the real data), so segment k gets k campaigns
    base = _campaigns()
    df = base.loc[base.index.repeat(base.index + 1)].reset_index(drop=True)
    df["campaign_id"] = [f"X{i}" for i in range(len(df))]
    rfm = rfm_by_segment(df)
    assert len(rfm) == 5 and (rfm["R_Score"] == 3).all()
    top = rfm.set_index("Customer_Segment").loc["E"]
    assert top["Recency"] == 0 and top["M_Score"] == 5


def test_clv_retention_proxy_is_clipped():
    clv = clv_by_segment(_campaigns())
    assert clv["Retention_Rate"].max() <= 0.95 and clv["RRetention_Rate"].max() == 1.0
    assert (clv["CLV_simple"] == clv["total_revenue"]).all()


def test_equal_split_attribution_preserves_revenue():
    con = duckdb.connect()
    con.register("campaigns", pd.DataFrame({
        "campaign_id": ["a", "b"], "channel_used": ["Email, YouTube", "Google"],
        "revenue": [300.0, 100.0], "spend": [100.0, 50.0]}))
    sql = open("sql/campaign/06_channel_attribution.sql").read()
    out = con.execute(sql).df()
    assert out["attributed_revenue_equal_split"].sum() == 400.0       # no double counting
    assert out["naive_revenue_double_counted"].sum() == 700.0         # naive explode inflates
