"""
A/B testing statistics: design (power / MDE / duration), validity (SRM),
frequentist + Bayesian readouts, CUPED variance reduction, multiple-testing control.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
import math

import numpy as np
from scipy import stats


# --------------------------------------------------------------------------- #
# DESIGN — decide sample size BEFORE launch
# --------------------------------------------------------------------------- #
def sample_size_proportion(p_baseline: float, mde_rel: float, alpha: float = 0.05,
                           power: float = 0.8, two_sided: bool = True) -> int:
    """Users per arm to detect a relative lift `mde_rel` on a conversion rate."""
    p1, p2 = p_baseline, p_baseline * (1 + mde_rel)
    za = stats.norm.ppf(1 - alpha / (2 if two_sided else 1))
    zb = stats.norm.ppf(power)
    pbar = (p1 + p2) / 2
    n = (za * math.sqrt(2 * pbar * (1 - pbar)) + zb * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2 / (p2 - p1) ** 2
    return int(math.ceil(n))


def sample_size_mean(sd: float, mde_abs: float, alpha: float = 0.05, power: float = 0.8) -> int:
    za, zb = stats.norm.ppf(1 - alpha / 2), stats.norm.ppf(power)
    return int(math.ceil(2 * ((za + zb) * sd / mde_abs) ** 2))


def mde_for_sample(p_baseline: float, n_per_arm: int, alpha: float = 0.05, power: float = 0.8) -> float:
    """Smallest relative lift detectable with the traffic you actually have."""
    za, zb = stats.norm.ppf(1 - alpha / 2), stats.norm.ppf(power)
    se = math.sqrt(2 * p_baseline * (1 - p_baseline) / n_per_arm)
    return (za + zb) * se / p_baseline


def duration_days(n_per_arm: int, arms: int, daily_eligible_users: int, allocation: float = 1.0) -> int:
    """Round up to whole weeks so every weekday is represented equally."""
    days = math.ceil(n_per_arm * arms / (daily_eligible_users * allocation))
    return max(7, int(math.ceil(days / 7) * 7))


# --------------------------------------------------------------------------- #
# VALIDITY — Sample Ratio Mismatch
# --------------------------------------------------------------------------- #
def srm_check(observed: dict[str, int], expected_split: dict[str, float], threshold: float = 0.001) -> dict:
    keys = list(observed)
    obs = np.array([observed[k] for k in keys], dtype=float)
    exp = np.array([expected_split[k] for k in keys]) * obs.sum()
    chi2, p = stats.chisquare(obs, exp)
    return {"chi2": float(chi2), "p_value": float(p), "srm_detected": bool(p < threshold),
            "observed_split": {k: round(float(v / obs.sum()), 4) for k, v in zip(keys, obs)}}


# --------------------------------------------------------------------------- #
# FREQUENTIST READOUT
# --------------------------------------------------------------------------- #
@dataclass
class MetricResult:
    metric: str
    metric_type: str
    control: float
    treatment: float
    abs_diff: float
    rel_lift: float
    ci_low: float           # CI on relative lift
    ci_high: float
    p_value: float
    n_control: int
    n_treatment: int
    prob_treatment_better: float | None = None
    expected_loss: float | None = None   # relative, if you ship and you are wrong

    def as_dict(self):
        return asdict(self)


def proportion_test(x_c: int, n_c: int, x_t: int, n_t: int, metric: str = "conversion_rate",
                    alpha: float = 0.05) -> MetricResult:
    pc, pt = x_c / n_c, x_t / n_t
    se_pool = math.sqrt((x_c + x_t) / (n_c + n_t) * (1 - (x_c + x_t) / (n_c + n_t)) * (1 / n_c + 1 / n_t))
    z = (pt - pc) / se_pool if se_pool else 0.0
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    # CI for relative lift via delta method on log ratio
    se_log = math.sqrt((1 - pc) / (pc * n_c) + (1 - pt) / (pt * n_t))
    zc = stats.norm.ppf(1 - alpha / 2)
    lr = math.log(pt / pc)
    return MetricResult(metric, "proportion", pc, pt, pt - pc, pt / pc - 1,
                        math.exp(lr - zc * se_log) - 1, math.exp(lr + zc * se_log) - 1,
                        float(p), n_c, n_t)


def mean_test(c: np.ndarray, t: np.ndarray, metric: str = "revenue_per_user", alpha: float = 0.05) -> MetricResult:
    """Welch t-test; CI on relative lift by delta method (ratio of means)."""
    mc, mt = c.mean(), t.mean()
    vc, vt = c.var(ddof=1) / len(c), t.var(ddof=1) / len(t)
    tstat, p = stats.ttest_ind(t, c, equal_var=False)
    se_rel = math.sqrt(vt / mc ** 2 + (mt ** 2) * vc / mc ** 4)
    zc = stats.norm.ppf(1 - alpha / 2)
    rel = mt / mc - 1
    return MetricResult(metric, "mean", float(mc), float(mt), float(mt - mc), float(rel),
                        float(rel - zc * se_rel), float(rel + zc * se_rel), float(p), len(c), len(t))


def cuped(y: np.ndarray, x: np.ndarray) -> np.ndarray:
    """CUPED: remove variance explained by a pre-experiment covariate x.
    Keeps the mean, shrinks the variance -> narrower CIs / shorter tests."""
    theta = np.cov(y, x, ddof=1)[0, 1] / np.var(x, ddof=1)
    return y - theta * (x - x.mean())


# --------------------------------------------------------------------------- #
# BAYESIAN READOUT
# --------------------------------------------------------------------------- #
def bayes_proportion(x_c: int, n_c: int, x_t: int, n_t: int, draws: int = 200_000,
                     prior=(1, 1), seed: int = 7) -> dict:
    rng = np.random.default_rng(seed)
    a, b = prior
    pc = rng.beta(a + x_c, b + n_c - x_c, draws)
    pt = rng.beta(a + x_t, b + n_t - x_t, draws)
    lift = pt / pc - 1
    return {"prob_treatment_better": float((pt > pc).mean()),
            "expected_loss_rel": float(np.maximum(-lift, 0).mean()),   # cost of shipping if wrong
            "lift_cri_low": float(np.quantile(lift, 0.025)),
            "lift_cri_high": float(np.quantile(lift, 0.975))}


def bayes_mean(c: np.ndarray, t: np.ndarray, draws: int = 200_000, seed: int = 7) -> dict:
    """Normal approximation to posterior of each mean (fine at e-commerce sample sizes)."""
    rng = np.random.default_rng(seed)
    mc = rng.normal(c.mean(), c.std(ddof=1) / math.sqrt(len(c)), draws)
    mt = rng.normal(t.mean(), t.std(ddof=1) / math.sqrt(len(t)), draws)
    lift = mt / mc - 1
    return {"prob_treatment_better": float((mt > mc).mean()),
            "expected_loss_rel": float(np.maximum(-lift, 0).mean()),
            "lift_cri_low": float(np.quantile(lift, 0.025)),
            "lift_cri_high": float(np.quantile(lift, 0.975))}


# --------------------------------------------------------------------------- #
# MULTIPLE TESTING — for segment cuts
# --------------------------------------------------------------------------- #
def holm(pvals: list[float]) -> list[float]:
    m = len(pvals)
    order = np.argsort(pvals)
    adj = np.empty(m)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * pvals[i]))
        adj[i] = running
    return adj.tolist()
