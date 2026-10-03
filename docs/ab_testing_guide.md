# A/B Testing Guide

A practical workflow for running and reading a controlled experiment, with the pitfalls that most often produce
wrong decisions.

> **Scope in this repository.** The campaign data is **observational**: nobody randomly assigned which campaigns ran,
> so it cannot answer causal questions. Every experiment here uses **clearly labelled synthetic data**:
> * `notebooks/05_ab_testing_experimentation.ipynb` walks through one test end to end.
> * `src/experimentation/` + `experiments/registry.yml` apply a pre-registered decision rule to four simulated tests
>   (`reports/experiments/`, Power BI *Experiment Decisions* page).

## Workflow

```
Business Question → Hypothesis → Metric Definition → Experiment Design → Sample Size → Randomisation
→ Data Validation → Statistical Test → Confidence Interval → Segment Analysis → Decision
```

| Step | What to do | In this repo |
|---|---|---|
| **1. Business question** | State the decision the test will inform ("ship the cart widget or not?"). | notebook 05 §1; `registry.yml` `hypothesis` |
| **2. Hypothesis** | H0: no difference. H1: a difference (two-sided unless harm is impossible). Say *why* the change should work. | notebook 05 §1 |
| **3. Metric definition** | One **primary** metric that decides the test; **secondary** metrics to explain it; **guardrails** that must not get worse (margin, refunds, unsubscribes, latency). Fix the unit (user, session, order) and match it to the randomisation unit. | `registry.yml` `primary_metric`, `secondary_metrics`, `guardrails` |
| **4. Experiment design** | Control vs treatment, split (usually 50/50), eligible population, start/end dates. | notebook 05 §3 |
| **5. Sample size** | From baseline rate, **minimum detectable effect (MDE)**, α (usually 0.05) and power (usually 0.80). The MDE is a business choice: the smallest lift worth shipping. Round duration up to whole weeks. | `stats.sample_size_proportion`, `stats.duration_days`; e.g. 3.5% baseline, +8% MDE → 70,229 users per arm |
| **6. Randomisation** | Random, persistent assignment per unit (hash of user ID). Log the assignment, not just the exposure. | simulated |
| **7. Data validation** | **Before reading results:** sample ratio mismatch (SRM) test, each unit in one arm only, no duplicates, logging complete in both arms. | `stats.srm_check` (p < 0.001 ⇒ INVALID) |
| **8. Statistical test** | Proportions: two-proportion z-test. Means: Welch t-test. Optional: CUPED variance reduction, Bayesian P(better). | `stats.proportion_test`, `mean_test`, `cuped`, `bayes_proportion` |
| **9. Confidence interval** | Report absolute and relative lift with a 95% CI. Compare the CI with zero (statistical) **and** with the MDE (practical). | `MetricResult.ci_low/ci_high` |
| **10. Segment analysis** | Exploratory only; correct for multiple comparisons (Holm). Never override the primary result with a segment. | `stats.holm`, `decide.segment_cuts` |
| **11. Decision** | Apply the rule written before launch: SRM → guardrails → significance → MDE. | `decide.decide()` → SHIP / SHIP WITH MONITORING / DO NOT SHIP / KEEP RUNNING / INVALID |

## Statistical vs business significance

* **Statistically significant:** the CI excludes zero (p < α). The effect is probably not zero.
* **Business significant:** the effect is large enough to pay for itself. Check the CI against the MDE and convert it to money.

With very large samples, a +0.5% lift can be "significant" and still not worth shipping. The campaign data shows the
same trap in observational form: platform conversion rates of 22.03% vs 21.94% differ with a tiny p-value only because
the click counts run into the hundreds of millions.

## Why observational analysis is not causal

Comparing campaigns that happened to use different channels or types mixes the effect of the choice with everything
correlated with it: budget, season, brand, audience. Randomisation balances all of these, including the ones you
cannot measure. Observational patterns are useful for *generating* hypotheses; a controlled test confirms them.

## Common pitfalls

| Pitfall | What goes wrong | Guard |
|---|---|---|
| **Peeking** | Checking daily and stopping at the first p < 0.05. In notebook 05, 2,000 A/A tests with 10 looks give a **21.4%** false-positive rate instead of 5%. | Fix the sample size and analyse once, or use sequential methods (alpha spending, always-valid p-values). |
| **Under-powered tests** | Real effects are usually missed, and the ones that reach significance are exaggerated ("winner's curse"). | Compute sample size up front; report the achievable MDE. |
| **Sample ratio mismatch** | A 50/50 test comes out 53/47 because of a redirect, bot filter or logging bug. The groups are no longer comparable. | SRM chi-square test before reading any metric; if it fails, the test is INVALID (EXP-003). |
| **Multiple testing** | 10 metrics or segments at α = 0.05 give about a 40% chance of at least one false win. | One primary metric; Holm / Bonferroni for the rest; label segment cuts exploratory. |
| **Novelty / primacy effects** | Users react to change itself; the lift fades (or a dip recovers) after a few weeks. | Run whole weeks; compare early vs late periods; hold out a long-term control for big changes. |
| **Selection bias** | Analysing only users who saw or clicked the feature, or letting users opt in. | Analyse everyone assigned (intention to treat); randomise before exposure. |
| **Simpson's paradox** | Treatment wins inside every segment but loses overall (or the reverse) because segment mix differs between arms or over time. | Check arm balance by segment; keep traffic allocation constant during the test. |
| **Metric definition problems** | Ratio metrics with the wrong denominator (per session vs per user); metric changed mid-test; revenue skewed by a few large orders. | Define metrics in the pre-registration; match denominator to randomisation unit; cap or log-transform heavy tails; use the delta method for ratio metrics. |
| **Guardrail blind spots** | Conversion improves but margin or refunds get worse (EXP-002: CVR +10.6%, margin per user −28%). | Pre-register guardrails with thresholds; a breach blocks shipping. |
| **Interference** | Treated users affect control users (shared inventory, referrals, marketplace prices). | Cluster or geo randomisation; switchback designs. |

## Checklist before shipping

- [ ] Hypothesis, primary metric, MDE, α, power and guardrails were written down before launch
- [ ] Planned sample size reached; no early stop
- [ ] SRM test passed (p ≥ 0.001)
- [ ] Primary metric CI excludes zero **and** the effect is worth it against the MDE
- [ ] No guardrail breached
- [ ] Segment findings labelled exploratory and multiplicity-adjusted
- [ ] Decision memo written (see `reports/experiments/EXP-00x_decision.md`)
