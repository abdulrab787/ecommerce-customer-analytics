# EXP-004 - Email subject line with first name
**Decision: DO NOT SHIP**  
No meaningful effect: CI -7.4% to +2.9% rules out the 8% MDE. Stop and test a bolder idea.

> Data is SIMULATED for portfolio demonstration.

| Platform | Owner | Window | Planned n/arm | Actual n (C / T) |
|---|---|---|---|---|
| Nykaa | CRM | 2025-06-02 to 2025-06-29 | 70,229 (28 days) | 75,983 / 76,017 |

**Hypothesis:** Personalising the subject line with the customer's first name will lift conversion.

## 1. Validity
SRM chi-square p = 9.31e-01 -> passed (observed split {'treatment': 0.5001, 'control': 0.4999})

## 2. Metrics
| Role | Metric | Control | Treatment | Rel. lift | 95% CI | p | P(T better) | Status |
|---|---|---|---|---|---|---|---|---|
| primary | conversion_rate | 0.0356 | 0.0347 | -2.41% | -7.42% to +2.87% | 0.3637 | 18.0% | - |
| secondary | revenue_per_user | 22.8330 | 22.1003 | -3.21% | -8.83% to +2.41% | 0.2705 | 13.5% | - |
| guardrail | unsubscribe_rate | 0.0039 | 0.0036 | -8.15% | -22.07% to +8.25% | 0.3105 | 15.5% | OK |

CUPED (pre-period revenue) cut variance on revenue metrics by ~2%.

## 3. Business impact (annualised on eligible traffic)
- Not estimated: result is invalid or not distinguishable from zero.


## 4. Segment cuts (exploratory, Holm-adjusted)
| Segment | Lift | 95% CI | p (Holm) |
|---|---|---|---|
| College Students | -13.63% | -23.48% to -2.51% | 0.088 |
| Premium Shoppers | -0.08% | -11.11% to +12.32% | 1.000 |
| Tier 2 City Customers | +7.67% | -4.07% to +20.84% | 0.837 |
| Working Women | -3.76% | -14.48% to +8.30% | 1.000 |
| Youth | -1.99% | -12.92% to +10.30% | 1.000 |

Segment results are for generating the next hypothesis only - the decision uses the pre-registered primary metric and guardrails.