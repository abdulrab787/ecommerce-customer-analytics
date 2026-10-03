"""
Campaign-risk model (replaces the leaky churn model).

    python -m src.train_model

Old label: churn = engagement_score < 30  ->  99.98% positive, and engagement was also a
feature, so the model just re-learned the rule (label leakage, "100%" accuracy).

New label: `churn` = 1 when a campaign UNDER-PERFORMS, i.e. ROI below the 25th percentile
of the TRAINING period. Features are only things known BEFORE launch, and the split is
by time (train < 2025-03-01, test >= 2025-03-01), so the score is an honest forecast.
Column names (churn, Churn_Prediction) are kept so the Power BI model keeps working.
"""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, precision_score, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

PRE_LAUNCH_CAT = ["campaign_type", "channel_used", "target_audience", "customer_segment", "language", "platform", "month"]
PRE_LAUNCH_NUM = ["duration"]
CUTOFF = pd.Timestamp("2025-03-01")


def main(root: Path = Path(".")):
    df = pd.read_csv(root / "data/processed/campaign_data_cleaned.csv", parse_dates=["date"])
    df["month"] = df["date"].dt.month.astype(str)
    train, test = df[df.date < CUTOFF], df[df.date >= CUTOFF]
    threshold = train["roi"].quantile(0.25)
    df["churn"] = (df["roi"] < threshold).astype(int)
    pre = ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore", min_frequency=50), PRE_LAUNCH_CAT),
                             ("num", StandardScaler(), PRE_LAUNCH_NUM)])
    model = Pipeline([("pre", pre), ("clf", LogisticRegression(max_iter=500, class_weight="balanced"))])
    X = PRE_LAUNCH_CAT + PRE_LAUNCH_NUM
    model.fit(train[X], df.loc[train.index, "churn"])
    p_test = model.predict_proba(test[X])[:, 1]
    y_test = df.loc[test.index, "churn"]
    p_all = model.predict_proba(df[X])[:, 1]
    cut = np.quantile(p_all, 0.75)                       # flag the riskiest 25% (matches base rate)
    df["Churn_Prediction"] = (p_all >= cut).astype(int)
    pred_test = (p_test >= cut).astype(int)
    metrics = {"label": "roi < train P25 (underperforming campaign)", "roi_threshold": round(float(threshold), 4),
               "positive_rate": round(float(df["churn"].mean()), 4), "train_rows": int(len(train)), "test_rows": int(len(test)),
               "test_auc": round(float(roc_auc_score(y_test, p_test)), 4),
               "test_precision": round(float(precision_score(y_test, pred_test)), 4),
               "test_recall": round(float(recall_score(y_test, pred_test)), 4),
               "interpretation": "AUC near 0.5 means pre-launch attributes do not predict which campaigns underperform."}
    df["frequency"] = df.groupby("customer_segment")["campaign_id"].transform("count")
    out_cols = ["campaign_id", "campaign_type", "target_audience", "duration", "channel_used", "impressions", "clicks",
                "leads", "conversions", "revenue", "acquisition_cost", "roi", "language", "engagement_score",
                "customer_segment", "date", "CTR", "Conversion_Rate", "CPL", "CPCV", "frequency", "churn", "Churn_Prediction"]
    out = df[out_cols].copy(); out["date"] = out["date"].dt.date
    out.to_csv(root / "data/processed/churn_predictions.csv", index=False)
    joblib.dump(model, root / "models/churn_model.pkl")
    (root / "reports/model").mkdir(parents=True, exist_ok=True)
    (root / "reports/model/metrics.json").write_text(json.dumps(metrics, indent=2))
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
