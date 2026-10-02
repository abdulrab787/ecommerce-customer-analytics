# EXP-003 - WhatsApp cart-abandonment reminder (2h vs 24h)
**Decision: INVALID**  
Sample ratio mismatch (observed {'treatment': 0.5307, 'control': 0.4693}, p=3.1e-126). Assignment or logging is broken, so no metric can be trusted. Fix the bug and re-run.

> Data is SIMULATED for portfolio demonstration.

| Platform | Owner | Window | Planned n/arm | Actual n (C / T) |
|---|---|---|---|---|
| Tira | CRM | 2025-05-05 to 2025-06-01 | 70,229 (28 days) | 71,341 / 80,659 |

**Hypothesis:** Sending the WhatsApp reminder after 2h instead of 24h will recover more carts.

## 1. Validity
SRM chi-square p = 3.05e-126 -> **FAILED** - results not trustworthy (observed split {'treatment': 0.5307, 'control': 0.4693})

## 2. Metrics
| Role | Metric | Control | Treatment | Rel. lift | 95% CI | p | P(T better) | Status |
|---|---|---|---|---|---|---|---|---|
| primary | conversion_rate | 0.0345 | 0.0402 | +16.41% | +10.57% to +22.55% | 0.0000 | 100.0% | - |
| secondary | revenue_per_user | 22.2645 | 25.6036 | +15.00% | +8.52% to +21.47% | 0.0000 | 100.0% | - |
| guardrail | unsubscribe_rate | 0.0039 | 0.0054 | +38.40% | +19.10% to +60.82% | 0.0000 | 100.0% | BREACH |

CUPED (pre-period revenue) cut variance on revenue metrics by ~2%.

## 3. Business impact (annualised on eligible traffic)
- Not estimated: result is invalid or not distinguishable from zero.


## 4. Segment cuts (exploratory, Holm-adjusted)
| Segment | Lift | 95% CI | p (Holm) |
|---|---|---|---|
| College Students | +21.23% | +7.88% to +36.23% | 0.005 |
| Premium Shoppers | +7.56% | -3.99% to +20.49% | 0.209 |
| Tier 2 City Customers | +20.76% | +7.50% to +35.65% | 0.005 |
| Working Women | +11.01% | -0.96% to +24.43% | 0.145 |
| Youth | +22.73% | +9.42% to +37.66% | 0.002 |

Segment results are for generating the next hypothesis only - the decision uses the pre-registered primary metric and guardrails.