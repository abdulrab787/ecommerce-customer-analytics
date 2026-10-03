import numpy as np

from src.experimentation import stats as S


def test_sample_size_reasonable():
    n = S.sample_size_proportion(0.035, 0.08)
    assert 65_000 < n < 75_000


def test_srm_detects_skew():
    assert S.srm_check({"control": 4700, "treatment": 5300}, {"control": .5, "treatment": .5})["srm_detected"]
    assert not S.srm_check({"control": 5010, "treatment": 4990}, {"control": .5, "treatment": .5})["srm_detected"]


def test_proportion_test_ci_contains_true_lift():
    r = S.proportion_test(3500, 100_000, 3850, 100_000)
    assert r.ci_low < 0.10 < r.ci_high and r.p_value < 0.05


def test_bayes_prob_better():
    b = S.bayes_proportion(3500, 100_000, 3850, 100_000)
    assert b["prob_treatment_better"] > 0.99


def test_cuped_keeps_mean_reduces_variance():
    rng = np.random.default_rng(0)
    x = rng.normal(100, 20, 10_000)
    y = x * 0.8 + rng.normal(0, 10, 10_000)
    adj = S.cuped(y, x)
    assert abs(adj.mean() - y.mean()) < 1e-9 and adj.var() < y.var() * 0.5


def test_holm_adjustment():
    assert np.allclose(S.holm([0.01, 0.04, 0.03]), [0.03, 0.06, 0.06])
