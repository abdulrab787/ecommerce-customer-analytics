import pandas as pd

from src.data_quality import checks as C
from src.data_quality.kpis import compute_kpis


def test_duplicate_key_detected():
    df = pd.DataFrame({"id": [1, 1, 2]})
    assert not C.duplicate_records(df, "t", key=["id"]).passed


def test_referential_integrity_orphans():
    child = pd.DataFrame({"k": ["a", "b", "z"]})
    parent = pd.DataFrame({"k": ["a", "b"]})
    r = C.referential_integrity(child, parent, "c", "p", "k", "k")
    assert not r.passed and r.failing_rows == 1


def test_row_multiplication_from_duplicate_dim_key():
    fact = pd.DataFrame({"seg": ["A", "B"], "rev": [10, 20]})
    dim = pd.DataFrame({"seg": ["A", "A", "B"]})          # duplicate key -> fan-out
    r = C.row_multiplication(fact, dim, "fact", "dim", "seg", "seg")
    assert not r.passed and r.observed == 1.5


def test_funnel_rule():
    df = pd.DataFrame({"clicks": [5, 50], "impressions": [10, 10]})
    assert C.business_rule(df, "t", "funnel", "clicks <= impressions").failing_rows == 1


def test_spend_is_cost_times_conversions():
    df = pd.DataFrame({"revenue": [300.0], "acquisition_cost": [10.0], "conversions": [10],
                       "impressions": [1000], "clicks": [100], "leads": [50]})
    k = compute_kpis(df)
    assert k["total_spend"] == 100 and k["roi"] == 2.0


def test_source_to_report_flags_wrong_roi():
    res = C.source_to_report({"roi": 1.94}, {"roi": 1365.4})
    assert not res[0].passed
