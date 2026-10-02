# EXP-002 - Influencer code 20% off vs 10% off
**Decision: DO NOT SHIP**  
Guardrail breached: gross_margin_per_user. A primary-metric win does not justify the damage.

> Data is SIMULATED for portfolio demonstration.

| Platform | Owner | Window | Planned n/arm | Actual n (C / T) |
|---|---|---|---|---|
| Purplle | Influencer Marketing | 2025-04-07 to 2025-05-04 | 70,229 (28 days) | 76,266 / 75,734 |

**Hypothesis:** Doubling the influencer discount from 10% to 20% will lift conversion enough to grow gross margin per user.

## 1. Validity
SRM chi-square p = 1.72e-01 -> passed (observed split {'control': 0.5018, 'treatment': 0.4983})

## 2. Metrics
| Role | Metric | Control | Treatment | Rel. lift | 95% CI | p | P(T better) | Status |
|---|---|---|---|---|---|---|---|---|
| primary | conversion_rate | 0.0358 | 0.0396 | +10.59% | +5.10% to +16.36% | 0.0001 | 100.0% | - |
| secondary | revenue_per_user | 22.6989 | 24.5220 | +8.03% | +2.00% to +14.06% | 0.0066 | 99.7% | - |
| guardrail | gross_margin_per_user | 6.8079 | 4.9028 | -27.98% | -32.00% to -23.96% | 0.0000 | 0.0% | BREACH |
| guardrail | refund_rate | 0.0645 | 0.0580 | -9.97% | -26.51% to +10.29% | 0.3102 | 15.4% | AT RISK |

CUPED (pre-period revenue) cut variance on revenue metrics by ~2%.

## 3. Business impact (annualised on eligible traffic)
- Revenue: Rs.3,992,588
- Gross margin: Rs.-4,172,233

## 4. Segment cuts (exploratory, Holm-adjusted)
| Segment | Lift | 95% CI | p (Holm) |
|---|---|---|---|
| College Students | +10.00% | -1.73% to +23.13% | 0.292 |
| Premium Shoppers | +6.80% | -4.73% to +19.72% | 0.518 |
| Tier 2 City Customers | +6.18% | -5.35% to +19.12% | 0.518 |
| Working Women | +16.74% | +4.35% to +30.60% | 0.034 |
| Youth | +13.44% | +1.15% to +27.23% | 0.124 |

Segment results are for generating the next hypothesis only - the decision uses the pre-registered primary metric and guardrails.