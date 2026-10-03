"""
Experiment readout + decision engine.

    python -m src.experimentation.decide

For each pre-registered experiment in experiments/registry.yml:
  1. Validity   : sample-ratio-mismatch test, sample size vs. plan
  2. Primary    : frequentist (z-test, CI on lift) + Bayesian (P(better), expected loss)
  3. Secondary  : revenue per user (Welch + CUPED)
  4. Guardrails : margin / refunds / unsubscribes must not degrade beyond tolerance
  5. Segments   : exploratory only, Holm-adjusted (never used to ship)
  6. Decision   : deterministic rule -> SHIP / SHIP WITH MONITORING / DO NOT SHIP /
                  KEEP RUNNING / INVALID, plus a decision memo per experiment.

Outputs (reports/experiments/) are shaped for a Power BI "Experiment Decisions" page.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from . import stats as S

METRIC_COLUMN = {
    "conversion_rate": "converted",
    "revenue_per_user": "revenue",
    "gross_margin_per_user": "gross_margin",
    "refund_rate": "refunded",
    "unsubscribe_rate": "unsubscribed",
}


def _arms(df):
    return df[df.variant == "control"], df[df.variant == "treatment"]


def evaluate_metric(df: pd.DataFrame, name: str, mtype: str, use_cuped: bool = True) -> tuple[S.MetricResult, dict]:
    c, t = _arms(df)
    col = METRIC_COLUMN[name]
    if name == "refund_rate":                      # refund rate is per converting user
        c, t = c[c.converted == 1], t[t.converted == 1]
    extra = {}
    if mtype == "proportion":
        r = S.proportion_test(int(c[col].sum()), len(c), int(t[col].sum()), len(t), metric=name)
        b = S.bayes_proportion(int(c[col].sum()), len(c), int(t[col].sum()), len(t))
    else:
        yc, yt = c[col].to_numpy(float), t[col].to_numpy(float)
        if use_cuped and "pre_period_revenue" in df:
            allx = df["pre_period_revenue"].to_numpy(float)
            ally = df[col].to_numpy(float)
            adj = pd.Series(S.cuped(ally, allx), index=df.index)
            var_before = np.var(ally)
            yc, yt = adj.loc[c.index].to_numpy(), adj.loc[t.index].to_numpy()
            extra["cuped_variance_reduction"] = round(1 - np.var(adj) / var_before, 4)
        r = S.mean_test(yc, yt, metric=name)
        b = S.bayes_mean(yc, yt)
    r.prob_treatment_better = b["prob_treatment_better"]
    r.expected_loss = b["expected_loss_rel"]
    return r, extra


def guardrail_status(r: S.MetricResult, g: dict, alpha: float) -> str:
    if "max_rel_drop" in g:          # bad if it goes DOWN
        tol, harm, worst = g["max_rel_drop"], -r.rel_lift, -r.ci_low
    else:                            # bad if it goes UP
        tol, harm, worst = g["max_rel_increase"], r.rel_lift, r.ci_high
    if harm > tol and r.p_value < alpha:
        return "BREACH"
    if worst > tol:
        return "AT RISK"
    return "OK"


def decide(exp: dict, d: dict, df: pd.DataFrame) -> dict:
    alpha = exp.get("alpha", d["alpha"])
    pm = exp["primary_metric"]
    n_plan = S.sample_size_proportion(pm["baseline"], pm["mde_rel"], alpha, d["power"])
    plan_days = S.duration_days(n_plan, 2, exp["daily_eligible_users"])
    counts = df.variant.value_counts().to_dict()
    srm = S.srm_check(counts, d["split"], d["srm_threshold"])

    rows, notes = [], []
    prim, _ = evaluate_metric(df, pm["name"], pm["type"])
    rows.append({**prim.as_dict(), "role": "primary", "status": ""})
    for m in exp.get("secondary_metrics", []):
        r, extra = evaluate_metric(df, m["name"], m["type"])
        rows.append({**r.as_dict(), "role": "secondary", "status": "", **extra})
    g_status = {}
    for g in exp.get("guardrails", []):
        r, extra = evaluate_metric(df, g["name"], g["type"])
        st = guardrail_status(r, g, alpha)
        g_status[g["name"]] = st
        rows.append({**r.as_dict(), "role": "guardrail", "status": st, **extra})

    n_min = min(counts.values())
    # ---------------- decision rule (order matters) ----------------
    if srm["srm_detected"]:
        decision = "INVALID"
        reason = (f"Sample ratio mismatch (observed {srm['observed_split']}, p={srm['p_value']:.1e}). "
                  "Assignment or logging is broken, so no metric can be trusted. Fix the bug and re-run.")
    elif "BREACH" in g_status.values():
        bad = [k for k, v in g_status.items() if v == "BREACH"]
        decision = "DO NOT SHIP"
        reason = f"Guardrail breached: {', '.join(bad)}. A primary-metric win does not justify the damage."
    elif n_min < n_plan:
        decision = "KEEP RUNNING"
        reason = f"Only {n_min:,} users/arm vs {n_plan:,} planned. Do not read early (peeking inflates false positives)."
    elif prim.p_value < alpha and prim.rel_lift > 0 and prim.prob_treatment_better >= d["ship_prob_threshold"] \
            and prim.expected_loss <= d["max_expected_loss"]:
        risky = [k for k, v in g_status.items() if v == "AT RISK"]
        decision = "SHIP WITH MONITORING" if risky else "SHIP"
        reason = (f"{pm['name']} +{prim.rel_lift:.1%} (95% CI {prim.ci_low:+.1%} to {prim.ci_high:+.1%}), "
                  f"P(better)={prim.prob_treatment_better:.1%}, expected loss {prim.expected_loss:.2%}. "
                  + (f"Guardrails at risk: {', '.join(risky)} - monitor post-launch." if risky else "All guardrails OK."))
    elif prim.p_value < alpha and prim.rel_lift < 0:
        decision = "DO NOT SHIP"
        reason = f"Treatment is significantly worse on {pm['name']} ({prim.rel_lift:+.1%})."
    elif prim.ci_high < pm["mde_rel"]:
        decision = "DO NOT SHIP"
        reason = (f"No meaningful effect: CI {prim.ci_low:+.1%} to {prim.ci_high:+.1%} rules out the "
                  f"{pm['mde_rel']:.0%} MDE. Stop and test a bolder idea.")
    else:
        decision = "INCONCLUSIVE"
        reason = "Effect could still be >= MDE but is not significant. Iterate on the treatment or extend with a new power calc."

    # business impact (annualised, on eligible traffic) - only meaningful for shipped tests
    rpu = next((r for r in rows if r["metric"] == "revenue_per_user"), None)
    gm = next((r for r in rows if r["metric"] == "gross_margin_per_user"), None)
    yearly_users = exp["daily_eligible_users"] * 365
    impact_rev = rpu["abs_diff"] * yearly_users if rpu else np.nan
    impact_gm = gm["abs_diff"] * yearly_users if gm else np.nan
    # never put a Rs. figure on an invalid or null result - it is noise
    if decision == "INVALID" or reason.startswith("No meaningful") or decision == "INCONCLUSIVE":
        impact_rev = impact_gm = np.nan

    summary = {
        "experiment_id": exp["id"], "name": exp["name"], "platform": exp["platform"], "owner": exp["owner"],
        "start": str(exp["start"]), "end": str(exp["end"]), "primary_metric": pm["name"],
        "planned_n_per_arm": n_plan, "planned_days": plan_days, "actual_n_control": counts.get("control", 0),
        "actual_n_treatment": counts.get("treatment", 0), "srm_p_value": srm["p_value"],
        "srm_detected": srm["srm_detected"], "primary_lift": prim.rel_lift, "primary_ci_low": prim.ci_low,
        "primary_ci_high": prim.ci_high, "primary_p_value": prim.p_value,
        "prob_treatment_better": prim.prob_treatment_better, "expected_loss": prim.expected_loss,
        "guardrails": "; ".join(f"{k}={v}" for k, v in g_status.items()),
        "annual_revenue_impact": impact_rev, "annual_margin_impact": impact_gm,
        "decision": decision, "reason": reason, "is_simulated": int(df.get("is_simulated", pd.Series([0])).max()),
    }
    metrics = pd.DataFrame(rows).assign(experiment_id=exp["id"])
    return summary, metrics, srm


def segment_cuts(exp_id: str, df: pd.DataFrame) -> pd.DataFrame:
    out = []
    for seg, g in df.groupby("customer_segment"):
        c, t = _arms(g)
        r = S.proportion_test(int(c.converted.sum()), len(c), int(t.converted.sum()), len(t))
        out.append({"experiment_id": exp_id, "customer_segment": seg, "rel_lift": r.rel_lift,
                    "ci_low": r.ci_low, "ci_high": r.ci_high, "p_value": r.p_value})
    out = pd.DataFrame(out)
    out["p_holm"] = S.holm(out.p_value.tolist())
    out["significant_after_holm"] = out.p_holm < 0.05
    out["note"] = "exploratory - not a shipping criterion"
    return out


def memo(s: dict, m: pd.DataFrame, srm: dict, seg: pd.DataFrame, exp: dict) -> str:
    def pct(x): return f"{x:+.2%}"
    L = [f"# {s['experiment_id']} - {s['name']}",
         f"**Decision: {s['decision']}**  \n{s['reason']}\n",
         "> Data is SIMULATED for portfolio demonstration.\n" if s["is_simulated"] else "",
         f"| Platform | Owner | Window | Planned n/arm | Actual n (C / T) |", "|---|---|---|---|---|",
         f"| {s['platform']} | {s['owner']} | {s['start']} to {s['end']} | {s['planned_n_per_arm']:,} "
         f"({s['planned_days']} days) | {s['actual_n_control']:,} / {s['actual_n_treatment']:,} |\n",
         f"**Hypothesis:** {exp['hypothesis'].strip()}\n",
         f"## 1. Validity\nSRM chi-square p = {srm['p_value']:.2e} -> "
         f"{'**FAILED** - results not trustworthy' if srm['srm_detected'] else 'passed'} "
         f"(observed split {srm['observed_split']})\n",
         "## 2. Metrics", "| Role | Metric | Control | Treatment | Rel. lift | 95% CI | p | P(T better) | Status |",
         "|---|---|---|---|---|---|---|---|---|"]
    for _, r in m.iterrows():
        L.append(f"| {r.role} | {r.metric} | {r.control:.4f} | {r.treatment:.4f} | {pct(r.rel_lift)} | "
                 f"{pct(r.ci_low)} to {pct(r.ci_high)} | {r.p_value:.4f} | {r.prob_treatment_better:.1%} | {r.status or '-'} |")
    if "cuped_variance_reduction" in m and m.cuped_variance_reduction.notna().any():
        L.append(f"\nCUPED (pre-period revenue) cut variance on revenue metrics by "
                 f"~{m.cuped_variance_reduction.dropna().mean():.0%}.")
    L += ["\n## 3. Business impact (annualised on eligible traffic)",
          (f"- Revenue: Rs.{s['annual_revenue_impact']:,.0f}" if pd.notna(s["annual_revenue_impact"])
           else "- Not estimated: result is invalid or not distinguishable from zero."),
          f"- Gross margin: Rs.{s['annual_margin_impact']:,.0f}" if pd.notna(s["annual_margin_impact"]) else "",
          "\n## 4. Segment cuts (exploratory, Holm-adjusted)",
          "| Segment | Lift | 95% CI | p (Holm) |", "|---|---|---|---|"]
    for _, r in seg.iterrows():
        L.append(f"| {r.customer_segment} | {pct(r.rel_lift)} | {pct(r.ci_low)} to {pct(r.ci_high)} | {r.p_holm:.3f} |")
    L.append("\nSegment results are for generating the next hypothesis only - the decision uses the pre-registered primary metric and guardrails.")
    return "\n".join(x for x in L if x is not None)


def main(root: Path = Path(".")):
    reg = yaml.safe_load((root / "experiments/registry.yml").read_text())
    out = root / "reports/experiments"
    out.mkdir(parents=True, exist_ok=True)
    summaries, metrics, segs = [], [], []
    for exp in reg["experiments"]:
        df = pd.read_csv(root / f"experiments/data/{exp['id']}.csv")
        s, m, srm = decide(exp, reg["defaults"], df)
        sg = segment_cuts(exp["id"], df)
        (out / f"{exp['id']}_decision.md").write_text(memo(s, m, srm, sg, exp), encoding="utf-8")
        summaries.append(s); metrics.append(m); segs.append(sg)
        print(f"{exp['id']}: {s['decision']:<22} {s['reason'][:110]}")
    pd.DataFrame(summaries).to_csv(out / "experiment_decisions.csv", index=False)
    pd.concat(metrics).to_csv(out / "experiment_metrics.csv", index=False)
    pd.concat(segs).to_csv(out / "experiment_segments.csv", index=False)


if __name__ == "__main__":
    main()
