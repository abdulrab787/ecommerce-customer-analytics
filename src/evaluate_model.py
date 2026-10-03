"""
Evaluate the saved campaign-risk model on the time-based hold-out.

    python -m src.train_model      # trains, writes models/churn_model.pkl + reports/model/metrics.json
    python -m src.evaluate_model   # writes reports/model/evaluation.json, confusion_matrix.csv, coefficients.csv

Uses exactly the same label, split and decision cut-off as src.train_model, so the
numbers here are consistent with metrics.json. Adds: F1, confusion matrix, PR-AUC,
a base-rate comparison and the logistic-regression coefficients.
"""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (average_precision_score, confusion_matrix, f1_score,
                             precision_score, recall_score, roc_auc_score)

from src.feature_engineering import add_time_features
from src.train_model import CUTOFF, PRE_LAUNCH_CAT, PRE_LAUNCH_NUM


def evaluate(root: Path = Path(".")) -> dict:
    df = pd.read_csv(root / "data/processed/campaign_data_cleaned.csv", parse_dates=["date"])
    df = add_time_features(df)
    train_mask = df["date"] < CUTOFF
    threshold = df.loc[train_mask, "roi"].quantile(0.25)
    y = (df["roi"] < threshold).astype(int)
    X = PRE_LAUNCH_CAT + PRE_LAUNCH_NUM

    model = joblib.load(root / "models/churn_model.pkl")
    p_all = model.predict_proba(df[X])[:, 1]
    cut = np.quantile(p_all, 0.75)                  # same rule as train_model: flag riskiest 25%
    test = ~train_mask
    y_test, p_test = y[test], p_all[test]
    pred = (p_test >= cut).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_test, pred, labels=[0, 1]).ravel()

    res = {
        "model": "LogisticRegression(class_weight='balanced') on pre-launch attributes",
        "label": "roi < train-period P25 (underperforming campaign)",
        "split": f"time-based: train date < {CUTOFF.date()}, test date >= {CUTOFF.date()}",
        "train_rows": int(train_mask.sum()), "test_rows": int(test.sum()),
        "test_positive_rate": round(float(y_test.mean()), 4),
        "roc_auc": round(float(roc_auc_score(y_test, p_test)), 4),
        "pr_auc": round(float(average_precision_score(y_test, p_test)), 4),
        "pr_auc_random_baseline": round(float(y_test.mean()), 4),
        "precision": round(float(precision_score(y_test, pred)), 4),
        "recall": round(float(recall_score(y_test, pred)), 4),
        "f1": round(float(f1_score(y_test, pred)), 4),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        "interpretation": ("ROC-AUC ~0.50 and precision ~= the positive rate: pre-launch campaign "
                           "attributes carry no usable signal for predicting under-performance."),
    }

    pre, clf = model.named_steps["pre"], model.named_steps["clf"]
    coefs = pd.DataFrame({"feature": pre.get_feature_names_out(), "coefficient": clf.coef_[0]})
    coefs["abs_coefficient"] = coefs["coefficient"].abs()
    coefs = coefs.sort_values("abs_coefficient", ascending=False)

    out = root / "reports/model"
    out.mkdir(parents=True, exist_ok=True)
    (out / "evaluation.json").write_text(json.dumps(res, indent=2))
    pd.DataFrame([[tn, fp], [fn, tp]], index=["actual_0", "actual_1"],
                 columns=["pred_0", "pred_1"]).to_csv(out / "confusion_matrix.csv")
    coefs.to_csv(out / "coefficients.csv", index=False)
    return res


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2))
