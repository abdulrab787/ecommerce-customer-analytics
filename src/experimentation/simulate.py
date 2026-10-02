"""
Generate SIMULATED user-level experiment data (clearly labelled) so the
decision framework can be demonstrated end-to-end. AOV (Rs.200-800) and the
customer segments are taken from the real campaign files.

    python -m src.experimentation.simulate
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

SEGMENTS = ["College Students", "Premium Shoppers", "Tier 2 City Customers", "Working Women", "Youth"]

# true effects baked into each scenario (the analyst does NOT see these)
SCENARIOS = {
    #            n/arm  cvr_lift  aov_mult  margin_pct(c,t)  refund_lift  unsub_lift  treat_share
    "EXP-001": (76000, 0.11,     1.00,     (0.30, 0.30),    0.00,        0.00,       0.50),   # clean win
    "EXP-002": (76000, 0.12,     0.98,     (0.30, 0.20),    0.05,        0.00,       0.50),   # wins CVR, loses margin
    "EXP-003": (76000, 0.15,     1.00,     (0.30, 0.30),    0.00,        0.30,       0.53),   # SRM bug + unsub spike
    "EXP-004": (76000, 0.005,    1.00,     (0.30, 0.30),    0.00,        0.00,       0.50),   # no real effect
}


def simulate(exp_id: str, platform: str, start: str, seed: int) -> pd.DataFrame:
    n_arm, lift, aov_mult, (m_c, m_t), refund_lift, unsub_lift, t_share = SCENARIOS[exp_id]
    rng = np.random.default_rng(seed)
    n = 2 * n_arm
    variant = np.where(rng.random(n) < t_share, "treatment", "control")
    is_t = variant == "treatment"
    seg = rng.choice(SEGMENTS, n)
    pre_rev = rng.gamma(1.2, 420, n) * (rng.random(n) < 0.35)            # pre-period spend (CUPED covariate)
    base_p = 0.035 * (1 + 1.5 * (pre_rev > 0) + pre_rev / 1500)                             # past buyers convert more
    base_p = base_p / base_p.mean() * 0.035
    p = base_p * np.where(is_t, 1 + lift, 1.0)
    converted = rng.random(n) < p
    aov = rng.uniform(200, 800, n) * np.where(is_t, aov_mult, 1.0) * (1 + pre_rev / 1200)
    revenue = np.where(converted, aov, 0.0).round(2)
    margin = (revenue * np.where(is_t, m_t, m_c)).round(2)
    refunded = converted & (rng.random(n) < 0.06 * np.where(is_t, 1 + refund_lift, 1.0))
    unsub = rng.random(n) < 0.004 * np.where(is_t, 1 + unsub_lift, 1.0)
    assigned = pd.Timestamp(start) + pd.to_timedelta(rng.integers(0, 28, n), unit="D")
    return pd.DataFrame({
        "experiment_id": exp_id, "user_id": [f"{exp_id[-3:]}-U{i:06d}" for i in range(n)],
        "platform": platform, "variant": variant, "customer_segment": seg,
        "assigned_date": assigned.date, "pre_period_revenue": pre_rev.round(2),
        "converted": converted.astype(int), "revenue": revenue, "gross_margin": margin,
        "refunded": refunded.astype(int), "unsubscribed": unsub.astype(int), "is_simulated": 1,
    })


def main(root: Path = Path(".")):
    import yaml
    reg = yaml.safe_load((root / "experiments/registry.yml").read_text())
    out = root / "experiments/data"
    out.mkdir(parents=True, exist_ok=True)
    for i, e in enumerate(reg["experiments"]):
        df = simulate(e["id"], e["platform"], str(e["start"]), seed=100 + i)
        df.to_csv(out / f"{e['id']}.csv", index=False)
        print(e["id"], len(df), df.groupby("variant").converted.mean().round(4).to_dict())


if __name__ == "__main__":
    main()
